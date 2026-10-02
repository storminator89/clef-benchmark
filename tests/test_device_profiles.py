"""Model-free mocks prove routing/guards, not execution on AMD hardware."""
from contextlib import nullcontext
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime.check_backend import check
from runtime.device_profiles import BackendUnavailable, dtype_for_profile, resolve_profile, validate_profile
from runtime.live_adapter import ClefRuntime
from server import Workbench


def fake_torch(hip='10.0.0', available=True, free_gib=40, bf16=True):
    cuda = MagicMock()
    cuda.is_available.return_value = available
    cuda.device_count.return_value = 2
    cuda.is_bf16_supported.return_value = bf16
    cuda.get_device_properties.return_value = SimpleNamespace(name='Mock Radeon', gcnArchName='gfx1151')
    cuda.mem_get_info.return_value = (free_gib * 1024**3, 48 * 1024**3)
    return SimpleNamespace(__version__='mock-rocm', version=SimpleNamespace(hip=hip),
                           cuda=cuda, bfloat16='bf16', float16='fp16', float32='fp32',
                           device=lambda name: name, inference_mode=nullcontext)


class DeviceProfileTests(unittest.TestCase):
    def test_explicit_cpu_does_not_probe_or_choose_available_gpu(self):
        torch = fake_torch()
        self.assertEqual(resolve_profile(torch)['device'], 'cpu')
        torch.cuda.is_available.assert_not_called()

    def test_rocm_uses_cuda_namespace_but_requires_hip(self):
        with self.assertRaisesRegex(BackendUnavailable, 'HIP/ROCm'):
            resolve_profile(fake_torch(hip=None), 'rocm-bf16')
        info = resolve_profile(fake_torch(), 'rocm-bf16', 1)
        self.assertEqual((info['backend'], info['device'], info['gpu_architecture']), ('rocm', 'cuda:1', 'gfx1151'))
        self.assertEqual(info['quantization'], 'none')

    def test_unavailable_invalid_index_and_low_memory_fail_without_fallback(self):
        for torch, index in [(fake_torch(available=False), 0), (fake_torch(), 2), (fake_torch(free_gib=8), 0)]:
            with self.subTest(index=index), self.assertRaises(BackendUnavailable):
                resolve_profile(torch, 'rocm-bf16', index)

    def test_native_fp16_is_explicit_not_silent_bf16_fallback(self):
        torch = fake_torch(bf16=False)
        with self.assertRaisesRegex(BackendUnavailable, 'BF16'):
            resolve_profile(torch, 'rocm-bf16')
        self.assertEqual(resolve_profile(torch, 'rocm-fp16')['profile'], 'rocm-fp16')
        self.assertEqual(dtype_for_profile(torch, 'rocm-fp16'), 'fp16')

    def test_configuration_rejects_implicit_or_unsupported_backend(self):
        for profile, index in [('auto', 0), ('cuda', 0), ('npu', 0), ('cpu-nf4', 1), ('rocm-bf16', -1), ('rocm-bf16', True)]:
            with self.subTest(profile=profile, index=index), self.assertRaises(ValueError):
                validate_profile(profile, index)

    def test_probe_does_not_claim_model_or_kernel_test(self):
        result = check(fake_torch(), 'rocm-bf16')
        self.assertFalse(result['model_loaded'])
        self.assertEqual(result['kernel_test'], 'not_run')


