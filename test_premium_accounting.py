import math
import pytest
from premium_accounting import example, premium_from_gap_shares


def test_rate_and_growth_fraction_are_distinct_results():
    result = example()
    assert result['premium_log_growth_per_year'] == pytest.approx(.023)
    assert result['premium_fraction_of_market_log_growth'] == pytest.approx(2.3/7.9)


def test_nonzero_initial_share_recovers_growth_rate_over_stated_period():
    start, rate, years = .2, .023, 7.
    end = 1-(1-start)*math.exp(-rate*years)
    assert premium_from_gap_shares(start, end, years) == pytest.approx(rate)


def test_declining_relative_claims_produce_negative_premium():
    assert premium_from_gap_shares(.2, .1, 5) < 0
