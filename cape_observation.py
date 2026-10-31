"""Read dated CAPE observations without turning missing values into measured zero."""
from datetime import date
import hashlib
import json
import math
from pathlib import Path

DEFAULT=Path(__file__).parent/'data/ensemble/cape_multpl_monthly.json'


def read_cape(path=DEFAULT, *, as_of=None, max_age_days=None):
    path=Path(path)
    raw=path.read_bytes()
    document=json.loads(raw)
    if not isinstance(document.get('source_url'),str) or not document['source_url'].startswith('https://'):
        raise ValueError('CAPE source URL required')
    if not isinstance(document.get('retrieved_at'),str):
        raise ValueError('CAPE retrieval date required')
    retrieved=date.fromisoformat(document['retrieved_at'][:10])
    limit=date.today() if as_of is None else date.fromisoformat(str(as_of))
    if retrieved>limit:
        raise ValueError('CAPE source retrieved after as-of date')
    observations=[]
    for row in document.get('rows',[]):
        day=date.fromisoformat(row['date'])
        value=row.get('cape')
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
            raise ValueError('CAPE must be a finite positive observation')
        if day>retrieved or day>limit:
            raise ValueError('CAPE observation is future-dated')
        observations.append((day,value))
    if not observations:
        raise ValueError('CAPE observations missing')
    day,value=max(observations)
    if max_age_days is not None and (limit-day).days>max_age_days:
        raise ValueError('CAPE observation exceeds requested freshness limit')
    return {'date':day.isoformat(),'cape':value,'source_url':document['source_url'],
            'retrieved_at':document['retrieved_at'],'file_sha256':hashlib.sha256(raw).hexdigest(),
            'as_of':limit.isoformat(),'age_days':(limit-day).days}
