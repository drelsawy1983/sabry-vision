"""
SABRY VISION - Unified Core Quantitative Engine (Production Ready)
"""

import os
import html
import time
import zoneinfo
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

import pandas as pd
import numpy as np
import yfinance as yf
import requests

# ==========================================
# 1. إعدادات النظام والهيكلة (Config)
# ==========================================
@dataclass
class MarketConfig:
    market_id: str
    ticker_suffix: str
    index_symbol: str
    timezone: str
    open_time: str
    close_time: str
    trading_days: List[int]
    min_volume_usd: float
    min_price: float

@dataclass
class Config:
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
    account_size: float = 100000.0
    risk_per_trade_pct: float = 0.75
    max_open_positions: int = 10
    atr_multiplier: float = 2.0
    max_extension_atr: float = 3.5
    elite_tier_percentile: float = 0.90
    good_tier_percentile: float = 0.70
    markets: Dict[str, MarketConfig] = field(default_factory=lambda: {
        "US": MarketConfig("US", "", "^GSPC", "America/New_York", "09:30", "16:00", [0, 1, 2, 3, 4], 5000000.0, 5.0),
        "TASI": MarketConfig("TASI", ".SR", "^TASI.SR", "Asia/Riyadh", "10:00", "15:00", [0, 1, 2, 3, 4], 2000000.0, 10.0),
    })

    @classmethod
    def from_secrets(cls, secrets_dict: dict) -> "Config":
        cfg = cls()
        cfg.telegram_bot_token = secrets_dict.get("TELEGRAM_BOT_TOKEN", cfg.telegram_bot_token)
        cfg.telegram_chat_id = secrets_dict.get("TELEGRAM_CHAT_ID", cfg.telegram_chat_id)
        return cfg
 
 

# ==========================================
# 2. طبقة البيانات والكاش التدريجي (Data Layer)
# ==========================================
class YFinanceProvider:
    def fetch_ohlcv(self, ticker: str, interval: str, days: int) -> pd.DataFrame:
        period = f"{days}d" if days <= 60 else "max"
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        df = df[["open", "high", "low", "close", "volume"]].dropna()
        if df.index.tz is not None:
            df.index = df.index.tz_convert("UTC").tz_localize(None)
        return df

def incremental_update(cache_path: str, ticker: str, interval: str, provider: YFinanceProvider) -> pd.DataFrame:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    if os.path.exists(cache_path):
        existing_df = pd.read_parquet(cache_path)
        last_date = existing_df.index.max()
        days_to_fetch = max(1, (datetime.now() - last_date).days + 2)
        new_df = provider.fetch_ohlcv(ticker, interval, days=days_to_fetch)
        if not new_df.empty:
            combined = pd.concat([existing_df, new_df])
            combined = combined[~combined.index.duplicated(keep="last")].sort_index()
            combined.to_parquet(cache_path)
            return combined
        return existing_df
    else:
        full_df = provider.fetch_ohlcv(ticker, interval, days=60)
        if not full_df.empty:
            full_df.to_parquet(cache_path)
        return full_df

# ==========================================
# 3. محرك الميزات والمؤشرات (Feature Engineering)
# ==========================================
def compute_rvol(df: pd.DataFrame, window_days: int = 20) -> pd.Series:
    df_c = df.copy()
    df_c["time_slot"] = df_c.index.time
    mean_vol = df_c.groupby("time_slot")["volume"].transform(
        lambda x: x.shift(1).rolling(window_days, min_periods=1).mean()
    )
    return (df_c["volume"] / mean_vol.replace(0, np.nan)).fillna(1.0)

def compute_poc(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, window: int = 100, bins: int = 50) -> pd.Series:
    tp = (high + low + close) / 3.0
    n = len(tp)
    poc = np.full(n, np.nan)
    tp_v, vol_v = tp.values, volume.values
    for i in range(window - 1, n):
        w_tp, w_vol = tp_v[i - window + 1:i + 1], vol_v[i - window + 1:i + 1]
        lo, hi = w_tp.min(), w_tp.max()
        if hi <= lo or w_vol.sum() == 0:
            poc[i] = tp_v[i]
            continue
        bin_idx = np.minimum(((w_tp - lo) / (hi - lo) * bins).astype(int), bins - 1)
        hist = np.bincount(bin_idx, weights=w_vol, minlength=bins)
        poc[i] = lo + (hist.argmax() + 0.5) * ((hi - lo) / bins)
    return pd.Series(poc, index=close.index).ffill()

