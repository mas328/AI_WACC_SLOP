"""The WACC card.

Run from the repo root:   streamlit run app.py

Owner: the product manager. This works today on the FAKE numbers, so you can build
the page before the real numbers exist. When the developer's pull request is merged,
outputs/wacc.csv appears and the app switches to it automatically.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title='WACC card', layout='centered')

real = Path('outputs/wacc.csv')
card = pd.read_csv(real if real.exists() else 'outputs/wacc_FAKE.csv').iloc[0]
inputs = pd.read_csv('inputs/assumptions.csv', index_col='item')

if not real.exists():
    st.warning('Showing FAKE numbers. Run `python code/wacc.py` to make outputs/wacc.csv.')

st.title(f"WACC card: {card['ticker']}")
st.caption(f"Returns through {card['asof']}")

c1, c2, c3 = st.columns(3)
c1.metric('WACC', f"{card['wacc']:.2%}")
c2.metric('Cost of equity', f"{card['cost_of_equity']:.2%}")
c3.metric('Beta', f"{card['beta']:.2f}")

st.subheader('Inputs and sources')
st.dataframe(inputs, width='stretch')

# TODO (product manager): make this something a CFO would read. Ideas:
#   - one sentence at the top: what the WACC means for the hurdle rate on new projects
#   - a slider for w_d (leverage) or mrp, with the WACC recomputed live
#   - a comparison to one or two competitors (ask the developer for a second row in wacc.csv)
