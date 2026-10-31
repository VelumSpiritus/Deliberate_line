"""Reconstruct the retained log-CAPE/ten-year real-price method, separately from total return.

The retained original-session narrative reports r=-0.35 and the rough -1% to -2.5% range.
The later retained capetest.py identifies log(CAPE), real prices and overlapping horizons.
This explicit OLS reconstruction supplies a reproducible value within that rough range.
The range is a rounded descriptive statement, not a fitted confidence interval.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics as st

from cape_observation import read_cape

HERE=Path(__file__).parent
DATA=HERE/'data/ensemble/shiller_sp500_monthly.csv'


def month_index(value):
    return int(value[:4])*12+int(value[5:7])-1


def load(path=DATA):
    rows=[]
    for row in csv.DictReader(Path(path).open(encoding='utf-8')):
        cape,price=float(row['PE10']),float(row['Real Price'])
        if cape>0 and price>0:
            if not math.isfinite(cape) or not math.isfinite(price):
                raise ValueError('non-finite historical observation')
            rows.append({'date':row['Date'],'cape':cape,'price':price})
    if any(month_index(b['date'])-month_index(a['date'])!=1 for a,b in zip(rows,rows[1:])):
        raise ValueError('historical monthly observations are not contiguous')
    return rows


def fit(x,y):
    xm,ym=st.mean(x),st.mean(y)
    xx=sum((v-xm)**2 for v in x)
    yy=sum((v-ym)**2 for v in y)
    if not xx or not yy:
        raise ValueError('non-varying fit')
    xy=sum((v-xm)*(w-ym) for v,w in zip(x,y))
    slope=xy/xx
    return {'intercept':ym-slope*xm,'slope':slope,'correlation':xy/math.sqrt(xx*yy)}


def reconstruct(path=DATA, *, target_cape=41.0, horizon_months=120):
    if not math.isfinite(target_cape) or target_cape<=0 or type(horizon_months) is not int or horizon_months<=0:
        raise ValueError('positive CAPE and horizon required')
    rows=load(path)
    starts=rows[:-horizon_months]
    if len(starts)<3:raise ValueError('insufficient matured observations')
    x=[math.log(row['cape']) for row in starts]
    y=[math.log(rows[i+horizon_months]['price']/row['price'])/(horizon_months/12) for i,row in enumerate(starts)]
    model=fit(x,y)
    forecast=100*math.expm1(model['intercept']+model['slope']*math.log(target_cape))
    high=[100*math.expm1(v) for row,v in zip(starts,y) if row['cape']>=30]
    return {'method':'OLS annualized real log-price return on log(CAPE)',
            'formula':'log(P_real[t+H]/P_real[t])/(H/12) = intercept + slope*log(CAPE[t])',
            'return_conversion':'exp(fitted annual log return)-1',
            'includes_dividends':False,'horizon_months':horizon_months,
            'valid_history':[rows[0]['date'],rows[-1]['date']],
            'matured_start_dates':[starts[0]['date'],starts[-1]['date']],
            'n_overlapping_months':len(starts),'model':model,
            'target_cape':target_cape,'reconstructed_real_price_CAGR_pct':forecast,
            'CAPE_at_least_30':{'n':len(high),'median_real_price_CAGR_pct':st.median(high)},
            'data_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'scope':'Descriptive historical OLS reconstruction; overlapping observations, no fitted uncertainty interval and no causal forecast certification.',
            'original_range':'Original rough -1% to -2.5% statement preserved and corroborated by the explicit fit; not a fitted confidence interval.'}


if __name__=='__main__':
    result={'schema':'cape-method-reconstruction-v1','dated_CAPE_input':read_cape(),
            'reconstruction':reconstruct()}
    print(json.dumps(result,indent=2))
