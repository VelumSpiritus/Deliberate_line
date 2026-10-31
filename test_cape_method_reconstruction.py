import csv
import math
import pytest
from cape_method_reconstruction import fit,load,reconstruct


def test_known_linear_fit():
    result=fit([1,2,3],[3,5,7])
    assert result=={'intercept':1,'slope':2,'correlation':1}


def test_calendar_gap_cannot_turn_two_months_into_one(tmp_path):
    p=tmp_path/'history.csv'
    p.write_text('Date,PE10,Real Price\n2000-01-01,20,100\n2000-03-01,21,101\n')
    with pytest.raises(ValueError,match='contiguous'):load(p)


def test_zero_padded_future_is_not_a_real_outcome(tmp_path):
    p=tmp_path/'history.csv'
    p.write_text('Date,PE10,Real Price\n2000-01-01,20,100\n2000-02-01,21,101\n2000-03-01,0,0\n')
    assert len(load(p))==2
    with pytest.raises(ValueError,match='insufficient'):reconstruct(p,horizon_months=1)


def test_invalid_target_is_rejected():
    with pytest.raises(ValueError,match='positive'):reconstruct(target_cape=0)
