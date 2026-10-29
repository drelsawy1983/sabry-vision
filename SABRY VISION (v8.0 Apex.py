"""
SABRY VISION - Apex Institutional Quant Terminal (v8.0 Master Enterprise Edition)
Part 1: Core System Initialization, Logging, Configuration Dataclasses & Telegram Dispatcher.
"""

import os
import json
import logging
import io
import requests
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

# تهيئة إعدادات صفحة المؤسسة كأول أمر ستريمليت
st.set_page_config(
    page_title="SABRY VISION - Apex Institutional Terminal",
    page_icon="🛡️",
    layout="wide"
)

# تكوين السجلات المؤسسية لمتابعة حالة النظام بدقة
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SabryVisionApexCore")

# الذاكرة المؤقتة للواجهة والقوائم
if "custom_watchlist" not in st.session_state:
    st.session_state["custom_watchlist"] = [
        "AAPL", "MSFT", "2222.SR", "1120.SR", 
        "GLD", "SLV", "QQQ", "SPY", "BTC-USD"
    ]

if "last_scan_results" not in st.session_state:
    st.session_state["last_scan_results"] = pd.DataFrame()

@dataclass
class RiskManagementConfig:
    account_size: float = 100000.0
    risk_pct: float = 0.01
    atr_mult: float = 2.0
    reward_mult: float = 2.5
    min_score: float = 60.0
    min_rvol: float = 1.2
    require_vwap: bool = True

class TelegramEngine:
    @staticmethod
    def send_html_alert(token: str, chat_id: str, message: str) -> bool:
        if not token or not chat_id:
            return False
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.ok
        except Exception as e:
            logger.error(f"Telegram dispatch error: {e}")
            return False
"""
SABRY VISION - Apex Institutional Quant Terminal (v8.0 Master Enterprise Edition)
Part 2: Universal Multi-Market Universe Loader (TASI, US Equities, Commodities, Crypto).
"""

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
        return ["GC=F", "GLD", "IAU", "SI=F", "SLV", "CL=F", "USO", "QQQ", "XLK", "SPY", "SOXX", "ARKK"]

    @staticmethod
    def get_crypto_universe() -> List[str]:
        return ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]

    @staticmethod
    def fetch_sp500_tickers() -> List[str]:
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            df = pd.read_html(io.StringIO(res.text))[0]
            return df["Symbol"].str.replace(".", "-", regex=False).tolist()
        except Exception:
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    @staticmethod
    def fetch_nasdaq100_tickers() -> List[str]:
        try:
            url = "https://en.wikipedia.org/wiki/NASDAQ-100"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            df = pd.read_html(io.StringIO(res.text))[3]
            return df["Ticker"].str.replace(".", "-", regex=False).tolist()
        except Exception:
            return ["AAPL", "MSFT", "TSLA", "AMD"]

    @classmethod
    def get_full_us_universe(cls) -> List[str]:
        return sorted(list(set(cls.fetch_sp500_tickers() + cls.fetch_nasdaq100_tickers())))
"""
SABRY VISION - Apex Institutional Quant Terminal (v8.0 Master Enterprise Edition)
Part 3: Unified Data Provider with Robust MultiIndex Handling & Live Tick Injection.
"""

