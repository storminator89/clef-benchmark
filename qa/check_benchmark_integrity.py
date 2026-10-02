"""Pre-inference artifact checks; does not read inference outputs."""
import collections
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
P = BASE / 'benchmark'

def read(name):
    return [json.loads(s) for s in (P/name).read_text().splitlines() if s.strip()]

cases = read('cases.jsonl')
diagnostics = read('diagnostic_cases.jsonl')
gold = read('gold.jsonl')
requests = read('requests.jsonl')
pairs = read('pairs.jsonl')
policies = json.loads((P/'policies.json').read_text())
all_cases = cases + diagnostics
by_id = {x['id']: x for x in all_cases}
gold_by_id = {x['id']: x for x in gold}
assert len(cases) == 150
assert len(diagnostics) == 30
assert len(all_cases) == len(by_id) == len(gold) == len(requests) == 180
assert set(by_id) == set(gold_by_id) == {x['id'] for x in requests}
assert len(pairs) == len({x['pair_id'] for x in pairs}) == 30
assert len({x['german_id'] for x in pairs}) == 30
assert len({x['english_id'] for x in pairs}) == 30
assert len({x['mixed_id'] for x in pairs}) == 30
assert collections.Counter(x['split'] for x in all_cases) == {'german_primary':120, 'english_control':30, 'mixed_schema_diagnostic':30}
for case in all_cases:
    assert case['questions'] == policies[case['category']][case['schema_language']], case['id']
    assert case['expected']['decision'] in case['questions']['decision']['criteria'], case['id']
    for field in ['expected', 'tags', 'pair_id', 'gold_rationale', 'language', 'category', 'schema_language', 'split']:
        assert case[field] == gold_by_id[case['id']][field], (case['id'], field)
for request in requests:
    assert set(request) == {'id', 'request'}
    payload = request['request']
    assert set(payload) == {'model', 'state', 'questions'}, request['id']
    assert payload['state'] == by_id[request['id']]['input'], request['id']
    assert payload['questions'] == by_id[request['id']]['questions'], request['id']
    assert payload['model'] == 'clef-flash'
for pair in pairs:
    de, en, mixed = (by_id[pair[k]] for k in ['german_id', 'english_id', 'mixed_id'])
    assert de['language'] == mixed['language'] == 'de'
    assert en['language'] == 'en'
    assert de['schema_language'] == 'de'
    assert en['schema_language'] == mixed['schema_language'] == 'en'
    assert de['expected'] == en['expected'] == mixed['expected']
    assert mixed['input'] == de['input']
    assert mixed['questions'] == en['questions']
    assert de['pair_id'] == en['pair_id'] == mixed['pair_id'] == pair['pair_id']
    assert de['category'] == en['category'] == mixed['category'] == pair['category']
counts = {}
for category in policies:
    counts[category] = {}
    for split in ['german_primary', 'english_control', 'mixed_schema_diagnostic']:
        relevant = [c for c in all_cases if c['category'] == category and c['split'] == split]
        counts[category][split] = dict(collections.Counter(c['expected']['decision'] for c in relevant))
        assert len(relevant) == (20 if split == 'german_primary' else 5)
        assert set(counts[category][split]) == set(policies[category]['de']['decision']['criteria'])
        if split == 'german_primary':
            assert len(set(counts[category][split].values())) == 1
filenames = ['cases.jsonl', 'diagnostic_cases.jsonl', 'policies.json', 'gold.jsonl', 'pairs.jsonl', 'requests.jsonl']
summary = {
    'integrity_checks': 'pass',
    'scenario_count': 120,
    'payload_count': 180,
    'sha256': {name: hashlib.sha256((P/name).read_bytes()).hexdigest() for name in filenames},
    'class_counts': counts,
    'paired_german_ids': [x['german_id'] for x in pairs],
    'paired_source_tag_counts': dict(collections.Counter(t for c in cases if c['language']=='en' for t in c['tags'])),
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
