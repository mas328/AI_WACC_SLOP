"""The WACC card.

Run from the repo root:   streamlit run app.py

Owner: the product manager. This works today on the FAKE numbers, so you can build
the page before the real numbers exist. When the developer's pull request is merged,
outputs/wacc.csv appears and the app switches to it automatically.

The app only reads outputs/ and inputs/. The what-if section re-applies the README's
WACC formula to slider values; it does no downloading or estimation.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

COLUMNS = ['ticker', 'asof', 'beta', 'rf', 'mrp', 'cost_of_equity',
           'rd', 'tax', 'w_e', 'w_d', 'wacc']

st.set_page_config(page_title='WACC card', layout='centered')

real = Path('outputs/wacc.csv')
rows = pd.read_csv(real if real.exists() else 'outputs/wacc_FAKE.csv')
inputs = pd.read_csv('inputs/assumptions.csv', index_col='item')

# Checks for things that would silently break the card.
missing = set(COLUMNS) - set(rows.columns)
assert not missing, f'wacc.csv is missing columns: {sorted(missing)}'
assert len(rows) >= 1, 'wacc.csv has no rows'
card = rows.iloc[0]  # the client is the first row; any extra rows are peers
assert abs(card['w_e'] + card['w_d'] - 1) < 1e-6, 'weights must sum to 1'
assert 0 < card['wacc'] < 0.25, 'WACC outside 0-25%: check the inputs'


def wacc(beta, rf, mrp, rd, tax, w_d):
    """Same formula as README.md, with w_e = 1 - w_d."""
    cost_of_equity = rf + beta * mrp
    return (1 - w_d) * cost_of_equity + w_d * rd * (1 - tax), cost_of_equity


def source(item):
    return inputs['source'].get(item, '') if item in inputs.index else ''


if not real.exists():
    st.warning('Showing FAKE numbers. Run `python code/wacc.py` to make outputs/wacc.csv.')

# --- Headline -------------------------------------------------------------
st.title(f"WACC card: {card['ticker']}")
st.caption(f"Returns through {card['asof']}")

st.markdown(
    f"**Bottom line:** {card['ticker']}'s cost of capital is **{card['wacc']:.1%}**. "
    f"A new project with the same risk as the existing business should be approved only "
    f"if it is expected to return more than {card['wacc']:.1%}. Riskier projects need a higher hurdle."
)

after_tax_rd = card['rd'] * (1 - card['tax'])
c1, c2, c3, c4 = st.columns(4)
c1.metric('WACC (hurdle rate)', f"{card['wacc']:.2%}")
c2.metric('Cost of equity', f"{card['cost_of_equity']:.2%}")
c3.metric('After-tax cost of debt', f"{after_tax_rd:.2%}")
c4.metric('Beta vs. SPY', f"{card['beta']:.2f}")

# --- How it is built ------------------------------------------------------
st.subheader('How the WACC is built')
build = pd.DataFrame([
    ('Risk-free rate', f"{card['rf']:.2%}", source('rf')),
    ('Beta', f"{card['beta']:.2f}", 'Estimated: 5 years of daily returns vs. SPY'),
    ('Market risk premium', f"{card['mrp']:.2%}", source('mrp')),
    ('Cost of equity = rf + beta × MRP', f"{card['cost_of_equity']:.2%}", 'Calculated'),
    ('Pre-tax cost of debt', f"{card['rd']:.2%}", source('rd')),
    ('Tax rate', f"{card['tax']:.0%}", source('tax')),
    ('Equity weight', f"{card['w_e']:.0%}", source('w_e')),
    ('Debt weight', f"{card['w_d']:.0%}", source('w_d')),
    ('WACC', f"{card['wacc']:.2%}", 'w_e × cost of equity + w_d × rd × (1 − tax)'),
], columns=['Input', 'Value', 'Source'])
st.dataframe(build, hide_index=True, width='stretch')

# --- What if --------------------------------------------------------------
st.subheader('What if?')
st.caption('Move the sliders to see how the hurdle rate responds. '
           'Beta is held fixed, so leverage changes are a first approximation only.')
s1, s2 = st.columns(2)
w_d = s1.slider('Debt weight (w_d)', 0.0, 0.8, float(card['w_d']), 0.01, format='%.2f')
mrp = s2.slider('Market risk premium', 0.03, 0.08, float(card['mrp']), 0.0025, format='%.4f')

new_wacc, new_ke = wacc(card['beta'], card['rf'], mrp, card['rd'], card['tax'], w_d)
d1, d2 = st.columns(2)
d1.metric('WACC', f'{new_wacc:.2%}', f"{(new_wacc - card['wacc']) * 1e4:+.0f} bp",
          delta_color='inverse')
d2.metric('Cost of equity', f'{new_ke:.2%}',
          f"{(new_ke - card['cost_of_equity']) * 1e4:+.0f} bp", delta_color='inverse')

# --- Peers ----------------------------------------------------------------
st.subheader('Compared with peers')
if len(rows) > 1:
    peers = rows[['ticker', 'beta', 'cost_of_equity', 'w_d', 'wacc']].rename(columns={
        'ticker': 'Ticker', 'beta': 'Beta', 'cost_of_equity': 'Cost of equity',
        'w_d': 'Debt weight', 'wacc': 'WACC'})
    st.dataframe(
        peers.style.format({'Beta': '{:.2f}', 'Cost of equity': '{:.2%}',
                            'Debt weight': '{:.0%}', 'WACC': '{:.2%}'}),
        hide_index=True, width='stretch')
    st.bar_chart(peers.set_index('Ticker')['WACC'])
else:
    st.info('Peer comparison appears here once outputs/wacc.csv has a row for each '
            'competitor (e.g. COST, TGT). The client stays in the first row.')
