"""Rate/share conversions using the paper's rounded annual log-growth inputs.

This is arithmetic illustrating the definitions, not a new fit to market data.
"""
import json
import math


def premium_from_gap_shares(start, end, years):
    """Annual log growth of M/T where s=1-T/M for positive indexed levels."""
    if not all(math.isfinite(x) for x in (start, end, years)):
        raise ValueError('Inputs must be finite')
    if years <= 0 or start >= 1 or end >= 1:
        raise ValueError('Positive years and gap shares below one are required')
    return (math.log1p(-start)-math.log1p(-end))/years


def example():
    market, output, years = .079, .056, 56.0
    premium = market-output
    end_share = -math.expm1(-premium*years)
    return {
        'scope': 'Arithmetic with rounded paper inputs; not independent empirical estimates',
        'market_log_growth_per_year': market,
        'output_log_growth_per_year': output,
        'premium_log_growth_per_year': premium,
        'premium_fraction_of_market_log_growth': premium/market,
        'indexed_level_example': {
            'years': years, 'start_gap_share': 0.0, 'end_gap_share': end_share,
            'annual_premium_recovered_from_shares': premium_from_gap_shares(0., end_share, years),
        },
    }


if __name__ == '__main__':
    print(json.dumps(example(), indent=2))
