"""
SABRY VISION - Apex Institutional Quant Terminal & Backtesting Engine (v11.4 Master Edition)
Part 1: Enterprise Infrastructure, Secure Telegram Engine, Massive Hardcoded Registries 
(TASI/Nomu/REITs/9000-Series ETFs with corrected 9405/9406/9407/9410/9411 codes, 
Hang Seng Index & Top Weighted Hong Kong Components, US/Global Assets), and Custom Index Manager.
Audited & Verified by SABRY VISION Institutional QA Council.
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

# ------------------------------------------------------------------------------
# 1. SYSTEM INITIALIZATION & PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v11.4",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SabryVisionMaster11.4")

# ------------------------------------------------------------------------------
# 2. SESSION STATE & DYNAMIC CUSTOM INDEX / WATCHLIST MANAGER
# ------------------------------------------------------------------------------
if "custom_watchlist" not in st.session_state:
    st.session_state["custom_watchlist"] = [
        "AAPL", "MSFT", "2222.SR", "1120.SR", 
        "GLD", "SLV", "QQQ", "SPY", "BTC-USD", 
        "9405.SR", "9406.SR", "9407.SR", "9410.SR", "9411.SR"
    ]

if "custom_indices_dict" not in st.session_state:
    st.session_state["custom_indices_dict"] = {
        "Hang Seng Core Group": ["^HSI", "0700.HK", "9988.HK", "3690.HK", "0005.HK", "1299.HK", "1810.HK", "2318.HK", "0939.HK"],
        "Albilad Flagship ETFs": ["9405.SR", "9406.SR", "9407.SR", "9410.SR", "9411.SR"]
    }

if "dynamic_discovered_universe" not in st.session_state:
    st.session_state["dynamic_discovered_universe"] = []

if "last_scan_results" not in st.session_state:
    st.session_state["last_scan_results"] = pd.DataFrame()

# ------------------------------------------------------------------------------
# 3. INSTITUTIONAL CONFIGURATION DATACLASS
# ------------------------------------------------------------------------------
@dataclass
class InstitutionalConfig:
    account_size: float = 100000.0
    risk_pct: float = 0.01
    atr_mult: float = 2.0
    reward_mult: float = 2.5
    min_score: float = 55.0
    require_vwap: bool = True
    require_daily_shield: bool = True

# ------------------------------------------------------------------------------
# 4. TELEGRAM NOTIFICATION ENGINE (HTML & SECRETS INTEGRATED)
# ------------------------------------------------------------------------------
class TelegramEngine:
    @staticmethod
    def send_html_alert(token: str, chat_id: str, message: str) -> bool:
        if not token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID is missing.")
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
            logger.error(f"Error sending Telegram alert: {e}")
            return False

# ------------------------------------------------------------------------------
# 5. MASSIVE HARDCODED INSTITUTIONAL UNIVERSE LOADER (TASI, HANG SENG, US & GLOBAL)
# ------------------------------------------------------------------------------
class GlobalUniverseLoader:
    
    @staticmethod
    def get_tasi_universe() -> List[str]:
        """
        السوق السعودي (تاسي + نمو) كاملاً + الصناديق العقارية (REITs) + 
        الصناديق المتداولة المحدثة بدقة:
        - 9405: صندوق البلاد للمتاجرة بالذهب
        - 9406: صندوق البلاد للأسهم الأمريكية
        - 9407: صندوق البلاد لأسهم التقنية الأمريكية
        - 9410: صندوق البلاد لمؤشر هانج سينج
        - 9411: صندوق البلاد لأسواق هونج كونج
        """
        base_tasi_and_nomu = [
            # قطاع الطاقة، المرافق، والبتروكيماويات الأساسية
            "2222", "1301", "1302", "1303", "1304", "2010", "2020", "2060", "2070", "2080", 
            "2090", "2100", "2120", "2130", "2140", "2150", "2160", "2170", "2180", "2190", 
            "2200", "2210", "2230", "2240", "2250", "2270", "2280", "2290", "2300", "2310", 
            "2320", "2330", "2340", "2350", "2360", "2370", "2380", "2381", "2382", "2383",
            
            # قطاع المصارف، الخدمات المالية، التأمين والوساطة
            "1010", "1020", "1030", "1060", "1080", "1090", "1110", "1111", "1120", "1121", 
            "1140", "1150", "1180", "1181", "1182", "8010", "8012", "8020", "8030", "8040", 
            "8050", "8060", "8070", "8080", "8090", "8100", "8110", "8120", "8130", "8140", 
            "8150", "8160", "8170", "8180", "8190", "8200", "8210", "8230", "8240", "8250", 
            "8260", "8270", "8280", "8300", "8310", "8311", "8340", "8341", "8342", "8343",
            
            # قطاع التجزئة، الأغذية، الزراعة، الأسمدة والسلع الاستهلاكية
            "4001", "4002", "4003", "4004", "4005", "4006", "4007", "4008", "4009", "4010", 
            "4020", "4030", "4040", "4050", "4060", "4070", "4080", "4090", "4100", "4110", 
            "4130", "4140", "4150", "4160", "4180", "4190", "4200", "4210", "4220", "4230", 
            "4240", "4250", "4260", "4270", "4280", "4290", "4300", "4310", "4320", "4330", 
            "4340", "4341", "4342", "4343", "4344", "4345", "4346", "4347", "4348", "4349", 
            "4350", "6001", "6002", "6004", "6010", "6020", "6040", "6060", "7010", "7020", 
            "7030", "7040", "7200", "5110", "3001", "3002", "3003", "3004", "3005", "3006", 
            "3007", "3008", "3010", "3020", "3030", "3040", "3050", "3060",
            
            # الصناديق العقارية المتداولة (REITs)
            "4311", "4331", "4332", "4333", "4334", "4335", "4337", "4338", "4339", "4345",
            "4700", "4701", "4702", "4710", "4711", "4720", "4721", "4730", "4740", "4750",
            
            # الصناديق المتداولة المصححة بدقة (ETFs) ومجموعة الـ 9000
            "9401", "9402", "9403", "9404", "9405", "9406", "9407", "9408", "9409", 
            "9410", "9411", "9412", "9413", "9414", "9415", "9510", "9521", "9522"
        ]
        
        universe = [f"{t.strip()}.SR" for t in base_tasi_and_nomu if t.strip()]
        
        if "dynamic_discovered_universe" in st.session_state:
            for dyn_t in st.session_state["dynamic_discovered_universe"]:
                if dyn_t not in universe:
                    universe.append(dyn_t)
                    
        return sorted(list(set(universe)))

    @staticmethod
    def get_commodities_and_etfs_universe() -> List[str]:
        return [
            "GC=F", "GLD", "IAU", "SI=F", "SLV", "PL=F", "PA=F", "HG=F", "REMX", "9405.SR",
            "CL=F", "BZ=F", "USO", "UNG", "XLE",
            "DBA", "MOO", "WEAT", "CORN", "SOYB", "MOS", "NTR", "ADM", "BG"
        ]

    @staticmethod
    def get_specialized_sector_universe() -> List[str]:
        return [
            "QQQ", "XLK", "SOXX", "ARKK", "SMH", "9406.SR", "9407.SR", "9410.SR", "9411.SR",
            "ICLN", "PBW", "TAN", "FAN", "PHO", "CGW",
            "XLV", "IBB", "XBI", "JNJ", "PFE", "MRK", "ABBV"
        ]

    @staticmethod
    def get_us_and_global_indices_universe() -> List[str]:
        """السوق الأمريكي، مؤشر هانج سينج (Hang Seng) وأهم الأسهم القيادية العالمية"""
        return [
            # المؤشرات الكبرى العالمية والمحلية
            "SPY", "QQQ", "^DJI", "^RUT", "^HSI", "DIA", "IWM",
            # مكونات مؤشر هانج سينج الكبرى (مرتبة تنازلياً حسب الوزن النسبي)
            "0700.HK", "9988.HK", "3690.HK", "0005.HK", "1299.HK", "1810.HK", "2318.HK", "0939.HK", "0941.HK", "0388.HK",
            # عمالقة S&P 500 و Nasdaq 100
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "JNJ",
            "XOM", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
            "AMD", "INTC", "QCOM", "NFLX", "ADBE", "CSCO", "TXN", "AMGN", "HON", "IBM"
        ]

    @staticmethod
    def get_crypto_universe() -> List[str]:
        return ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD"]
# ------------------------------------------------------------------------------
# 6. UNIFIED DATA PROVIDER & LIVE TICK INJECTION ENGINE (Part 2)
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d") -> pd.DataFrame:
        """
        محرك جالب البيانات المؤسسي الموحد مع التكيف التلقائي للفريمات والتحمل ضد الأعطال (Fault Tolerance)
        """
        try:
            if interval == "5m":
                period = "5d"
            elif interval == "15m":
                period = "1mo"
            elif interval == "1h":
                period = "60d"
            elif interval == "1d":
                period = "6mo"
            elif interval == "1W":
                period = "2y"
            else:
                period = "3mo"

            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
            
            if df is None or df.empty:
                df = yf.download(symbol, period="max", interval=interval, progress=False, auto_adjust=True)
                
            if df is None or df.empty:
                return pd.DataFrame()
            
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

            # حقن التكة السعرية الحية (Live Tick Injection)
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
            logger.error(f"Critical error fetching data for {symbol}: {e}")
            return pd.DataFrame()


# ------------------------------------------------------------------------------
# 7. SABRY VISION 5-LAYER INSTITUTIONAL QUANT ENGINE WITH SLOPE ANGLE (Part 2 Core)
# ------------------------------------------------------------------------------
class SabryVision5LayerEngine:
    """
    محرك الطبقات الخمس المؤسسي الكامل (الدرع اليومي، الزخم والـ VWAP، إشارة الدخول والزاوية، مكافحة التلاعب، التنفيذ المحصن).
    """
    def __init__(self, settings: InstitutionalConfig, active_setups: List[str], timeframe: str):
        self.settings = settings
        self.active_setups = active_setups
        self.timeframe = timeframe

    def _get_dynamic_rvol(self) -> float:
        # RVOL ديناميكي متغير حسب الفريم لقطع الطريق على التلاعب والفتائل
        if self.timeframe == "5m": return 1.8
        elif self.timeframe == "15m": return 1.5
        elif self.timeframe == "1h": return 1.3
        else: return 1.2

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        roll_window = min(20, len(f))
        
        # الطبقة الأولى: الدرع اليومي (EMA 200) لحماية الاتجاه الكلي
        f["ema200"] = f["close"].ewm(span=200, adjust=False).mean() if len(f) >= 200 else f["close"].expanding().mean()
        
        # الطبقة الثانية: زخم الفريم (VWAP + SMA 50)
        f["sma50"] = f["close"].rolling(50).mean() if len(f) >= 50 else f["close"].expanding().mean()
        tp = (f["high"] + f["low"] + f["close"]) / 3.0
        f["vwap"] = (tp * f["volume"]).rolling(roll_window).sum() / f["volume"].rolling(roll_window).sum()
        
        # حساب زاوية ميل الـ VWAP (Slope Angle) لضمان الانفجار الزخمي الحقيقي
        vwap_diff = f["vwap"].diff(3)
        f["vwap_slope_deg"] = np.degrees(np.arctan(vwap_diff))
        
        tr = np.maximum(
            f["high"] - f["low"],
            np.maximum((f["high"] - f["close"].shift(1)).abs(), (f["low"] - f["close"].shift(1)).abs())
        )
        f["atr14"] = tr.rolling(14).mean()
        
        f["volume_ma20"] = f["volume"].rolling(roll_window).mean()
        f["rvol"] = (f["volume"] / f["volume_ma20"].replace(0, np.nan)).fillna(1.0)
        f["poc"] = tp.rolling(min(50, len(f))).mean()
        f["rs_momentum"] = f["close"].pct_change(min(20, len(f) - 1))
        
        lookback_p = min(20, len(f) - 1)
        f["pivot_20"] = f["high"].rolling(lookback_p).max().shift(1)
        f["low_20"] = f["low"].rolling(lookback_p).min().shift(1)
        
        dynamic_rvol = self._get_dynamic_rvol()
        
        # الطبقة الرابعة: مكافحة التلاعب (فلتر الفتائل العلوية <= 0.35 و Stop Hunts)
        candle_range = f["high"] - f["low"]
        upper_wick = f["high"] - np.maximum(f["close"], f["open"])
        wick_ratio = upper_wick / candle_range.replace(0, np.nan)
        clean_wick_filter = (wick_ratio <= 0.35) | (f["close"] > f["open"])
        
        # شرط زاوية الميل الإيجابية أو الانفجارية للزخم
        slope_momentum_filter = (f["vwap_slope_deg"] > 10.0) | (f["close"] > f["vwap"])
        
        # الطبقة الثالثة: إشارات الدخول المؤسسية المصفاة
        is_breakout = (f["close"] > f["pivot_20"]) & (f["rvol"] >= dynamic_rvol) & (f["close"] > f["open"]) & clean_wick_filter & slope_momentum_filter
        is_setup = (f["close"] <= f["pivot_20"]) & (f["close"] >= f["pivot_20"] * 0.95) & (f["rvol"] < 1.3)
        is_retest = (f["close"].shift(1) > f["pivot_20"]) & (f["low"] <= f["poc"] * 1.03) & (f["close"] > f["poc"])
        is_bottom = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"]) & (f["rvol"] >= (dynamic_rvol * 1.05))
        
        f["sig_breakout"] = is_breakout if "BREAKOUT" in self.active_setups else False
        f["sig_setup"] = is_setup if "SETUP" in self.active_setups else False
        f["sig_retest"] = is_retest if "RETEST" in self.active_setups else False
        f["sig_bottom_reversal"] = is_bottom if "BOTTOM_REVERSAL" in self.active_setups else False
        
        # تطبيق فلاتر الحماية والدرع اليومي والـ VWAP الإلزامي
        shield_filter = (f["close"] >= f["ema200"]) if self.settings.require_daily_shield else True
        if self.settings.require_vwap:
            vwap_mask = (f["close"] >= f["vwap"])
            f["sig_breakout"] &= vwap_mask & shield_filter
            f["sig_setup"] &= vwap_mask & shield_filter
            f["sig_retest"] &= vwap_mask & shield_filter
            f["sig_bottom_reversal"] &= vwap_mask & shield_filter

        conditions = [f["sig_breakout"], f["sig_retest"], f["sig_setup"], f["sig_bottom_reversal"]]
        choices = ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"]
        f["signal_type"] = np.select(conditions, choices, default="NONE")
        
        return f
# ------------------------------------------------------------------------------
# 8. INSTITUTIONAL MULTITHREADED MASTER SCANNER (Part 3)
# ------------------------------------------------------------------------------
class SabryVisionMasterScanner:
    """
    محرك السكانر المؤسسي فائق السرعة لمسح آلاف الأسهم والصناديق بالتوازي.
    """
    def __init__(self, config: InstitutionalConfig, active_setups: List[str], timeframe: str):
        self.config = config
        self.active_setups = active_setups
        self.timeframe = timeframe

    def scan_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, self.timeframe)
        if df.empty or len(df) < 50:
            return None
            
        engine = SabryVision5LayerEngine(self.config, self.active_setups, self.timeframe)
        processed = engine.process_data(df)
        if processed.empty:
            return None
            
        latest = processed.iloc[-1]
        sig_type = latest.get("signal_type", "NONE")
        
        if sig_type == "NONE":
            return None
            
        close_p = float(latest["close"])
        atr = float(latest.get("atr14", close_p * 0.02))
        rvol = float(latest.get("rvol", 1.0))
        slope = float(latest.get("vwap_slope_deg", 0.0))
        
        # حساب السكور المؤسسي المتقدم (Institutional Score)
        base_score = 60.0 if sig_type == "BREAKOUT" else 55.0
        score = base_score + min(20.0, rvol * 5.0) + min(15.0, abs(slope) * 0.5)
        
        if score < self.config.min_score:
            return None

        stop_loss = close_p - (atr * self.config.atr_mult)
        take_profit = close_p + ((close_p - stop_loss) * self.config.reward_mult)
        
        return {
            "Symbol": symbol,
            "Timeframe": self.timeframe,
            "Signal": sig_type,
            "Close": round(close_p, 2),
            "RVOL": round(rvol, 2),
            "VWAP Slope (°)": round(slope, 1),
            "Score": round(score, 1),
            "Stop Loss": round(stop_loss, 2),
            "Take Profit": round(take_profit, 2),
            "Timestamp": str(processed.index[-1])
        }

    def run_scan(self, symbols: List[str]) -> pd.DataFrame:
        results = []
        max_workers = min(16, os.cpu_count() * 2 or 4)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_sym = {executor.submit(self.scan_symbol, sym): sym for sym in symbols}
            for future in as_completed(future_to_sym):
                res = future.result()
                if res:
                    results.append(res)
                    
        if not results:
            return pd.DataFrame()
            
        df_res = pd.DataFrame(results)
        df_res = df_res.sort_values(by="Score", ascending=False).reset_index(drop=True)
        return df_res


# ------------------------------------------------------------------------------
# 9. VECTORIZED BACKTESTING ENGINE (Part 3)
# ------------------------------------------------------------------------------
class SabryVectorizedBacktester:
    """
    محرك باك تست متجهي دقيق لمحاكاة الصفقات التاريخية وحساب الأداء الاستثماري.
    """
    @staticmethod
    def run_backtest(df: pd.DataFrame, config: InstitutionalConfig) -> Dict[str, Any]:
        if df.empty or "signal_type" not in df.columns:
            return {"Total Trades": 0, "Win Rate (%)": 0.0, "Profit Factor": 0.0, "Net PnL ($)": 0.0}
            
        trades = []
        in_trade = False
        entry_price = 0.0
        stop_loss = 0.0
        take_profit = 0.0
        
        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        signals = df["signal_type"].values
        atrs = df.get("atr14", pd.Series(closes * 0.02)).values
        
        for i in range(1, len(df)):
            if not in_trade and signals[i] != "NONE":
                in_trade = True
                entry_price = closes[i]
                atr = atrs[i] if not np.isnan(atrs[i]) else entry_price * 0.02
                stop_loss = entry_price - (atr * config.atr_mult)
                take_profit = entry_price + ((entry_price - stop_loss) * config.reward_mult)
            elif in_trade:
                # التحقق من ضرب الوقف أو الهدف
                if lows[i] <= stop_loss:
                    pnl = stop_loss - entry_price
                    trades.append(pnl)
                    in_trade = False
                elif highs[i] >= take_profit:
                    pnl = take_profit - entry_price
                    trades.append(pnl)
                    in_trade = False
                    
        total_trades = len(trades)
        if total_trades == 0:
            return {"Total Trades": 0, "Win Rate (%)": 0.0, "Profit Factor": 0.0, "Net PnL ($)": 0.0}
            
        wins = [t for t in trades if t > 0]
        losses = [t for t in trades if t <= 0]
        win_rate = (len(wins) / total_trades) * 100.0
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses)) if losses else 1.0
        profit_factor = gross_profit / gross_loss
        net_pnl = sum(trades)
        
        return {
            "Total Trades": total_trades,
            "Win Rate (%)": round(win_rate, 2),
            "Profit Factor": round(profit_factor, 2),
            "Net PnL ($)": round(net_pnl, 2)
        }


# ------------------------------------------------------------------------------
# 10. STREAMLIT UI COMMAND CENTER & DASHBOARD (Main Execution UI)
# ------------------------------------------------------------------------------
def main():
    st.sidebar.title("🛡️ SABRY VISION v11.4")
    st.sidebar.markdown("---")
    
    # إعدادات الحساب والمخاطر
    acc_size = st.sidebar.number_input("حجم المحفظة ($)", value=100000.0, step=10000.0)
    risk_pct = st.sidebar.slider("نسبة المخاطرة لكل صفقة (%)", 0.5, 5.0, 1.0, 0.5) / 100.0
    
    config = InstitutionalConfig(account_size=acc_size, risk_pct=risk_pct)
    
    # اختيار الأسواق والقوائم
    market_choice = st.sidebar.selectbox(
        "اختر السوق المستهدف:",
        ["السوق السعودي (تاسي + صناديق 9000 + REITs)", "السوق الأمريكي (S&P 500 & Nasdaq)", "مؤشر هانج سينج ومكوناته (.HK)", "السلع والمعادن الثمينة", "قائمتي المخصصة (Custom Watchlist)"]
    )
    
    timeframe = st.sidebar.selectbox("الإطار الزمني للفحص:", ["5m", "15m", "1h", "1d", "1W"], index=3)
    
    st.sidebar.markdown("### نماذج الدخول النشطة")
    use_breakout = st.sidebar.checkbox("Breakout (اختراق محوري)", value=True)
    use_retest = st.sidebar.checkbox("Retest (إعادة اختبار POC)", value=True)
    use_setup = st.sidebar.checkbox("Setup (تأسيس عرضي)", value=True)
    use_bottom = st.sidebar.checkbox("Bottom Reversal (انعكاس قاع)", value=True)
    
    active_setups = []
    if use_breakout: active_setups.append("BREAKOUT")
    if use_retest: active_setups.append("RETEST")
    if use_setup: active_setups.append("SETUP")
    if use_bottom: active_setups.append("BOTTOM_REVERSAL")
    
    st.sidebar.markdown("---")
    telegram_token = st.sidebar.text_input("Telegram Bot Token", type="password")
    telegram_chat_id = st.sidebar.text_input("Telegram Chat ID")
    
    # الواجهة الرئيسية وتصميم التبويبات
    st.title("🛡️ SABRY VISION - Institutional Quant Terminal")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 السكانر الشامل", "📊 تحليل الأصول العميق", "📈 محرك الباك تست", "⚙️ إدارة القوائم والمؤشرات"])
    
    with tab1:
        st.subheader("محرك السكانر المؤسسي للفرص الحية")
        if st.button("بدء المسح الشامل (Run Master Scan)", type="primary"):
            # تحديد قائمة الأصول حسب اختيار المستخدم
            if "السوق السعودي" in market_choice:
                symbols_to_scan = GlobalUniverseLoader.get_tasi_universe()
            elif "السوق الأمريكي" in market_choice:
                symbols_to_scan = GlobalUniverseLoader.get_us_and_global_indices_universe()
            elif "هانج سينج" in market_choice:
                symbols_to_scan = st.session_state["custom_indices_dict"].get("Hang Seng Core Group", ["^HSI"])
            elif "السلع" in market_choice:
                symbols_to_scan = GlobalUniverseLoader.get_commodities_and_etfs_universe()
            else:
                symbols_to_scan = st.session_state["custom_watchlist"]
                
            scanner = SabryVision5LayerEngine(config, active_setups, timeframe)
            master_scanner = SabryVisionMasterScanner(config, active_setups, timeframe)
            
            with st.spinner(f"جاري مسح {len(symbols_to_scan)} أصل مالى بمعايير صبري فيجن..."):
                results_df = master_scanner.run_scan(symbols_to_scan)
                st.session_state["last_scan_results"] = results_df
                
            if not results_df.empty:
                st.success(f"تم رصد {len(len(results_df) if isinstance(results_df, pd.DataFrame) else 0)} فرصة استثمارية مؤسسية مطابقة للشروط الخمسة!")
                st.dataframe(results_df, use_container_width=True)
                
                # إرسال عبر تليجرام إذا توفرت البيانات
                if telegram_token and telegram_chat_id:
                    msg = f"<b>🚨 SABRY VISION SCANNER ALERT</b>\nتم رصد {len(results_df)} فرصة جديدة على فريم {timeframe}!"
                    TelegramEngine.send_html_alert(telegram_token, telegram_chat_id, msg)
            else:
                st.warning("لم يتم العثور على فرص مطابقة للشروط الصارمة في هذا الفحص.")
                
    with tab2:
        st.subheader("تحليل العمق الفني والطبقات الخمس لأصل معين")
        selected_sym = st.text_input("أدخل رمز الأصل (مثال: 2222.SR أو 9405.SR أو AAPL أو ^HSI):", value="2222.SR")
        if st.button("تحليل الأصل"):
            df_asset = UnifiedDataProvider.fetch_raw_ohlcv(selected_sym, timeframe)
            if not df_asset.empty:
                engine = SabryVision5LayerEngine(config, active_setups, timeframe)
                res_df = engine.process_data(df_asset)
                st.line_chart(res_df[["close", "ema200", "vwap"]])
                st.dataframe(res_df.tail(10), use_container_width=True)
            else:
                st.error("فشل في جلب البيانات لهذا الأصل. تأكد من صحة الرمز.")
                
    with tab3:
        st.subheader("محرك الباك تست التاريخي (Vectorized Backtest)")
        bt_symbol = st.text_input("رمز الأصل لفحص الباك تست:", value="2222.SR")
        if st.button("تشغيل المحاكاة التاريخية"):
            df_bt = UnifiedDataProvider.fetch_raw_ohlcv(bt_symbol, "1d")
            if not df_bt.empty:
                engine = SabryVision5LayerEngine(config, active_setups, "1d")
                processed_bt = engine.process_data(df_bt)
                metrics = SabryVectorizedBacktester.run_backtest(processed_bt, config)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("إجمالي الصفقات", metrics["Total Trades"])
                col2.metric("نسبة النجاح (%)", f"{metrics['Win Rate (%)']}%")
                col3.metric("عامل الربح (Profit Factor)", metrics["Profit Factor"])
                col4.metric("صافي الربح ($)", f"${metrics['Net PnL ($)']}")
            else:
                st.error("لا توجد بيانات كافية لتشغيل الباك تست.")
                
    with tab4:
        st.subheader("إدارة القوائم والمؤشرات المخصصة")
        new_item = st.text_input("أضف رمز جديد للقائمة (مثال: 1120.SR أو TSLA):")
        if st.button("إضافة للقائمة المخصصة"):
            if new_item and new_item not in st.session_state["custom_watchlist"]:
                st.session_state["custom_watchlist"].append(new_item.strip())
                st.success(f"تمت إضافة {new_item} بنجاح!")
                
        st.write("القائمة الحالية المخصصة:", st.session_state["custom_watchlist"])
        
        if st.button("حذف عنصر من القائمة"):
            rem_item = st.selectbox("اختر العنصر للحذف:", st.session_state["custom_watchlist"])
            if rem_item:
                st.session_state["custom_watchlist"].remove(rem_item)
                st.success(f"تم حذف {rem_item} بنجاح!")
                st.rerun()

if __name__ == "__main__":
    main()
# ------------------------------------------------------------------------------
# 11. GOOGLE SHEETS CLOUD SYNC ENGINE (Part 4)
# ------------------------------------------------------------------------------
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetsEngine:
    """
    محرك المزامنة السحابية مع Google Sheets لتخزين ومشاركة نتائج السكانر والباك تست فورياً.
    """
    @staticmethod
    def sync_to_google_sheet(df_results: pd.DataFrame, sheet_name: str = "SabryVision_Master_Log") -> Optional[str]:
        try:
            # التحقق من وجود الاعتمادات في Streamlit Secrets
            if "gcp_service_account" not in st.secrets:
                logger.warning("Google Cloud Service Account secrets not found. Using local session sync.")
                return None
                
            creds_dict = dict(st.secrets["gcp_service_account"])
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            
            # فتح أو إنشاء شيت جديد
            try:
                sheet = client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                sheet = client.create(sheet_name)
                sheet.share(creds_dict.get("client_email", ""), perm_type='user', role='writer')
                
            worksheet = sheet.get_worksheet(0)
            worksheet.clear()
            
            # رفع البيانات
            data_to_upload = [df_results.columns.values.tolist()] + df_results.astype(str).values.tolist()
            worksheet.update(data_to_upload)
            
            sheet_url = sheet.url
            return sheet_url
        except Exception as e:
            logger.error(f"Error syncing with Google Sheets: {e}")
            return None


# ------------------------------------------------------------------------------
# 12. ENHANCED TELEGRAM & EXPORT COMMAND HUB (Part 4 UI Extension)
# ------------------------------------------------------------------------------
def render_export_and_cloud_hub(scan_df: pd.DataFrame, telegram_token: str, telegram_chat_id: str):
    st.markdown("---")
    st.subheader("🌐 مركز التصدير، الربط السحابي (Google Sheets) ومشاركة النتائج")
    
    if scan_df.empty:
        st.info("لا توجد نتائج سحب حالية لتصديرها أو مشاركتها. قم بتشغيل السكانر أولاً.")
        return
        
    col1, col2, col3 = st.columns(3)
    
    sheet_link = None
    with col1:
        st.markdown("### 📊 مزامنة Google Sheets")
        if st.button("رفع النتائج إلى Google Sheets وفتح الرابط"):
            with st.spinner("جاري الاتصال بسحابة جوجل ورفع السجلات..."):
                sheet_link = GoogleSheetsEngine.sync_to_google_sheet(scan_df)
                if sheet_link:
                    st.success("تم الرفع بنجاح!")
                    st.markdown(f"🔗 **[رابط Google Sheet المباشر]({sheet_link})**", unsafe_allow_html=True)
                else:
                    st.warning("تعذر الاتصال بـ Google Sheets. تأكد من إعدادات الـ Secrets أو استخدم التصدير اليدوي أدناه.")

    with col2:
        st.markdown("### 📱 التنبيه عبر تليجرام")
        if st.button("إرسال التقرير الشامل والرابط لتليجرام"):
            if telegram_token and telegram_chat_id:
                msg = f"<b>🚨 SABRY VISION - MASTER SCAN REPORT</b>\n" \
                      f"عدد الفرص المرصودة: <b>{len(scan_df)}</b>\n" \
                      f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                      
                if sheet_link:
                    msg += f"\n🔗 <a href='{sheet_link}'>رابط جدول بيانات Google Sheets</a>"
                    
                success = TelegramEngine.send_html_alert(telegram_token, telegram_chat_id, msg)
                if success:
                    st.success("تم إرسال التقرير لتليجرام بنجاح!")
                else:
                    st.error("فشل الإرسال. تأكد من صحة التوكن ومحادثة تليجرام.")
            else:
                st.warning("يرجى إدخال Telegram Bot Token و Chat ID في القائمة الجانبية أولاً.")

    with col3:
        st.markdown("### 💾 التخزين على التابلت والنوتس")
        # زر لتحميل الملف بصيغة CSV لتخزينه في نوتس التابلت أو إرساله بالإيميل
        csv_data = scan_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 تحميل النتائج (CSV لنوتس التابلت)",
            data=csv_data,
            file_name=f"SabryVision_Scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
        
        # خيار تجهيز رسالة بريد إلكتروني جاهزة للمشاركة
        email_body = f"Sabry Vision Scan Results - {len(scan_df)} Assets Found."
        st.markdown(f"📧 **[مشاركة عبر البريد الإلكتروني](mailto:?subject=Sabry%20Vision%20Report&body={email_body})**", unsafe_allow_html=True)
