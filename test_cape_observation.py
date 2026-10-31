from datetime import date
import json
import pytest
from cape_observation import read_cape


def write(tmp_path,**changes):
    data={'source_url':'https://example.com/cape','retrieved_at':'2026-09-20T16:15',
          'rows':[{'date':'2026-09-18','cape':40.94}]}|changes
    p=tmp_path/'cape.json';p.write_text(json.dumps(data),encoding='utf-8');return p


def test_missing_file_is_not_zero(tmp_path):
    with pytest.raises(FileNotFoundError):read_cape(tmp_path/'missing.json',as_of='2026-09-20')


@pytest.mark.parametrize('value',[0,-1,None,True,float('nan')])
def test_invalid_observations_are_not_measurements(tmp_path,value):
    with pytest.raises(ValueError):read_cape(write(tmp_path,rows=[{'date':'2026-09-18','cape':value}]),as_of='2026-09-20')


def test_dated_observation_and_explicit_freshness_limit(tmp_path):
    p=write(tmp_path)
    result=read_cape(p,as_of='2026-09-20',max_age_days=31)
    assert result['cape']==40.94 and result['date']=='2026-09-18' and result['age_days']==2
    with pytest.raises(ValueError,match='freshness'):read_cape(p,as_of='2026-10-31',max_age_days=31)


def test_unsorted_rows_use_latest_date(tmp_path):
    p=write(tmp_path,rows=[{'date':'2026-09-18','cape':40.94},{'date':'2026-08-01','cape':41.13}])
    assert read_cape(p,as_of='2026-09-20')['cape']==40.94


def test_missing_source_and_future_row_rejected(tmp_path):
    with pytest.raises(ValueError,match='source'):read_cape(write(tmp_path,source_url=''),as_of='2026-09-20')
    with pytest.raises(ValueError,match='future'):read_cape(write(tmp_path,rows=[{'date':'2026-10-01','cape':41}]),as_of='2026-09-20')