class AdapterProfileTests(unittest.TestCase):
    def test_original_standalone_path_import_needs_no_project_on_sys_path(self):
        source = Path(__file__).resolve().parents[1] / 'runtime/live_adapter.py'
        code = "import importlib.util; from pathlib import Path; import sys; spec=importlib.util.spec_from_file_location('standalone',sys.argv[1]); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); assert m.ClefRuntime(Path('.')).status()['state']=='unloaded'; assert 'torch' not in sys.modules"
        subprocess.run([sys.executable, '-I', '-B', '-c', code, str(source)], check=True, capture_output=True)

    def test_gpu_construction_stays_lazy_and_unverified(self):
        before = 'torch' in sys.modules
        runtime = ClefRuntime(Path('.'), profile='rocm-bf16')
        self.assertEqual('torch' in sys.modules, before)
        self.assertIsNone(runtime.status()['device'])
        self.assertIsNone(runtime.status()['runtime'])

    def test_gpu_loader_never_imports_or_configures_bitsandbytes(self):
        for profile in ['rocm-bf16', 'rocm-fp16']:
            torch = fake_torch()
            runtime = ClefRuntime(Path('.'), profile=profile, device_index=1)
            runtime._runtime_info = resolve_profile(torch, profile, 1)
            vendor = MagicMock()
            # Any accidental import of transformers/BitsAndBytesConfig fails.
            with patch.dict(sys.modules, {'transformers': None, 'bitsandbytes': None}):
                runtime._load_model(vendor, torch)
            kwargs = vendor.load_release_model.call_args.kwargs
            self.assertEqual(kwargs, {'device': 'cuda:1', 'dtype': dtype_for_profile(torch, profile), 'local_files_only': True})

    def test_cpu_loader_retains_original_nf4_configuration(self):
        torch = fake_torch()
        runtime = ClefRuntime(Path('.'))
        runtime._runtime_info = resolve_profile(torch)
        config = MagicMock()
        vendor = MagicMock()
        with patch.dict(sys.modules, {'transformers': SimpleNamespace(BitsAndBytesConfig=config)}):
            runtime._load_model(vendor, torch)
        config.assert_called_once_with(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype='bf16', bnb_4bit_use_double_quant=True, llm_int8_skip_modules=['lm_head'])
        self.assertEqual(vendor.load_release_model.call_args.kwargs['device'], 'cpu')
        self.assertIn('quantization_config', vendor.load_release_model.call_args.kwargs)

    def model(self, dtype='bf16', device='cuda:0'):
        embedding = SimpleNamespace(dtype=dtype, shape=(248320, 4096), device=device, is_floating_point=lambda: True)
        head = SimpleNamespace(dtype=dtype, device=device, is_floating_point=lambda: True)
        model = SimpleNamespace(language_model=SimpleNamespace(get_output_embeddings=lambda: SimpleNamespace(weight=embedding)),
                                head=SimpleNamespace(parameters=lambda: iter([head])),
                                named_parameters=lambda: iter([('embedding', embedding), ('head', head)]))
        return model, embedding, head

    def test_preserve_head_lexical_embedding_and_full_device_placement(self):
        torch = fake_torch()
        runtime = ClefRuntime(Path('.'), profile='rocm-bf16')
        runtime._runtime_info = resolve_profile(torch, 'rocm-bf16')
        model, embedding, head = self.model()
        runtime._validate_model(model, torch)
        for parameter, attribute, wrong in [(embedding, 'dtype', 'uint8'), (embedding, 'shape', (1, 4096)), (head, 'dtype', 'fp16'), (head, 'device', 'cpu')]:
            original = getattr(parameter, attribute)
            setattr(parameter, attribute, wrong)
            with self.subTest(attribute=attribute, wrong=wrong), self.assertRaises(RuntimeError):
                runtime._validate_model(model, torch)
            setattr(parameter, attribute, original)

    def test_fp16_validates_original_head_at_explicitly_selected_precision(self):
        torch = fake_torch()
        runtime = ClefRuntime(Path('.'), profile='rocm-fp16')
        runtime._runtime_info = resolve_profile(torch, 'rocm-fp16')
        runtime._validate_model(self.model(dtype='fp16')[0], torch)
        self.assertIn('conversion', runtime._runtime_info['precision'])

    def test_wrong_fp32_backbone_cannot_be_labeled_bf16_or_fp16(self):
        torch = fake_torch()
        for profile, dtype in [('rocm-bf16', 'bf16'), ('rocm-fp16', 'fp16')]:
            runtime = ClefRuntime(Path('.'), profile=profile)
            runtime._runtime_info = resolve_profile(torch, profile)
            model, embedding, head = self.model(dtype=dtype)
            wrong = SimpleNamespace(dtype='fp32', device='cuda:0', is_floating_point=lambda: True)
            model.named_parameters = lambda: iter([('embedding', embedding), ('head', head), ('language_model.mlp.weight', wrong)])
            with self.subTest(profile=profile), self.assertRaisesRegex(RuntimeError, 'unexpected precision'):
                runtime._validate_model(model, torch)

    def test_gpu_inference_batches_on_selected_device_and_synchronizes_timing(self):
        events = []
        torch = fake_torch()
        torch.cuda.synchronize.side_effect = lambda device: events.append(('sync', device))
        runtime = ClefRuntime(Path('.'), profile='rocm-bf16', device_index=1)
        runtime._runtime_info = resolve_profile(torch, 'rocm-bf16', 1)
        runtime._torch = torch
        runtime._processor = SimpleNamespace(tokenizer=SimpleNamespace(pad_token_id=0))
        encoded = SimpleNamespace(input_ids=[1, 2], questions=[SimpleNamespace(question_id='decision', option_ids=['a', 'b'])])
        values = MagicMock()
        values.float.return_value.softmax.return_value.tolist.return_value = [0.7, 0.3]
        runtime._model = lambda batch: events.append(('forward', batch)) or [[values]]
        runtime._vendor = SimpleNamespace(encode_record=lambda *args, **kwargs: encoded,
            collate_records=lambda records, pad, device: events.append(('collate', device)) or 'batch',
            systemone_answer=lambda question, probs: {'choice': 'a'})
        request = {'state': 'test', 'questions': {'decision': {'type': 'choice', 'criteria': {'a': 'A', 'b': 'B'}}}}
        with patch.object(runtime, '_ensure_loaded'):
            result = runtime.infer(request)
        self.assertEqual(events, [('collate', 'cuda:1'), ('sync', 'cuda:1'), ('forward', 'batch'), ('sync', 'cuda:1')])
        self.assertEqual(result['device'], 'cuda:1')
        self.assertEqual(result['runtime']['profile'], 'rocm-bf16')
        self.assertFalse(result['benchmark_result'])
        self.assertEqual(result['probabilities_unrounded']['decision'], {'a': 0.7, 'b': 0.3})


