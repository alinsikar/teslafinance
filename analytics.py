import pandas as pd
import numpy as np

REQUIRED = ['month','location','category','budget_qty','actual_qty','budget_unit_price','actual_unit_price']

def prepare(df):
    df=df.copy()
    missing=set(REQUIRED)-set(df.columns)
    if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
    for c in ['budget_qty','actual_qty','budget_unit_price','actual_unit_price']:
        df[c]=pd.to_numeric(df[c],errors='raise')
    if (df[['budget_qty','actual_qty','budget_unit_price','actual_unit_price']]<0).any().any():
        raise ValueError('Negative quantities or prices are not supported')
    df['month']=pd.to_datetime(df['month'],format='%Y-%m',errors='raise')
    df['budget_eur']=df.budget_qty*df.budget_unit_price
    df['actual_eur']=df.actual_qty*df.actual_unit_price
    df['price_variance']=(df.actual_unit_price-df.budget_unit_price)*df.actual_qty
    df['quantity_variance']=(df.actual_qty-df.budget_qty)*df.budget_unit_price
    df['variance_eur']=df.actual_eur-df.budget_eur
    df['variance_pct']=np.where(df.budget_eur>0,100*df.variance_eur/df.budget_eur,np.nan)
    assert np.allclose(df.price_variance+df.quantity_variance,df.variance_eur,rtol=1e-9,atol=0.01)
    return df

def summary(df):
    budget=float(df.budget_eur.sum()); actual=float(df.actual_eur.sum()); delta=actual-budget
    return {'budget':budget,'actual':actual,'variance':delta,'variance_pct':delta/budget*100 if budget else None}

def category_summary(df):
    d=df.groupby('category',as_index=False)[['budget_eur','actual_eur','price_variance','quantity_variance','variance_eur']].sum()
    d['variance_pct']=np.where(d.budget_eur>0,d.variance_eur/d.budget_eur*100,np.nan)
    return d.sort_values('variance_eur',ascending=False)

def flags(df, threshold=10.0):
    # Row-level budget variance flags; threshold is not a probability or audit finding.
    d=df.loc[(df.variance_pct>threshold)&df.variance_pct.notna()].copy()
    d['severity']=np.where(d.variance_pct>=20,'High','Review')
    return d.sort_values('variance_pct',ascending=False)

def money(v):
    if abs(v)>=1e6: return f'€{v/1e6:,.2f}M'
    if abs(v)>=1e3: return f'€{v/1e3:,.1f}K'
    return f'€{v:,.0f}'

def pct(v):
    return 'N/A' if v is None or pd.isna(v) else f'{v:+.1f}%'
