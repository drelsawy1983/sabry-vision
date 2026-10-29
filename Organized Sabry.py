"""
SABRY VISION - Ultimate Enterprise Global Universe & Quant Terminal
Featuring Dynamic Expansion, Full TASI, US Markets, Commodities, Dedicated ETFs,
Albilad & Alrajhi Funds Support, Mandatory VWAP, Stop Hunts, and Volume Profile.
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
logger = logging.getLogger("SabryVisionEnterpriseUltimate")

@dataclass
class SabryConfig:
    account_size: float = 100000.0
    max_extension_atr: float = 3.5
    atr_multiplier: float = 2.0
    elite_tier_percentile: float = 85.0
    good_tier_percentile: float = 60.0
    min_liquidity: float = 100000.0  # مرن للصناديق ذات السيولة المختلفة
    min_price: float = 1.0         # مرن للصناديق ذات الأسعار المختلفة
    require_vwap_alignment: bool = True

if "custom_watchlist" not in st.session_state:
    # قائمة افتراضية موسعة تضم الأسهم، الصناديق المحلية والعالمية، وصناديق الذهب والتقنية
    st.session_state["custom_watchlist"] = [
        "AAPL", "MSFT", "2222.SR", "1120.SR", 
        "GLD", "SLV", "QQQ", "SPY", "XLK", 
        "BTC-USD"
    ]

# ------------------------------------------------------------------------------
# DYNAMIC EXPANDABLE UNIVERSE LOADER
# ------------------------------------------------------------------------------
class GlobalUniverseLoader:
    
    @staticmethod
    def get_tasi_universe() -> List[str]:
        """سوق تداول السعودي (تاسي) - تغطية شاملة لجميع الشركات والصناديق المتداولة REITs"""
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
        """السلع العالمية وصناديق الذهب والفضة والتقنية والأسهم الأمريكية (مثل صناديق البلاد والراجحي والـ ETFs العالمية)"""
        return [
            # الذهب وصناديقه العالمية والمحلية المرتبطة
            "GC=F", "GLD", "IAU", "SGOL", 
            # الفضة
            "SI=F", "SLV", "SIVR", 
            # النفط والطاقة
            "CL=F", "BZ=F", "USO", "UNG",
            # صناديق التقنية والأسهم الأمريكية الكبرى (التي تُبنى عليها الصناديق التقنية والدولية)
            "QQQ", "XLK", "SOXX", "ARKK", "SPY", "VOO", "IVV",
            # المعادن الصناعية والسلع
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
    def fetch_raw_ohlcv(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        try:
            # دالة مرنة تجلب أي رمز في العالم طالما أن صيغته صحيحة في ياهو فاينانس
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
# SCANNER ENGINE (Ultimate Rules & VWAP)
# ------------------------------------------------------------------------------
class SabryVisionScanner:
    def __init__(self, cfg: SabryConfig, active_setups: Dict[str, bool]):
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
        
        diff = f["ema20"] - f["ema20"].shift(3)
        f["ema20_slope"] = (diff / (3 * f["atr14"].replace(0, np.nan))).fillna(0.0)
        f["extension_atr"] = (f["close"] - f["sma50"]) / f["atr14"].replace(0, np.nan)
        
        f["volume_ma20"] = f["volume"].rolling(20).mean()
        f["rvol"] = (f["volume"] / f["volume_ma20"].replace(0, np.nan)).fillna(1.0)
        f["poc"] = tp.rolling(50).mean()
        f["rs_momentum"] = f["close"].pct_change(63)
        return f

    def detect_setups(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        f["pivot_20"] = f["high"].rolling(20).max().shift(1)
        f["low_20"] = f["low"].rolling(20).min().shift(1)
        
        f["sig_breakout"] = False
        if self.active_setups.get("BREAKOUT", True):
            f["sig_breakout"] = (
                (f["close"] > f["pivot_20"]) &
                (f["rvol"] >= 1.5) &
                (f["close"] > f["open"]) &
                (f["close"] >= f["vwap"] if self.config.require_vwap_alignment else True)
            )
        
        f["sig_setup"] = False
        if self.active_setups.get("SETUP", True):
            f["sig_setup"] = (
                (f["close"] <= f["pivot_20"]) &
                (f["close"] >= f["pivot_20"] * 0.97) &
                (f["rvol"] < 1.0)
            )
        
        f["sig_retest"] = False
        if self.active_setups.get("RETEST", True):
            f["sig_retest"] = (
                (f["close"].shift(1) > f["pivot_20"]) &
                (f["low"] <= f["poc"] * 1.01) &
                (f["close"] > f["poc"]) &
                (f["volume"] < f["volume_ma20"])
            )
        
        f["sig_bottom_reversal"] = False
        if self.active_setups.get("BOTTOM_REVERSAL", True):
            stop_hunt_sweep = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"]) & (f["close"] > f["open"])
            f["sig_bottom_reversal"] = (
                (f["close"] < f["sma200"]) &
                (f["rvol"] >= 1.8) &
                (f["close"] > f["poc"]) &
                stop_hunt_sweep
            )
        
        conditions = [f["sig_breakout"], f["sig_retest"], f["sig_setup"], f["sig_bottom_reversal"]]
        choices = ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"]
        f["signal_type"] = np.select(conditions, choices, default="NONE")
        return f

    def calculate_score(self, df: pd.DataFrame) -> pd.Series:
        rs_s = df["rs_momentum"].rank(pct=True).fillna(0.5) * 25.0
        slope_s = df["ema20_slope"].clip(0, 3) / 3.0 * 25.0
        rvol_s = df["rvol"].clip(0, 3) / 3.0 * 25.0
        vwap_bonus = np.where(df["close"] >= df["vwap"], 25.0, 0.0)
        return (rs_s + slope_s + rvol_s + vwap_bonus).clip(0, 100).round(1)

# ------------------------------------------------------------------------------
# STREAMLIT UI - COMMAND CENTER WITH EXPANSION
# ------------------------------------------------------------------------------
st.title("🛡️ SABRY VISION - Dynamic Enterprise Quant Terminal")

st.sidebar.header("🎛️ لوحة التحكم الموسعة للأسواق والصناديق")

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

timeframe = st.sidebar.selectbox("الإطار الزمني للفحص:", ["1d", "1h", "15m"])
period_choice = st.sidebar.selectbox("المدى التاريخي للبيانات:", ["6m", "1y", "2y"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ إعدادات الفرص والشرط الإلزامي")
active_setups = {
    "BREAKOUT": st.sidebar.checkbox("نموذج الاختراق (BREAKOUT)", value=True),
    "SETUP": st.sidebar.checkbox("نموذج التأسيس (SETUP)", value=True),
    "RETEST": st.sidebar.checkbox("إعادة الاختبار (RETEST)", value=True),
    "BOTTOM_REVERSAL": st.sidebar.checkbox("فخاخ السيولة (BOTTOM REVERSAL)", value=True),
}
require_vwap = st.sidebar.checkbox("الـ VWAP شرط إلزامي قاطع", value=True)

config = SabryConfig(require_vwap_alignment=require_vwap)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "🚀 السكانر الشامل والمتسع", 
    "📋 إدارة القوائم وإضافة أي صندوق حر", 
    "⚙️ إشعارات التليجرام"
])

with tab1:
    st.header("🔍 المسح الذكي المتسع للأسواق والصناديق الخاصة")
    st.write(f"النطاق النشط: **{market_mode}** | الإطار: **{timeframe}**")
    
    if st.button("🚀 بدء المسح والتحليل المتسع"):
        with st.spinner("جاري جلب وتحليل البيانات وفق شروط صبري فيجن المؤسسية..."):
            provider = UnifiedDataProvider()
            scanner = SabryVisionScanner(config, active_setups)
            
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
                if not df.empty and len(df) >= 100:
                    f = scanner.calculate_technical_features(df)
                    f = scanner.detect_setups(f)
                    latest = f.iloc[-1]
                    if latest["signal_type"] != "NONE":
                        score = scanner.calculate_score(f).iloc[-1]
                        tier = "Elite A+" if score >= 85 else ("Good B" if score >= 60 else "Watchlist")
                        results.append({
                            "الرمز / الصندوق": t,
                            "النموذج": latest["signal_type"],
                            "السكور": score,
                            "التصنيف": tier,
                            "الإغلاق": round(latest["close"], 2),
                            "RVOL": round(latest["rvol"], 2),
                            "فوق VWAP": "نعم" if latest["close"] >= latest["vwap"] else "لا"
                        })
                progress.progress((i + 1) / total)
                
            if results:
                res_df = pd.DataFrame(results)
                st.success(f"🎉 تم مسح الأصول بنجاح ورصد {len(res_df)} فرصة مطابقة:")
                st.dataframe(res_df, use_container_width=True)
            else:
                st.warning("⚠️ انتهى المسح، ولم يتم رصد إشارات نشطة تطابق الشروط الصارمة في الأصول المحددة حالياً.")

with tab2:
    st.header("📋 إضافة أي صندوق أو سهم محلي/عالمي للقائمة (Expansion Hub)")
    st.write("النظام **غير مقيد** بالقائمة الافتراضية؛ يمكنك كتابة رمز أي صندوق استثماري (مثل صناديق البلاد للذهب أو التكنولوجيا أو الأسهم الأمريكية أو أي صندوق في تداول) وسيتعامل معه النظام فوراً:")
    
    col1, col2 = st.columns(2)
    with col1:
        # مثال للمستخدم: صندوق البلاد للذهب أو أي رمز يضعه
        user_input_ticker = st.text_input("أدخل رمز السهم أو الصندوق بدقة (مثال: GLD, QQQ, أو رمز الصندوق في تاسي):")
        if st.button("➕ إضافة وتوسيع القائمة"):
            if user_input_ticker and user_input_ticker.upper() not in st.session_state["custom_watchlist"]:
                st.session_state["custom_watchlist"].append(user_input_ticker.upper())
                st.success(f"تم توسيع القائمة وإضافة '{user_input_ticker.upper()}' بنجاح! أصبح جاهزاً للفحص.")
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
            res = requests.post(url, json={"chat_id": tg_chat, "text": "<b>SABRY VISION:</b> تم التوسع بنجاح وتفعيل ربط الصناديق والأسواق العالمية!", "parse_mode": "HTML"}, timeout=5)
            if res.status_code == 200:
                st.success("تم إرسال تنبيه التجربة بنجاح!")
            else:
                st.error("فشل الاتصال، تحقق من صحة البيانات.")
        except Exception as e:
            st.error(f"خطأ في الاتصال: {e}")
