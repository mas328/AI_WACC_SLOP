"""Estimate the client's WACC.

Run from the repo root:   python code/wacc.py
Reads:  inputs/assumptions.csv
Writes: outputs/wacc.csv (one row; the columns are listed in README.md)

Owner: the developer. Assumptions must have sources before publishing a card.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

CLIENT = 'WMT'
MKT = 'SPY'
YEARS = 5
ASSUMPTIONS = ['rf', 'mrp', 'rd', 'tax', 'w_e', 'w_d']


def get_returns(ticker, mkt=MKT, years=YEARS):
    """Daily returns for the client and the market over the last `years` years.
    Returns a DataFrame with two columns, named ticker and mkt, and no missing values."""
    assert ticker != mkt, 'stock and market tickers must differ'
    assert isinstance(years, int) and years > 0, 'years must be a positive integer'
    # Exclude today's incomplete trading session. Yahoo's end is exclusive.
    end = pd.Timestamp.now(tz='America/New_York').normalize().tz_localize(None)
    start = end - pd.DateOffset(years=years)
    data = yf.download(
        [ticker, mkt], start=start.date(), end=end.date(), interval='1d',
        auto_adjust=True, group_by='column', progress=False, threads=False,
    )
    assert data is not None and not data.empty, 'price download failed or returned no data'
    assert 'Close' in data.columns.get_level_values(0), 'download is missing Close prices'
    close = data['Close']
    assert all(t in close.columns for t in [ticker, mkt]), 'download is missing a ticker'
    close = close[[ticker, mkt]].sort_index()
    assert isinstance(close.index, pd.DatetimeIndex), 'prices must have a date index'
    assert close.index.is_unique, 'duplicate price dates'
    assert not close.index.hasnans, 'missing price dates'
    observed = close.to_numpy(dtype=float)
    assert not np.isinf(observed).any(), 'infinite prices'
    assert (close.where(close.notna(), 1) > 0).all().all(), 'prices must be positive'
    # Do not fill gaps: a missing price invalidates both adjacent daily returns.
    rets = close.pct_change(fill_method=None).dropna()
    assert len(rets) > 200 * years, 'insufficient daily returns for requested history'
    assert np.isfinite(rets.to_numpy()).all(), 'returns must be finite with no missing values'
    return rets


def estimate_beta(rets, ticker, mkt=MKT):
    """Equity beta: cov(stock, market) / var(market)."""
    assert ticker != mkt, 'stock and market tickers must differ'
    assert all(t in rets.columns for t in [ticker, mkt]), 'returns are missing a ticker'
    paired = rets[[ticker, mkt]]
    assert len(paired) >= 2, 'at least two paired returns are required'
    assert np.isfinite(paired.to_numpy()).all(), 'returns must be finite with no missing values'
    market_variance = paired[mkt].var(ddof=1)
    assert market_variance > 0, 'market variance must be positive'
    beta = float(paired[ticker].cov(paired[mkt]) / market_variance)
    assert np.isfinite(beta), 'beta must be finite'
    return beta


def compute_wacc(beta, a):
    """a is a dict of assumptions: rf, mrp, rd, tax, w_e, w_d.
    Returns a dict with cost_of_equity and wacc (and the inputs), matching the README's columns."""
    assert all(key in a for key in ASSUMPTIONS), 'missing required assumptions'
    a = {key: float(a[key]) for key in ASSUMPTIONS}
    assert np.isfinite([beta, *a.values()]).all(), 'beta and assumptions must be finite'
    assert all(0 <= a[key] <= 1 for key in ASSUMPTIONS), 'assumptions must be decimals between 0 and 1'
    assert abs(a['w_e'] + a['w_d'] - 1) < 1e-6, 'weights must sum to 1'
    cost_of_equity = a['rf'] + beta * a['mrp']
    wacc = a['w_e'] * cost_of_equity + a['w_d'] * a['rd'] * (1 - a['tax'])
    assert 0 < wacc < 0.25, 'WACC outside 0-25%: check the inputs'
    return {**a, 'cost_of_equity': cost_of_equity, 'wacc': wacc}


if __name__ == '__main__':
    inputs = pd.read_csv('inputs/assumptions.csv', index_col='item')
    assert inputs.index.is_unique, 'duplicate assumption items'
    assert all(key in inputs.index for key in ASSUMPTIONS), 'missing required assumptions'
    assert {'value', 'source'}.issubset(inputs.columns), 'assumptions need value and source columns'
    sources = inputs.loc[ASSUMPTIONS, 'source'].fillna('').astype(str).str.strip()
    unfinished = sources.eq('') | sources.str.contains(r'\bTODO\b', case=False, regex=True)
    assert not unfinished.any(), (
        'Analyst sources are unfinished for: ' + ', '.join(sources.index[unfinished])
        + '. Complete inputs/assumptions.csv before publishing outputs/wacc.csv.'
    )
    a = inputs['value'].to_dict()

    rets = get_returns(CLIENT)
    assert len(rets) > 1000, 'expected about 5 years of daily returns'

    beta = estimate_beta(rets, CLIENT)
    out = compute_wacc(beta, a)
    out = {'ticker': CLIENT, 'asof': rets.index.max().date(), 'beta': beta, **out}

    assert 0 < out['wacc'] < 0.25, 'WACC outside 0-25%: check the inputs'
    cols = ['ticker', 'asof', 'beta', 'rf', 'mrp', 'cost_of_equity', 'rd', 'tax', 'w_e', 'w_d', 'wacc']
    Path('outputs').mkdir(exist_ok=True)
    pd.DataFrame([out])[cols].to_csv('outputs/wacc.csv', index=False)
    print(pd.DataFrame([out])[cols].T)
