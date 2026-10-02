"""Lazy, local-only Clef-flash CPU adapter. No model download or import on construction.

The server must opt in to live inference, bind loopback, validate requests, and
serialize access. This adapter independently serializes calls and validates all
pinned release files before importing vendor code. Live requests are separate
from the frozen benchmark and must never be added to its scores.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any

MODEL_ID = 'Cloudflare/clef-flash'
REVISION = '17f0b0ad64efb65d273590632833508766b2aae6'
SOURCE_SHA256 = '0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3'
# Filled from the independently verified official release manifest below.
EXPECTED_FILES: dict[str, dict[str, Any]] = {'chat_template.jinja': {'bytes': 7756, 'sha256': 'a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'}, 'config.json': {'bytes': 2832, 'sha256': '66f87f6fb2616b46604daf2a9c67ddc87938296d07156efa34d59b5be49e3238'}, 'generation_config.json': {'bytes': 116, 'sha256': '45707f8467bf4e54e112c6095a1b2d1f2d63651cf86816344cfff21f02dda0d4'}, 'joint_head.safetensors': {'bytes': 243538016, 'sha256': '19cdcec8c81dc9212be320fff47462ab342fbc1278be4368fb3da71241cf5ba0'}, 'joint_head_config.json': {'bytes': 119, 'sha256': '77efe959a38b5b17b241543e129e695f3c77465ece55a25985279bd8176279a0'}, 'joint_schema_model.py': {'bytes': 23263, 'sha256': '0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3'}, 'model-00001-of-00004.safetensors': {'bytes': 4942706120, 'sha256': '8b45a8e968141cdcc58fb71c9adfc258e2c77b5f062bc636c1fd5bc5d916b565'}, 'model-00002-of-00004.safetensors': {'bytes': 4987757928, 'sha256': '7590856c713eed844a2dcf48e6c43c4de165b788bc3f80e328311183cdbc7db8'}, 'model-00003-of-00004.safetensors': {'bytes': 4954810240, 'sha256': 'e6eac2467952c33361ed7dcb3c7959d1086bbe57201cd3749c3d769fdc17fe63'}, 'model-00004-of-00004.safetensors': {'bytes': 3934446832, 'sha256': '9fcecc6556b39171238373a465f409794b7f821fb4cd1e6459e3a9c0fe317af7'}, 'model.safetensors.index.json': {'bytes': 69253, 'sha256': '941305ff9f77551e145a6cea976ef456cd5cb208cbece99f168376c752fcf96c'}, 'processor_config.json': {'bytes': 1191, 'sha256': 'd89ef49ce9cd37fbf510158e13c1ef063d9286411c1ec9049932dbe0487143b1'}, 'tokenizer.json': {'bytes': 19989325, 'sha256': '06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523'}, 'tokenizer_config.json': {'bytes': 1075, 'sha256': '91a08f825d370d085d692e04cf117cdd7faad7bf18e996f1e6031b6dab03db72'}}


class ClefRuntime:
    """Create cheaply; the first infer() verifies files and loads the model once."""

    def __init__(self, model_dir: Path, threads: int = 6, max_length: int = 2048):
        if not isinstance(threads, int) or not 1 <= threads <= 128:
            raise ValueError('threads must be an integer from 1 to 128')
        if not isinstance(max_length, int) or not 64 <= max_length <= 2048:
            raise ValueError('max_length must be an integer from 64 to 2048')
        self.model_dir = Path(model_dir).expanduser().resolve()
        self.threads = threads
        self.max_length = max_length
        self._lock = threading.RLock()
        self._model = self._processor = self._vendor = self._torch = None
        self._state = 'unloaded'
        self._error: str | None = None
        self._load_seconds: float | None = None
        self._verify_seconds: float | None = None
        self._successful_requests = 0

    def status(self) -> dict[str, Any]:
        # Do not lock: the UI must be able to observe loading while infer runs.
        return {
            'state': self._state,
            'model': MODEL_ID,
            'revision': REVISION,
            'device': 'cpu',
            'precision': 'NF4 backbone; original BF16 joint head and output embeddings',
            'threads': self.threads,
            'max_length': self.max_length,
            'load_seconds': self._load_seconds,
            'verification_seconds': self._verify_seconds,
            'successful_requests': self._successful_requests,
            'error': self._error,
        }

    def _verify_files(self) -> None:
        if not self.model_dir.is_dir():
            raise FileNotFoundError('Model directory is missing; download the pinned release explicitly first')
        for name, expected in EXPECTED_FILES.items():
            path = self.model_dir / name
            if not path.is_file() or path.stat().st_size != expected['bytes']:
                raise ValueError(f'Pinned release file missing or wrong size: {name}')
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(8 * 1024**2), b''):
                    digest.update(chunk)
            if digest.hexdigest() != expected['sha256']:
                raise ValueError(f'Pinned release checksum mismatch: {name}')

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        self._state = 'verifying'
        self._error = None
        try:
            started = time.perf_counter()
            self._verify_files()
            self._verify_seconds = time.perf_counter() - started
            # Imports remain lazy: browsing stored results needs no ML packages.
            import psutil
            if psutil.virtual_memory().available < 7.5 * 1024**3:
                raise RuntimeError('Live inference needs at least 7.5 GiB available RAM before loading; close other heavy processes')
            import torch
            from transformers import AutoProcessor, BitsAndBytesConfig
            torch.set_num_threads(self.threads)
            try:
                torch.set_num_interop_threads(1)
            except RuntimeError:
                if torch.get_num_interop_threads() != 1:
                    raise RuntimeError('Set Torch interop threads to 1 before other Torch work in this server')
            torch.manual_seed(20261002)
            source = self.model_dir / 'joint_schema_model.py'
            if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
                raise ValueError('Official source changed after verification')
            module_name = '_clef_pinned_' + REVISION
            spec = importlib.util.spec_from_file_location(module_name, source)
            if spec is None or spec.loader is None:
                raise RuntimeError('Cannot import verified official Clef source')
            vendor = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = vendor
            spec.loader.exec_module(vendor)
            self._state = 'loading'
            started = time.perf_counter()
            # Catch missing image/video-processor dependencies before weight loading.
            AutoProcessor.from_pretrained(self.model_dir, local_files_only=True)
            quant = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type='nf4',
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
                llm_int8_skip_modules=['lm_head'],
            )
            model, processor = vendor.load_release_model(
                self.model_dir, device='cpu', dtype=torch.bfloat16,
                quantization_config=quant, local_files_only=True,
            )
            embedding = model.language_model.get_output_embeddings().weight
            if embedding.dtype != torch.bfloat16 or tuple(embedding.shape) != (248320, 4096):
                raise RuntimeError('Original BF16 lexical output embedding was not preserved')
            if any(parameter.dtype != torch.bfloat16 for parameter in model.head.parameters()):
                raise RuntimeError('Original joint head must remain BF16')
            self._model, self._processor, self._vendor, self._torch = model, processor, vendor, torch
            self._load_seconds = time.perf_counter() - started
            self._state = 'ready'
        except Exception as exc:
            self._state = 'error'
            self._error = f'{type(exc).__name__}: {exc}'
            raise

    def infer(self, request: dict[str, Any]) -> dict[str, Any]:
        """Return answers plus unrounded probabilities and forward-only latency."""
        if not isinstance(request, dict) or 'state' not in request:
            raise ValueError('request must contain state and questions')
        questions = request.get('questions')
        if not isinstance(questions, dict) or not questions:
            raise ValueError('questions must be a nonempty object')
        # Never forward client metadata, filenames, image URLs, labels or gold data.
        clean = {'model': 'clef-flash', 'state': request['state'], 'questions': questions}
        with self._lock:
            first_call = self._model is None
            self._ensure_loaded()
            torch, vendor, processor = self._torch, self._vendor, self._processor
            started = time.perf_counter()
            full = vendor.encode_record(processor.tokenizer, clean, processor=processor, max_length=1_000_000)
            if len(full.input_ids) > self.max_length:
                raise ValueError(f'Input is {len(full.input_ids)} tokens; maximum is {self.max_length}. Nothing was truncated or inferred')
            encoded = vendor.encode_record(processor.tokenizer, clean, processor=processor, max_length=self.max_length)
            if encoded.input_ids != full.input_ids:
                raise RuntimeError('Input truncation detected; inference was refused')
            batch = vendor.collate_records([encoded], processor.tokenizer.pad_token_id, torch.device('cpu'))
            encode_seconds = time.perf_counter() - started
            started = time.perf_counter()
            with torch.inference_mode():
                logits = self._model(batch)[0]
            inference_seconds = time.perf_counter() - started
            probabilities = {
                q.question_id: dict(zip(q.option_ids, values.float().softmax(-1).tolist()))
                for q, values in zip(encoded.questions, logits)
            }
            for values in probabilities.values():
                if not all(math.isfinite(v) and 0 <= v <= 1 for v in values.values()) or abs(sum(values.values()) - 1) > 1e-5:
                    raise RuntimeError('Model returned invalid probabilities')
            answers = {qid: vendor.systemone_answer(questions[qid], probs) for qid, probs in probabilities.items()}
            self._successful_requests += 1
            return {
                'answers': answers,
                'probabilities_unrounded': probabilities,
                'input_tokens': len(encoded.input_ids),
                'truncated': False,
                'encode_seconds': encode_seconds,
                'inference_seconds': inference_seconds,
                'latency_ms': inference_seconds * 1000,
                'first_call_after_load': first_call,
                'load_seconds': self._load_seconds if first_call else 0.0,
                'verification_seconds': self._verify_seconds if first_call else 0.0,
                'model': MODEL_ID, 'revision': REVISION,
                'precision': 'experimental CPU NF4; BF16 joint head and lexical output embeddings',
                'benchmark_result': False,
            }
