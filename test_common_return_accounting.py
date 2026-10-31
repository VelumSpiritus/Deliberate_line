from fractions import Fraction
import pytest
from common_return_accounting import allocate_pool, return_pool


def test_common_payment_is_not_added_on_top_of_full_attribution_pool():
    rows = allocate_pool(23, 9, {'A': '.5', 'B': '.5', 'C': '0'})
    assert [rows[name]['total'] for name in rows] == [10, 10, 3]
    assert sum(row['attributable'] for row in rows.values()) == 14
    assert sum(row['total'] for row in rows.values()) == 23


def test_common_only_distribution_conserves_indivisible_fractions():
    rows = allocate_pool(1, 1, {'A': 0, 'B': 0, 'C': 0})
    assert all(row['universal'] == Fraction(1, 3) for row in rows.values())
    assert sum(row['total'] for row in rows.values()) == 1


def test_no_residual_rate_produces_no_collection():
    assert return_pool(1000, 0) == 0
    assert allocate_pool(0, 0, {'A': 0})['A']['total'] == 0


@pytest.mark.parametrize('total,common,weights', [
    (10, 11, {'A': 1}),
    (10, 2, {'A': '.5'}),
    (10, 2, {'A': '-1', 'B': '2'}),
    (10, 2, {'A': 'unknown'}),
    (10, 2, {}),
])
def test_invalid_or_unresolved_allocation_is_not_silently_paid(total, common, weights):
    with pytest.raises(ValueError):
        allocate_pool(total, common, weights)
