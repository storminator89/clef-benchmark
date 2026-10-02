"""Descriptive metrics on already validated native-score rows. Standard library only."""
import math
from collections import Counter
THRESHOLDS = (0.5, 0.7, 0.8, 0.9, 0.95, 0.99)

def field_metrics(rows, expected_count):
    items = []
    for r in rows:
        p = r['probabilities']; y = r['gold']; choice = r['choice']
        py = p[y]
        items.append(dict(id=r['id'], gold=y, choice=choice,
            confidence=p[choice], correct=choice == y,
            brier=math.fsum((value-(key == y))**2 for key,value in p.items()),
            nll=-math.log(py) if py > 0 else None,
            nll_is_infinite=py == 0, gold_probability=py,
            tied_maximum_count=sum(value == p[choice] for value in p.values())))
    n=len(items); correct=sum(r['correct'] for r in items)
    bins=[]
    for b in range(10):
        lo=b/10; hi=(b+1)/10
        members=[r for r in items if lo <= r['confidence'] and (r['confidence'] < hi or b==9)]
        count=len(members); k=sum(r['correct'] for r in members)
        score=math.fsum(r['confidence'] for r in members)/count if count else None
        acc=k/count if count else None
        bins.append(dict(lower=lo,upper=hi,upper_inclusive=b==9,count=count,correct=k,
            mean_score=score,accuracy=acc,signed_score_minus_accuracy_gap=score-acc if count else None,
            absolute_gap=abs(score-acc) if count else None))
    risk=[]
    for threshold in THRESHOLDS:
        take=[r for r in items if r['confidence'] >= threshold]; count=len(take)
        k=sum(r['correct'] for r in take)
        risk.append(dict(threshold=threshold,selected_count=count,correct=k,incorrect=count-k,
            expected_count=expected_count,valid_count=n,
            coverage=count/expected_count if expected_count else None,
            valid_coverage=count/n if n else None,risk=(count-k)/count if count else None))
    good=[r for r in items if r['correct']]; bad=[r for r in items if not r['correct']]
    zeros=[r['id'] for r in items if r['nll_is_infinite']]
    finite=[r['nll'] for r in items if r['nll'] is not None]
    auc=(math.fsum(1 if b['confidence'] < g['confidence'] else .5 if b['confidence'] == g['confidence'] else 0
                   for b in bad for g in good)/(len(bad)*len(good))) if good and bad else None
    return dict(expected_count=expected_count,valid_count=n,correct=correct,incorrect=n-correct,
        accuracy=correct/n if n else None,correct_over_expected=correct/expected_count if expected_count else None,
        brier_mean=math.fsum(r['brier'] for r in items)/n if n else None,
        nll_mean=math.fsum(finite)/n if n and not zeros else None,nll_is_infinite=bool(zeros),
        zero_gold_probability_count=len(zeros),zero_gold_probability_ids=zeros,
        finite_nll_count=len(finite),finite_nll_mean=math.fsum(finite)/len(finite) if finite else None,
        mean_selected_score=math.fsum(r['confidence'] for r in items)/n if n else None,
        signed_score_minus_accuracy_gap=(math.fsum(r['confidence'] for r in items)-correct)/n if n else None,
        gold_class_counts=dict(sorted(Counter(r['gold'] for r in rows).items())),
        saved_choice_class_counts=dict(sorted(Counter(r['choice'] for r in rows).items())),
        tie_count=sum(r['tied_maximum_count'] > 1 for r in items),
        bins=bins,ece_10_equal_width=math.fsum(b['count']*(b['absolute_gap'] or 0) for b in bins)/n if n else None,
        risk_coverage=risk,error_detection_auroc=auc,error_auroc_correct_count=len(good),error_auroc_incorrect_count=len(bad),
        high_score_error_ids={format(t,'.2f'):[r['id'] for r in bad if r['confidence']>=t] for t in THRESHOLDS},
        items=items)
