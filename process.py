# =========================
# Stock Breakout Automation
# =========================

from tradingview_screener import Query
import pandas as pd
import numpy as np

# -------------------------
# 1) ดึงข้อมูลจาก TradingView
# -------------------------

column_tdv_multiperiod = [
    'name','description','sector','close'
    'market_cap_basic',
    'Perf.W','Perf.1M','Perf.3M','Perf.6M','Perf.Y'
]

markets = 'thailand'
number_stocks = 30000

df_multi_period = (Query()
                    .select(*column_tdv_multiperiod)
                    .set_markets(markets)
                    .limit(number_stocks)
                    .get_scanner_data())

df_multi_period = df_multi_period[1]

# -------------------------
# 2) Filter หุ้น
# -------------------------

df_filter = df_multi_period[
    (df_multi_period['ticker'].str.endswith(('R','F')) == False) &
    (df_multi_period['market_cap_basic'] >= 1_000_000_000)
].copy()

# -------------------------
# 3) คำนวณ RS Score
# -------------------------

weights = {
    'Perf.W': 0.10,
    'Perf.1M': 0.20,
    'Perf.3M': 0.30,
    'Perf.6M': 0.25,
    'Perf.Y': 0.15
}

df_filter['rs_weight'] = 0

for col, weight in weights.items():
    df_filter['rs_weight'] += df_filter[col] * weight

df_filter['rs_rank'] = df_filter['rs_weight'].rank(pct=True) * 100

# -------------------------
# 4) แบ่ง Category
# -------------------------

bins = [0, 80, 85, 90, 95, 101]
labels = ['RS Below 80', 'RS80-85', 'RS85-90', 'RS90-95', 'RS95-100']

df_filter['rs_category'] = pd.cut(df_filter['rs_rank'], bins=bins, labels=labels)

df_filter = df_filter.sort_values('rs_rank', ascending=False)

# -------------------------
# 5) Final DataFrame
# -------------------------

df_filter_final = df_filter[
    ['name','description','sector','close','rs_rank','rs_category']
].reset_index(drop=True)

# -------------------------
# 6) Export JSON
# -------------------------

df_filter_final.to_json(
    "rs_data.json",
    orient="records",
    force_ascii=False
)

print("RS data updated successfully.")
