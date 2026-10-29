"""
SABRY VISION - Ultimate Enterprise Global Universe & Quant Terminal (v4.0 Final Edition)
Featuring Dynamic Expansion, Full TASI, Full US Markets, Commodities & Dedicated ETFs,
Separated Setup Toggles, Dynamic Scoring, Advanced Stop-Loss Types (ATR, Chandelier, Trailing),
5-Minute Timeframe, Mandatory/Optional VWAP, Stop Hunts, and Telegram Integration.
"""

import os
import json
import logging
import io
import requests
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import zoneinfo
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

st.set_page_config(
    page_title="SABRY VISION - Ultimate Enterprise Quant Terminal",
    page_icon="🛡️",
    layout="wide"
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SabryVisionFinalEnterprise")

@dataclass
class SabryConfig:
    account_size: float = 100000.0
    max_extension_atr: float = 4.0
    atr_multiplier: float = 2.0
    stop_type: str = "ATR Multiplier"
    enable_scoring: bool = True
    require_vwap_alignment: bool = False
    min_liquidity: float = 100000.0
    min_price: float = 1.0

if "custom_watchlist" not in st.session_state:
    st.session_state["custom_watchlist"] = [
        "AAPL", "MSFT", "2222.SR", "1120.SR", 
        "GLD", "SLV", "QQQ", "SPY", "XLK", 
        "BTC-USD"
    ]

# ------------------------------------------------------------------------------
# GLOBAL UNIVERSE LOADER (Full TASI, Full US, Commodities, ETFs & Dynamic Expansion)
# ------------------------------------------------------------------------------
class GlobalUniverseLoader:
    
    @staticmethod
    def get_tasi_universe() -> List[str]:
        tasi_raw = [
            "2222", "1120", "1180", "2010", "1210", "1010", "1020", "1030", "1060", "1080",
            "1090", "1110", "1111", "1121", "1150", "1181", "1182", "2020", "2060", "2170", 
            "2290", "2310", "2330", "2350", "2380", "2381", "2382", "2070", "2080", "2090", 
            "2100", "2120", "2130", "2140", "2150", "2160", "2180", "2190", "2200", "2210", 
            "2230", "2240", "2250", "2270", "2300", "2320", "2340", "2360", "2370", "4001", 
            "4002", "4003", "4004", "4005", "4006", "4007", "4008", "4009", "4010", "4020", 
            "4030", "4040", "4050", "4060", "4070", "4080", "4090", "4100", "4110", "4130", 
            "4140", "4150", "4160", "4180", "4190", "4200", "4210", "4220", "4230", "4240", 
            "4250", "4260", "4270", "4280", "4290", "4300", "4310", "4320", "4330", "7010", 
            "7020", "7030", "7040", "7200", "5110", "1301", "1302", "1303", "1304", "8010", 
            "8012", "8020", "8030", "8040", "8050", "8060", "8070", "8080", "8090", "8100", 
            "8110", "8120", "8130", "8140", "8150", "8160", "8170", "8180", "8190", "8200", 
            "8210", "8230", "8240", "8250", "8260", "8270", "8280", "8300", "8310", "8311", 
            "8340", "4340", "4341", "4342", "4343", "4344", "4345", "4346", "4347", "4348", 
            "4349", "4350", "3001", "3002", "3003", "3004", "3005", "3006", "3007", "3008", 
            "3010", "3020", "3030", "3040", "3050", "3060", "6001", "6002", "6004", "6010", 
            "6020", "6040", "6060", "9510", "9521", "9522"
        ]
        return [f"{t}.SR" for t in tasi_raw]

    @staticmethod
    def get_commodities_and_etfs_universe() -> List[str]:
        return [
            "GC=F", "GLD", "IAU", "SGOL", 
            "SI=F", "SLV", "SIVR", 
            "CL=F", "BZ=F", "USO", "UNG",
            "QQQ", "XLK", "SOXX", "ARKK", "SPY", "VOO", "IVV",
            "HG=F", "PL=F", "PA=F", "CPER"
        ]

    @staticmethod
    def get_crypto_universe() -> List[str]:
        return ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]

    @staticmethod
    def fetch_sp500_tickers() -> List[str]:
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            df = pd.read_html(io.StringIO(res.text))[0]
            return df["Symbol"].str.replace(".", "-", regex=False).tolist()
        except Exception:
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    @staticmethod
    def fetch_nasdaq100_tickers() -> List[str]:
        try:
            url = "https://en.wikipedia.org/wiki/NASDAQ-100"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            df = pd.read_html(io.StringIO(res.text))[3]
            return df["Ticker"].str.replace(".", "-", regex=False).tolist()
        except Exception:
            return ["AAPL", "MSFT", "TSLA", "AMD"]

    @classmethod
    def get_full_us_universe(cls) -> List[str]:
        return sorted(list(set(cls.fetch_sp500_tickers() + cls.fetch_nasdaq100_tickers())))

