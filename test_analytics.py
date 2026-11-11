import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import pytest
from analytics import prepare,summary,flags

def test_bridge_reconciles():
    d=prepare(pd.DataFrame([{'month':'2026-01','location':'Test','category':'Parts','budget_qty':10,'actual_qty':12,'budget_unit_price':100,'actual_unit_price':110}]))
    assert d.iloc[0].budget_eur==1000
    assert d.iloc[0].actual_eur==1320
    assert d.iloc[0].price_variance==120
    assert d.iloc[0].quantity_variance==200
    assert d.iloc[0].variance_eur==320
    assert len(flags(d,10))==1
    assert summary(d)['variance_pct']==32

def test_negative_rejected():
    with pytest.raises(ValueError):
        prepare(pd.DataFrame([{'month':'2026-01','location':'Test','category':'Parts','budget_qty':-1,'actual_qty':12,'budget_unit_price':100,'actual_unit_price':110}]))