def engineer_features(df: pd.DataFrame, benchmark_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    f = df.copy()
    f["sma50"] = f["close"].rolling(50).mean()
    f["sma200"] = f["close"].rolling(200).mean()
    f["ema20"] = f["close"].ewm(span=20, adjust=False).mean()
    
    tr = np.maximum(f["high"] - f["low"], np.maximum((f["high"] - f["close"].shift(1)).abs(), (f["low"] - f["close"].shift(1)).abs()))
    f["atr14"] = tr.rolling(14).mean()
    f["atr50"] = tr.rolling(50).mean()
    
    diff = f["ema20"] - f["ema20"].shift(3)
    f["ema20_slope"] = (diff / (3 * f["atr14"].replace(0, np.nan))).fillna(0.0)
    f["rvol"] = compute_rvol(f)
    f["extension_atr"] = (f["close"] - f["sma50"]) / f["atr14"].replace(0, np.nan)
    f["poc"] = compute_poc(f["high"], f["low"], f["close"], f["volume"])
    
    if benchmark_df is not None and not benchmark_df.empty:
        bench_al = benchmark_df["close"].reindex(f.index).ffill()
        f["rs_momentum"] = (f["close"] / bench_al).pct_change(63)
    else:
        f["rs_momentum"] = f["close"].pct_change(63)
    return f

# ==========================================
# 4. محرك توليد الإشارات الأربع (Signals)
# ==========================================
def detect_signals(df: pd.DataFrame) -> pd.DataFrame:
    f = df.copy()
    f["pivot_20"] = f["high"].rolling(20).max().shift(1)
    f["low_20"] = f["low"].rolling(20).min().shift(1)
    
    f["sig_breakout"] = (f["close"] > f["pivot_20"]) & (f["rvol"] >= 1.5) & (f["close"] > f["open"])
    f["sig_retest"] = (f["close"].shift(1) > f["pivot_20"]) & (f["low"] <= f["poc"] * 1.01) & (f["close"] > f["poc"]) & (f["volume"] < f["volume"].rolling(20).mean())
    f["sig_setup"] = (f["close"] <= f["pivot_20"]) & (f["close"] >= f["pivot_20"] * 0.97) & (f["rvol"] < 1.0)
    
    liq_sweep = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"]) & (f["close"] > f["open"])
    f["sig_bottom_reversal"] = (f["close"] < f["sma200"]) & (f["rvol"] >= 1.8) & (f["close"] > f["poc"]) & liq_sweep
    
    conds = [f["sig_breakout"], f["sig_retest"], f["sig_setup"], f["sig_bottom_reversal"]]
    f["signal_type"] = np.select(conds, ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"], default="NONE")
    return f

# ==========================================
# 5. محرك السكور المؤسسي وإدارة المخاطر (Scoring & Risk)
# ==========================================
def calculate_score(df: pd.DataFrame) -> pd.Series:
    rs_s = df["rs_momentum"].rank(pct=True).fillna(0.5) * 20.0
    slope_s = df["ema20_slope"].clip(0, 3) / 3.0 * 20.0
    rvol_s = df["rvol"].clip(0, 3) / 3.0 * 20.0
    vcp_s = (1.0 - (df["atr14"] / df["atr50"]).clip(0.5, 1.5) + 0.5) * 15.0
    poc_dist = ((df["close"] - df["poc"]) / df["atr14"]).abs()
    poc_s = (1.0 - poc_dist.clip(0, 2) / 2.0) * 15.0
    return (rs_s + slope_s + rvol_s + vcp_s + poc_s + 10.0).clip(0, 100).round(1)

def classify_tier(scores: pd.Series, cfg: Config) -> pd.Series:
    p_el, p_gd = scores.quantile(cfg.elite_tier_percentile), scores.quantile(cfg.good_tier_percentile)
    return pd.Series(np.select([scores >= p_el, scores >= p_gd], ["Elite A+", "Good B"], default="Watchlist"), index=scores.index)

# =================4. التليجرام (Notify) ==========================
def send_telegram(token: str, chat_id: str, msg: str) -> bool:
    if not token or not chat_id: return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": chat_id, "text": html.escape(msg), "parse_mode": "HTML"}, timeout=10)
        return res.status_code == 200
    except:
        return False
"""
SABRY VISION - Main Dashboard Entrypoint (Streamlit)
"""

import streamlit as st
from core_engine import Config

st.set_page_config(
    page_title="SABRY VISION - Institutional Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "config" not in st.session_state:
    secrets = st.secrets if hasattr(st, "secrets") else {}
    st.session_state["config"] = Config.from_secrets(secrets)

st.title("🌐 SABRY VISION - لوحة التحكم الكمية المؤسسية")
st.markdown("---")

st.markdown("""
### أهلاً بك في منظومة صبري فيجن (SABRY VISION)
استخدم القائمة الجانبية للتنقل بين الأقسام:
* **📊 السكانر اللحظي (Scanner):** فحص الأسواق واستخراج الإشارات الأربع مع السكور والدروع.
* **📈 الباك تست (Backtest):** تشغيل المحاكاة التاريخية وتقييم الأداء بالـ Sharpe وDrawdown.
* **⚙️ الإعدادات (Settings):** ضبط إدارة المخاطر ومعايير التصفية.

name: SABRY VISION Automated Scanner

on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:

jobs:
  run-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Background Scanner
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python -c "from core_engine import Config; print('SABRY VISION Automation Engine Loaded Successfully.')"
# 🌐 SABRY VISION - Institutional Quantitative System

نظومة تحليل كمي مؤسسية متكاملة لأسواق المال (أسهم أمريكية, سعودية, مصرية, وسلع).

## 🚀 طريقة التشغيل المحلي (Local Deployment)
1. تثبيت الاعتمادات:
   ```bash
   pip install -r requirements.txt
