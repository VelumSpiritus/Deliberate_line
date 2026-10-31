"""Illustrative arithmetic for correlated breadth in the public paper.
All IC and breadth inputs are scenarios, not estimates from market data.
IR = IC * sqrt(BR) uses breadth over the stated measurement period.
It does not convert the result into an annual investment return.
"""
import math

def ir(ic, breadth):
    return ic*math.sqrt(breadth)

print("ILLUSTRATION: treating 1,200,000 contracts as independent")
for ic in (0.05,0.10):
    print(f"IC={ic:.2f}, nominal breadth=1200000: IR={ir(ic,1200000):.2f}")
print("ILLUSTRATION: fewer independent factors over the stated period")
for factors, rebalances, years in [(3,12,10),(6,24,10),(10,52,20)]:
    breadth=factors*rebalances*years
    print(f"factors={factors}, rebalances/year={rebalances}, years={years}, BR={breadth}: "
          f"IR at IC=.05/.10 = {ir(.05,breadth):.2f}/{ir(.10,breadth):.2f}")
print("Correlated contracts share exposures; effective breadth must be estimated separately.")