class UnifiedDataProvider:
    @staticmethod
    def fetch_raw_ohlcv(symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
            if df is None or df.empty:
                return pd.DataFrame()
            
            # معالجة أبعاد الـ MultiIndex إن وجدت لمنع أي أخطاء برمجية
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            if not all(col in df.columns for col in required_cols):
                return pd.DataFrame()
                
            df = df.rename(columns={
                "Open": "open", 
                "High": "high", 
                "Low": "low", 
                "Close": "close", 
                "Volume": "volume"
            })
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            
            if df.empty or len(df) < 30:
                return pd.DataFrame()

            # محرك حقن الأسعار الحية (Live Tick Injection Engine)
            try:
                ticker_obj = yf.Ticker(symbol)
                fast_info = getattr(ticker_obj, 'fast_info', None)
                live_price = fast_info.get('last_price', None) if fast_info else None
                if live_price and live_price > 0:
                    df.iloc[-1, df.columns.get_loc('close')] = float(live_price)
                    if float(live_price) > df.iloc[-1]['high']:
                        df.iloc[-1, df.columns.get_loc('high')] = float(live_price)
                    if float(live_price) < df.iloc[-1]['low']:
                        df.iloc[-1, df.columns.get_loc('low')] = float(live_price)
            except Exception:
                pass

            if df.index.tz is not None:
                try:
                    df.index = df.index.tz_convert("UTC").tz_localize(None)
                except Exception:
                    df.index = df.index.tz_localize(None)
                    
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
"""
SABRY VISION - Apex Institutional Quant Terminal (v8.0 Master Enterprise Edition)
Part 4: Apex Institutional Scanner with Anti-Manipulation & Risk-Adjusted Metrics.
"""

class ApexInstitutionalScanner:
    def __init__(self, settings: RiskManagementConfig, active_setups: List[str]):
        self.settings = settings
        self.active_setups = active_setups

    def analyze_asset(self, symbol: str, period: str, interval: str) -> Optional[Dict[str, Any]]:
        try:
            df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, period, interval)
            if df.empty or len(df) < 40:
                return None
                
            f = df.copy()
            f["sma50"] = f["close"].rolling(50).mean()
            f["ema20"] = f["close"].ewm(span=20, adjust=False).mean()
            
            tp = (f["high"] + f["low"] + f["close"]) / 3.0
            f["vwap"] = (tp * f["volume"]).rolling(20).sum() / f["volume"].rolling(20).sum()
            
            tr = np.maximum(
                f["high"] - f["low"],
                np.maximum((f["high"] - f["close"].shift(1)).abs(), (f["low"] - f["close"].shift(1)).abs())
            )
            f["atr14"] = tr.rolling(14).mean()
            
            f["volume_ma20"] = f["volume"].rolling(20).mean()
            f["rvol"] = (f["volume"] / f["volume_ma20"].replace(0, np.nan)).fillna(1.0)
            f["poc"] = tp.rolling(50).mean()
            f["rs_momentum"] = f["close"].pct_change(63)
            
            f["pivot_20"] = f["high"].rolling(20).max().shift(1)
            f["low_20"] = f["low"].rolling(20).min().shift(1)
            
            min_rvol = self.settings.min_rvol
            
            # --- شروط الفلاتر الخارقة ومكافحة التلاعب (Wick & Absorption Filters) ---
            candle_range = f["high"] - f["low"]
            upper_wick = f["high"] - np.maximum(f["close"], f["open"])
            wick_ratio = upper_wick / candle_range.replace(0, np.nan)
            
            # فلتر رفض الفتيلة العلوية الكبيرة (منع فخاص صناع السوق)
            clean_wick_filter = (wick_ratio <= 0.35) | (f["close"] > f["open"])
            
            # صياغة النماذج الاستراتيجية الأربعة بمعايير مؤسسية
            is_breakout = (f["close"] > f["pivot_20"]) & (f["rvol"] >= min_rvol) & (f["close"] > f["open"]) & clean_wick_filter
            is_setup = (f["close"] <= f["pivot_20"]) & (f["close"] >= f["pivot_20"] * 0.96) & (f["rvol"] < 1.2)
            is_retest = (f["close"].shift(1) > f["pivot_20"]) & (f["low"] <= f["poc"] * 1.02) & (f["close"] > f["poc"])
            is_bottom = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"]) & (f["rvol"] >= (min_rvol * 1.1))
            
            f["sig_breakout"] = is_breakout if "BREAKOUT" in self.active_setups else False
            f["sig_setup"] = is_setup if "SETUP" in self.active_setups else False
            f["sig_retest"] = is_retest if "RETEST" in self.active_setups else False
            f["sig_bottom_reversal"] = is_bottom if "BOTTOM_REVERSAL" in self.active_setups else False
            
            if self.settings.require_vwap:
                vwap_mask = f["close"] >= f["vwap"]
                f["sig_breakout"] &= vwap_mask
                f["sig_setup"] &= vwap_mask
                f["sig_retest"] &= vwap_mask
                f["sig_bottom_reversal"] &= vwap_mask

            conditions = [f["sig_breakout"], f["sig_retest"], f["sig_setup"], f["sig_bottom_reversal"]]
            choices = ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"]
            f["signal_type"] = np.select(conditions, choices, default="NONE")
            
            latest = f.iloc[-1]
            if latest["signal_type"] == "NONE":
                return None
                
            rs_s = latest["rs_momentum"] * 30.0 if pd.notna(latest["rs_momentum"]) else 0
            rvol_s = min(latest["rvol"], 3.0) / 3.0 * 40.0
            score = round(max(0, min(100, 50.0 + rs_s + rvol_s)), 1)
            
            if score < self.settings.min_score:
                return None
                
            close_p = latest["close"]
            atr = latest["atr14"]
            if pd.isna(atr) or atr <= 0:
                atr = close_p * 0.02
                
            # حسابات إدارة المخاطر الرأسمالية (Position Sizing & Break-Even Targets)
            stop_price = round(close_p - (self.settings.atr_mult * atr), 2)
            risk_per_share = close_p - stop_price
            
            if risk_per_share <= 0:
                return None
                
            total_risk_dollar = self.settings.account_size * self.settings.risk_pct
            shares_to_buy = int(total_risk_dollar / risk_per_share) if risk_per_share > 0 else 0
            position_value = shares_to_buy * close_p
            target_price = round(close_p + (self.settings.reward_mult * risk_per_share), 2)
            break_even_target = round(close_p + (1.0 * atr), 2)  # هدف تفعيل تأمين نقطة الدخول
            
            return {
                "الرمز / الصندوق": symbol,
                "النموذج": latest["signal_type"],
                "السكور": score,
                "الإغلاق": round(close_p, 2),
                "وقف الخسارة الأولي": stop_price,
                "هدف التعادل (Break-Even)": break_even_target,
                "الهدف الاستثماري": target_price,
                "حجم الأسهم": shares_to_buy,
                "قيمة المركز ($)": round(position_value, 2),
                "RVOL": round(latest["rvol"], 2)
            }
        except Exception:
            return None