class ServerProfileTests(unittest.TestCase):
    def test_requested_gpu_not_reported_as_loaded_or_verified(self):
        health = Workbench(True, Path('.'), profile='rocm-bf16').health()
        self.assertEqual(health['requested_profile'], 'rocm-bf16')
        self.assertFalse(health['model_loaded'])
        self.assertIsNone(health['runtime'])

    def test_profile_forwarded_once_and_health_reports_actual_runtime(self):
        info = resolve_profile(fake_torch(), 'rocm-fp16', 1)
        runtime = SimpleNamespace(infer=lambda request: {'runtime': info}, status=lambda: {'state': 'ready', 'runtime': info})
        factory = MagicMock(return_value=runtime)
        app = Workbench(True, Path('.'), factory, profile='rocm-fp16', device_index=1)
        self.assertEqual(app.infer({})[0], 200)
        self.assertEqual(app.infer({})[0], 200)
        factory.assert_called_once_with(Path('.'), profile='rocm-fp16', device_index=1)
        self.assertEqual(app.health()['runtime']['device'], 'cuda:1')

    def test_backend_guard_is_actionable_503_without_a_fake_answer(self):
        runtime = SimpleNamespace(infer=MagicMock(side_effect=BackendUnavailable('ROCm unavailable; no fallback')))
        app = Workbench(True, Path('.'), lambda *a, **k: runtime, profile='rocm-bf16')
        status, body = app.infer({})
        self.assertEqual(status, 503)
        self.assertNotIn('answers', body)
        self.assertIn('no fallback', body['error'])
        self.assertFalse(app.lock.locked())


if __name__ == '__main__':
    unittest.main()
