"""Independent, standard-library-only probability audit reference.

Written before inspecting the primary implementation or frozen prediction files.
No model calls, fitting, calibration, score clipping, or threshold selection.
"""

import math
from collections import Counter

THRESHOLDS = (0.50, 0.70, 0.80, 0.90, 0.95, 0.99)
SUM_TOLERANCE = 1e-5


def validate_record(record, sum_tolerance=SUM_TOLERANCE, max_tolerance=0.0):
    """Return errors; raw probability vectors are never normalized or altered."""
    if record is None:
        return ['missing']
    required = ('id', 'options', 'probabilities', 'gold', 'choice')
    errors = ['missing_' + k for k in required if k not in record]
    if errors:
        return errors
    options, ps = record['options'], record['probabilities']
    if not isinstance(options, list) or not options or any(not isinstance(o, str) for o in options) or len(set(options)) != len(options):
        errors.append('invalid_options')
        return errors
    if not isinstance(ps, list) or len(ps) != len(options):
        errors.append('probability_shape')
        return errors
    if any(isinstance(p, bool) or not isinstance(p, (float, int)) or not math.isfinite(p) or p < 0 or p > 1 for p in ps):
        errors.append('invalid_probability')
        return errors
    if abs(math.fsum(ps) - 1) > sum_tolerance:
        errors.append('probability_sum')
    if record['gold'] not in options:
        errors.append('unknown_gold')
    if record['choice'] not in options:
        errors.append('unknown_choice')
    elif ps[options.index(record['choice'])] < max(ps) - max_tolerance:
        errors.append('nonmax_native_choice')
    return errors


def confidence_bin(confidence):
    if not 0 <= confidence <= 1 or not math.isfinite(confidence):
        raise ValueError('confidence outside [0,1]')
    # Explicit decimal boundaries avoid a multiplication-based rounding step.
    for b in range(9):
        if confidence < (b + 1) / 10:
            return b
    return 9


def average(values):
    return math.fsum(values) / len(values) if values else None


def error_auroc(rows):
    """Error is positive; score = 1-selected probability; paired ties earn 0.5."""
    # Compare the original scores in reverse order: subtracting from 1 can
    # collapse distinct representable scores into an artificial tie.
    positive = [r['confidence'] for r in rows if not r['correct']]
    negative = [r['confidence'] for r in rows if r['correct']]
    if not positive or not negative:
        return None
    return sum((a < b) + 0.5 * (a == b) for a in positive for b in negative) / (len(positive) * len(negative))


def compute(records, expected_ids=None, sum_tolerance=SUM_TOLERANCE, max_tolerance=0.0):
    """Audit one suite/field. No pooling. Duplicated/unexpected IDs invalidate input."""
    records = list(records)
    ids = [r.get('id') for r in records if r is not None]
    duplicate_ids = sorted(k for k, n in Counter(ids).items() if n > 1)
    if duplicate_ids:
        raise ValueError('duplicate_ids: ' + ','.join(map(str, duplicate_ids)))
    expected = list(ids if expected_ids is None else expected_ids)
    if len(set(expected)) != len(expected):
        raise ValueError('duplicate_expected_ids')
    unexpected = set(ids) - set(expected)
    if unexpected:
        raise ValueError('unexpected_ids: ' + ','.join(sorted(map(str, unexpected))))
    by_id = {r['id']: r for r in records if r is not None}
    rows, invalid, missing = [], {}, []
    for rid in expected:
        rec = by_id.get(rid)
        if rec is None:
            missing.append(rid)
            continue
        errors = validate_record(rec, sum_tolerance=sum_tolerance, max_tolerance=max_tolerance)
        if errors:
            invalid[rid] = errors
            continue
        opts, ps = rec['options'], rec['probabilities']
        gold_idx, choice_idx = opts.index(rec['gold']), opts.index(rec['choice'])
        gold_p, confidence = ps[gold_idx], ps[choice_idx]
        rows.append(dict(id=rid, correct=rec['gold'] == rec['choice'],
                         confidence=confidence, gold_probability=gold_p,
                         brier=math.fsum((p - int(i == gold_idx))**2 for i,p in enumerate(ps)),
                         nll=-math.log(gold_p) if gold_p > 0 else math.inf,
                         choice=rec['choice'], gold=rec['gold'],
                         max_tie_options=[o for o,p in zip(opts,ps) if p == max(ps)],
                         original=rec))
    n = len(rows)
    correct = sum(r['correct'] for r in rows)
    bins = []
    for b in range(10):
        chosen = [r for r in rows if confidence_bin(r['confidence']) == b]
        count = len(chosen)
        hits = sum(r['correct'] for r in chosen)
        conf = average([r['confidence'] for r in chosen])
        acc = hits / count if count else None
        gap = abs(conf - acc) if count else None
        bins.append(dict(index=b, lower=b/10, upper=(b+1)/10, upper_inclusive=b==9,
                         count=count, correct=hits, mean_confidence=conf, accuracy=acc, absolute_gap=gap))
    risk = []
    for threshold in THRESHOLDS:
        chosen = [r for r in rows if r['confidence'] >= threshold]
        errors = sum(not r['correct'] for r in chosen)
        risk.append(dict(threshold=threshold, accepted=len(chosen), errors=errors,
                         coverage=len(chosen)/n if n else None,
                         expected_coverage=len(chosen)/len(expected) if expected else None,
                         risk=errors/len(chosen) if chosen else None))
    infinities = [r['id'] for r in rows if math.isinf(r['nll'])]
    return dict(expected_n=len(expected), observed_n=len(records), valid_n=n,
                missing_ids=missing, invalid=invalid, complete=not missing and not invalid,
                correct=correct, accuracy=correct/n if n else None,
                mean_confidence=average([r['confidence'] for r in rows]),
                brier=average([r['brier'] for r in rows]),
                nll=math.inf if infinities else average([r['nll'] for r in rows]),
                infinite_nll_ids=infinities,
                ece=math.fsum(b['count']*b['absolute_gap'] for b in bins if b['count'])/n if n else None,
                bins=bins, risk_coverage=risk,
                error_auroc=error_auroc(rows),
                errors=[r for r in rows if not r['correct']],
                high_score_errors=[r for r in rows if not r['correct'] and r['confidence'] >= 0.9],
                rows=rows)