"""
SABRY VISION - Apex Institutional Quant Terminal (v8.0 Master Enterprise Edition)
Part 5: Streamlit Master UI Command Center, Multi-Threaded Scanner & Telegram Dispatcher Hub.
"""

# ------------------------------------------------------------------------------
# 6. STREAMLIT MASTER UI COMMAND CENTER & EXECUTION
# ------------------------------------------------------------------------------

st.title("🛡️ SABRY VISION - Apex Institutional Quant Terminal (v8.0)")

st.sidebar.header("🎛️ لوحة القيادة المركزية المؤسسية")

market_mode = st.sidebar.selectbox(
    "اختر نطاق السوق المستهدف (Universal Engine):",
    [
        "القائمة المخصصة (Custom Watchlist)", 
        "السوق السعودي (تاسي - TASI)", 
        "السوق الأمريكي (S&P 500 & Nasdaq 100)", 
        "السلع العالمية وصناديق الذهب (Commodities & ETFs)", 
        "العملات الرقمية (Crypto)"
    ]
)

timeframe = st.sidebar.selectbox("الإطار الزمني للفحص:", ["15m", "1h", "1d"])
period_choice = st.sidebar.selectbox("العمق التاريخي:", ["1mo", "3mo", "6mo"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 النماذج الاستراتيجية المفعلة")
setup_options = ["BREAKOUT", "SETUP", "RETEST", "BOTTOM_REVERSAL"]
selected_setups = st.sidebar.multiselect("اختر النماذج:", setup_options, default=["BREAKOUT", "RETEST"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ إعدادات الفلترة ومكافحة التلاعب")
min_score_input = st.sidebar.slider("الحد الأدنى للسكور:", 40.0, 90.0, 60.0, 5.0)
min_rvol_input = st.sidebar.slider("أدنى معدل حجم تداول (RVOL):", 1.0, 3.0, 1.2, 0.1)
require_vwap_input = st.sidebar.checkbox("تفعيل شرط الـ VWAP الإلزامي", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 محرك إدارة المخاطر وحماية رأس المال")
account_cap = st.sidebar.number_input("إجمالي رأس المال ($)", value=100000.0, step=10000.0)
risk_pct = st.sidebar.slider("نسبة المخاطرة لكل صفقة (%)", 0.5, 3.0, 1.0, 0.5) / 100.0
atr_mult = st.sidebar.slider("مضاعف وقف الـ ATR الأولي", 1.0, 4.0, 2.0, 0.5)
reward_mult = st.sidebar.slider("مضاعف الهدف الاستثماري (Risk/Reward)", 1.5, 5.0, 2.5, 0.5)

current_risk_config = RiskManagementConfig(
    account_size=account_cap,
    risk_pct=risk_pct,
    atr_mult=atr_mult,
    reward_mult=reward_mult,
    min_score=min_score_input,
    min_rvol=min_rvol_input,
    require_vwap=require_vwap_input
)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "🚀 السكانر المؤسسي الحي", 
    "📋 إدارة القائمة المخصصة",
    "⚙️ مركز تنبيهات التليجرام"
])

with tab1:
    st.header("🔍 المسح الذكي المتزامن (الشروط الخارقة + حماية رأس المال)")
    
    if st.button("🚀 بدء المسح المؤسسي الشامل"):
        if not selected_setups:
            st.error("⚠️ يرجى اختيار نموذج تداول واحد على الأقل.")
        else:
            with st.spinner("جاري سحب الأسعار الحية، تطبيق فلاتر الامتصاص والفتائل، وإدارة المخاطر..."):
                scanner = ApexInstitutionalScanner(current_risk_config, selected_setups)
                
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
                max_workers = 10
                
                prog_bar = st.progress(0)
                completed_tasks = 0
                total_tickers = len(tickers)
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_ticker = {
                        executor.submit(scanner.analyze_asset, t, period_choice, timeframe): t 
                        for t in tickers
                    }
                    
                    for future in as_completed(future_to_ticker):
                        completed_tasks += 1
                        try:
                            prog_bar.progress(min(1.0, completed_tasks / total_tickers))
                        except Exception:
                            pass
                        try:
                            res = future.result()
                            if res:
                                results.append(res)
                        except Exception:
                            pass
                            
                prog_bar.empty()
                
                if results:
                    res_df = pd.DataFrame(results).sort_values(by="السكور", ascending=False)
                    st.success(f"🎉 تم مسح الأسواق بنجاح ورصد {len(res_df)} فرصة مؤسسية مطابقة تماماً لمعايير الحماية:")
                    st.dataframe(res_df, use_container_width=True)
                    st.session_state["last_scan_results"] = res_df
                else:
                    st.warning("⚠️ لم يتم رصد إشارات مطابقة لشروط الفلترة الصارمة الحالية.")

with tab2:
    st.header("📋 إدارة القائمة المخصصة للأصول (Expansion Hub)")
    user_input_ticker = st.text_input("أضف رمز سهم أو صندوق (مثال: GLD, QQQ, AAPL أو صندوق محلي):")
    if st.button("➕ إضافة الرمز للقائمة"):
        if user_input_ticker and user_input_ticker.upper() not in st.session_state["custom_watchlist"]:
            st.session_state["custom_watchlist"].append(user_input_ticker.upper())
            st.success(f"تم إضافة {user_input_ticker.upper()} بنجاح!")
            st.rerun()
    st.write(st.session_state["custom_watchlist"])

with tab3:
    st.header("⚙️ إعدادات تليجرام وإرسال التقارير الآلية")
    tg_token = st.text_input("Telegram Bot Token", type="password")
    tg_chat = st.text_input("Telegram Chat ID")
    
    if st.button("📤 إرسال تقرير الفرص المكتشفة عبر تليجرام"):
        if not tg_token or not tg_chat:
            st.error("⚠️ يرجى إدخال بيانات تليجرام أولاً.")
        elif st.session_state["last_scan_results"].empty:
            st.warning("⚠️ لا توجد نتائج مسح حديثة لإرسالها.")
        else:
            df_res = st.session_state["last_scan_results"]
            msg = f"🛡️ <b>SABRY VISION - Apex Institutional Report</b>\nعدد الفرص المؤكدة: <code>{len(df_res)}</code>\n\n"
            for r in df_res.head(5).itertuples(index=False):
                d = r._asdict()
                msg += f"📌 <b>{d.get('الرمز / الصندوق')}</b> | نموذج: <code>{d.get('النموذج')}</code> | سكور: <b>{d.get('السكور')}</b>\n"
            
            success = TelegramEngine.send_html_alert(tg_token, tg_chat, msg)
            if success:
                st.success("🎉 تم إرسال التقرير بنجاح عبر تليجرام!")
            else:
                st.error("❌ فشل إرسال الرسالة، تحقق من صحة بيانات التليجرام.")
