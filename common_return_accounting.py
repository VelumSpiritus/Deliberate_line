"""Exact accounting for supplied common/attributable portions of one return pool.

This checks allocation conservation. It does not infer contribution weights,
settle future claims, or estimate an economy's response to the proposed rule.
"""
from fractions import Fraction
import json


def amount(value, name):
    if isinstance(value, bool):
        raise ValueError(f'{name}: a finite number is required')
    try:
        result = Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f'{name}: a finite number is required') from exc
    if result < 0:
        raise ValueError(f'{name}: must be nonnegative')
    return result


def return_pool(surplus, rate_per_interval):
    return amount(surplus, 'surplus') * amount(rate_per_interval, 'rate_per_interval')


def allocate_pool(total, common, weights):
    total, common = amount(total, 'total'), amount(common, 'common')
    if common > total:
        raise ValueError('common: cannot exceed total pool')
    if not weights:
        raise ValueError('recipients: at least one eligible person is required')
    if any(not isinstance(name, str) or not name.strip() for name in weights):
        raise ValueError('recipients: each person needs an explicit identifier')
    weights = {name: amount(value, f'weight[{name}]') for name, value in weights.items()}
    attributed = total-common
    if attributed and sum(weights.values()) != 1:
        raise ValueError('attribution: supplied weights must sum to one for a nonzero attributed pool')
    base = common/len(weights)
    payments = {name: {'universal': base, 'attributable': value*attributed,
                       'total': base+value*attributed} for name, value in weights.items()}
    assert sum(row['total'] for row in payments.values()) == total
    return payments


def example():
    pool = return_pool('1000', '.023')
    payments = allocate_pool(pool, '9', {'A': '1/2', 'B': '1/2', 'C': '0'})
    return {
        'scope': 'One-year accounting example with stated inputs; no contribution inference or macroeconomic forecast',
        'surplus': '1000', 'rate_for_interval': '.023', 'pool': str(pool),
        'common_portion': '9', 'attributable_portion': str(pool-9),
        'payments': {name: {key: str(value) for key, value in row.items()}
                     for name, row in payments.items()},
        'total_paid': str(sum(row['total'] for row in payments.values())),
        'rounding': 'Exact fractions before any currency-unit rounding rule',
    }


if __name__ == '__main__':
    print(json.dumps(example(), indent=2))