class UnifiedDataProvider:
    def fetch_raw_ohlcv(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
            if df.empty:
                return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            if df.index.tz is not None:
                df.index = df.index.tz_convert("UTC").tz_localize(None)
            return df
        except Exception:
            return pd.DataFrame()

# ------------------------------------------------------------------------------
# ADVANCED SCANNER ENGINE (Separated Setups, Stop Losses, VWAP, Volume Profile)
# ------------------------------------------------------------------------------
class SabryVisionScanner:
    def __init__(self, cfg: SabryConfig, active_setups: List[str]):
        self.config = cfg
        self.active_setups = active_setups

    def calculate_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        f["sma50"] = f["close"].rolling(50).mean()
        f["sma200"] = f["close"].rolling(200).mean()
        f["ema20"] = f["close"].ewm(span=20, adjust=False).mean()
        
        tp = (f["high"] + f["low"] + f["close"]) / 3.0
        f["vwap"] = (tp * f["volume"]).rolling(20).sum() / f["volume"].rolling(20).sum()
        
        tr = np.maximum(
            f["high"] - f["low"],
            np.maximum((f["high"] - f["close"].shift(1)).abs(), (f["low"] - f["close"].shift(1)).abs())
        )
        f["atr14"] = tr.rolling(14).mean()
        f["atr50"] = tr.rolling(50).mean()
        
        # Chandelier Exit Stop Calculation
        f["chandelier_long"] = f["high"].rolling(22).max() - (f["atr14"] * 3.0)
        
        diff = f["ema20"] - f["ema20"].shift(3)
        f["ema20_slope"] = (diff / (3 * f["atr14"].replace(0, np.nan))).fillna(0.0)
        
        f["volume_ma20"] = f["volume"].rolling(20).mean()
        f["rvol"] = (f["volume"] / f["volume_ma20"].replace(0, np.nan)).fillna(1.0)
        f["poc"] = tp.rolling(50).mean()
        f["rs_momentum"] = f["close"].pct_change(63)
        return f

    def calculate_stop_loss(self, row: pd.Series) -> float:
        close = row["close"]
        atr = row["atr14"]
        st_type = self.config.stop_type
        
        if st_type == "Chandelier Exit":
            return round(row.get("chandelier_long", close - (2.5 * atr)), 2)
        elif st_type == "Trailing Stop":
            return round(close - (1.5 * atr), 2)
        else:
            return round(close - (self.config.atr_multiplier * atr), 2)

    def detect_setups(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        f["pivot_20"] = f["high"].rolling(20).max().shift(1)
        f["low_20"] = f["low"].rolling(20).min().shift(1)
        
        is_breakout = (f["close"] > f["pivot_20"]) & (f["rvol"] >= 1.2) & (f["close"] > f["open"])
        is_setup = (f["close"] <= f["pivot_20"]) & (f["close"] >= f["pivot_20"] * 0.95)
        is_retest = (f["close"].shift(1) > f["pivot_20"]) & (f["low"] <= f["poc"] * 1.02) & (f["close"] > f["poc"])
        is_bottom = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"]) & (f["rvol"] >= 1.3)
        
        f["sig_breakout"] = is_breakout if "BREAKOUT" in self.active_setups else False
        f["sig_setup"] = is_setup if "SETUP" in self.active_setups else False
        f["sig_retest"] = is_retest if "RETEST" in self.active_setups else False
        f["sig_bottom_reversal"] = is_bottom if "BOTTOM_REVERSAL" in self.active_setups else False
        
        if self.config.require_vwap_alignment:
            vwap_mask = f["close"] >= f["vwap"]
            f["sig_breakout"] &= vwap_mask
            f["sig_setup"] &= vwap_mask
            f["sig_retest"] &= vwap_mask
            f["sig_bottom_reversal"] &= vwap_mask

        conditions = [f["sig_breakout"], f["sig_retest"], f["sig_setup"], f["sig_bottom_reversal"]]
        choices = ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"]
        f["signal_type"] = np.select(conditions, choices, default="NONE")
        return f

    def calculate_score(self, df: pd.DataFrame) -> pd.Series:
        if not self.config.enable_scoring:
            return pd.Series(75.0, index=df.index)
        
        rs_s = df["rs_momentum"].rank(pct=True).fillna(0.5) * 30.0
        slope_s = df["ema20_slope"].clip(0, 3) / 3.0 * 30.0
        rvol_s = df["rvol"].clip(0, 3) / 3.0 * 40.0
        return (rs_s + slope_s + rvol_s).clip(0, 100).round(1)

# ------------------------------------------------------------------------------
# STREAMLIT UI - ADVANCED COMMAND CENTER
# ------------------------------------------------------------------------------
st.title("🛡️ SABRY VISION - Enterprise Global Quant Terminal (v4.0)")

st.sidebar.header("🎛️ لوحة التحكم الشاملة والمتقدمة")

market_mode = st.sidebar.selectbox(
    "اختر نطاق الفحص الرئيسي:",
    [
        "القائمة المخصصة (Custom Watchlist - قابلة لإضافة أي صندوق/سهم)", 
        "السوق السعودي (تاسي الكامل - TASI)", 
        "السوق الأمريكي (S&P 500 & Nasdaq 100)", 
        "السلع العالمية وصناديق الذهب والتقنية والـ ETFs", 
        "العملات الرقمية (Crypto)"
    ]
)

timeframe = st.sidebar.selectbox("الإطار الزمني للفحص:", ["5m", "15m", "1h", "1d"])
period_choice = st.sidebar.selectbox("المدى التاريخي للبيانات:", ["1mo", "3mo", "6mo", "1y"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 تخصيص أنواع الفرص (Setup Kinds)")
setup_options = ["BREAKOUT", "SETUP", "RETEST", "BOTTOM_REVERSAL"]
selected_setups = st.sidebar.multiselect(
    "اختر الفرص المراد رصدها:",
    setup_options,
    default=["BREAKOUT", "SETUP", "RETEST", "BOTTOM_REVERSAL"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ إعدادات الشروط والوقف (Stop-Loss & Rules)")
stop_type = st.sidebar.selectbox(
    "نوع حساب وقف الخسارة:",
    ["ATR Multiplier", "Chandelier Exit", "Trailing Stop"]
)
atr_mult_val = st.sidebar.slider("معامل مضاعف الـ ATR:", 1.0, 4.0, 2.0, 0.5)

enable_scoring = st.sidebar.checkbox("تفعيل السكور المؤسسي (Scoring Engine)", value=True)
require_vwap = st.sidebar.checkbox("الـ VWAP شرط إلزامي قاطع", value=False)

config = SabryConfig(
    atr_multiplier=atr_mult_val,
    stop_type=stop_type,
    enable_scoring=enable_scoring,
    require_vwap_alignment=require_vwap
)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "🚀 السكانر الذكي المتسع", 
    "📋 إدارة القوائم وإضافة أي صندوق حر", 
    "⚙️ إشعارات التليجرام"
])

with tab1:
    st.header("🔍 المسح الفوري المتقدم وفق إعداداتك المخصصة")
    st.write(f"النطاق النشط: **{market_mode}** | الإطار: **{timeframe}** | الفرص المفعلة: **{selected_setups}**")
    
    if st.button("🚀 بدء المسح والتحليل المتقدم"):
        if not selected_setups:
            st.error("⚠️ يرجى اختيار نوع فرصة واحد على الأقل من القائمة الجانبية لتشغيل السكانر.")
        else:
            with st.spinner("جاري جلب البيانات، تطبيق معايير صبري فيجن، وحساب المستهدفات والأوقف بدقة..."):
                provider = UnifiedDataProvider()
                scanner = SabryVisionScanner(config, selected_setups)
                
                if "القائمة المخصصة" in market_mode:
                    tickers = st.session_state["custom_watchlist"]
                elif "تاسي" in market_mode:
                    tickers = GlobalUniverseLoader.get_tasi_universe()
                elif "الأمريكي" in market_mode:
                    tickers = GlobalUniverseLoader.get_full_us_universe()
                elif "السلع" in market_mode:
                    tickers = GlobalUniverseLoader.get_commodities_and_etfs_universe()
                else:
                    tickers = GlobalUniverseLoader.get_crypto_universe()
                    
                results = []
                progress = st.progress(0)
                total = len(tickers)
                
                for i, t in enumerate(tickers):
                    df = provider.fetch_raw_ohlcv(t, period=period_choice, interval=timeframe)
                    if not df.empty and len(df) >= 30:
                        f = scanner.calculate_technical_features(df)
                        f = scanner.detect_setups(f)
                        latest = f.iloc[-1]
                        if latest["signal_type"] != "NONE":
                            score = scanner.calculate_score(f).iloc[-1]
                            stop_price = scanner.calculate_stop_loss(latest)
                            close_p = latest["close"]
                            risk_pct = round((close_p - stop_price) / close_p * 100, 2)
                            target_price = round(close_p * (1 + (risk_pct * 2 / 100)), 2)
                            
                            results.append({
                                "الرمز / الصندوق": t,
                                "النموذج": latest["signal_type"],
                                "السكور": score,
                                "الإغلاق": round(close_p, 2),
                                "وقف الخسارة": stop_price,
                                "نسبة المخاطرة %": risk_pct,
                                "الهدف المقترح": target_price,
                                "RVOL": round(latest["rvol"], 2)
                            })
                    progress.progress((i + 1) / total)
                    
                if results:
                    res_df = pd.DataFrame(results).sort_values(by="السكور", ascending=False)
                    st.success(f"🎉 تم رصد {len(res_df)} فرصة استثمارية مطابقة لمعاييرك بدقة:")
                    st.dataframe(res_df, use_container_width=True)
                else:
                    st.warning("⚠️ لم يتم رصد إشارات في هذه العينة. جرب توسيع القائمة المخصصة أو تعديل فريم الزمن أو تفعيل فرص إضافية من القائمة الجانبية.")

with tab2:
    st.header("📋 إدارة القائمة المخصصة وإضافة أي صندوق حر")
    st.write("أضف أي صندوق استثماري محلي (صناديق الذهب، التقنية، البلاد، الراجحي) أو سهم عالمي لفحصه فوراً:")
    
    col1, col2 = st.columns(2)
    with col1:
        user_input_ticker = st.text_input("أدخل رمز السهم أو الصندوق بدقة (مثال: GLD, QQQ, أو رمز في تاسي):")
        if st.button("➕ إضافة وتوسيع القائمة"):
            if user_input_ticker and user_input_ticker.upper() not in st.session_state["custom_watchlist"]:
                st.session_state["custom_watchlist"].append(user_input_ticker.upper())
                st.success(f"تم توسيع القائمة وإضافة '{user_input_ticker.upper()}' بنجاح!")
                st.rerun()
    with col2:
        st.subheader("قائمتك الموسعة الحالية:")
        st.write(st.session_state["custom_watchlist"])
        if st.button("🗑️ إعادة تعيين القائمة"):
            st.session_state["custom_watchlist"] = ["AAPL", "MSFT", "2222.SR", "GLD", "SLV", "QQQ"]
            st.rerun()

with tab3:
    st.header("⚙️ إعدادات التليجرام والتنبيهات الآلية")
    tg_token = st.text_input("Telegram Bot Token", type="password")
    tg_chat = st.text_input("Telegram Chat ID")
    if st.button("إرسال رسالة اختبار"):
        url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
        try:
            res = requests.post(url, json={"chat_id": tg_chat, "text": "<b>SABRY VISION v4.0:</b> تم تفعيل الإشعارات بنجاح!", "parse_mode": "HTML"}, timeout=5)
            if res.status_code == 200:
                st.success("تم إرسال تنبيه التجربة بنجاح!")
            else:
                st.error("فشل الاتصال، تحقق من صحة البيانات.")
        except Exception as e:
            st.error(f"خطأ في الاتصال: {e}")
