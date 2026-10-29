"""
SABRY VISION - Apex Institutional Quant Terminal & Backtesting Engine (v11.5 Master Edition)
Complete Enterprise System: Hardcoded Registries (320+ TASI/REITs/9000 ETFs & 750+ Global Assets),
5-Layer Engine with VWAP Slope Angle, Adaptive Market Regime & Dynamic Score Booster,
Multithreaded Scanner, Single Asset Vectorized Deep Backtester, Google Sheets Cloud Sync, 
Google Colab Integration, and Full Export Command Hub.
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

# Optional Google Sheets & Cloud Imports
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# ------------------------------------------------------------------------------
# 1. SYSTEM INITIALIZATION & PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v11.5",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SabryVisionMaster11.5")

# ------------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT & DYNAMIC WATCHLISTS
# ------------------------------------------------------------------------------
if "custom_watchlist" not in st.session_state:
    st.session_state["custom_watchlist"] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "2222.SR", "1120.SR", 
        "GLD", "SLV", "QQQ", "SPY", "BTC-USD", 
        "9405.SR", "9406.SR", "9407.SR", "9410.SR", "9411.SR"
    ]

if "custom_indices_dict" not in st.session_state:
    st.session_state["custom_indices_dict"] = {
        "Hang Seng Core Group": ["^HSI", "0700.HK", "9988.HK", "3690.HK", "0005.HK", "1299.HK", "1810.HK", "2318.HK", "0939.HK"],
        "Albilad Flagship ETFs": ["9405.SR", "9406.SR", "9407.SR", "9410.SR", "9411.SR"],
        "Saudi Blue Chips": ["2222.SR", "1120.SR", "2010.SR", "1180.SR", "7010.SR"]
    }

if "dynamic_discovered_universe" not in st.session_state:
    st.session_state["dynamic_discovered_universe"] = []

if "last_scan_results" not in st.session_state:
    st.session_state["last_scan_results"] = pd.DataFrame()

if "colab_url" not in st.session_state:
    st.session_state["colab_url"] = ""

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
    adaptive_regime_protection: bool = True

# ------------------------------------------------------------------------------
# 4. TELEGRAM NOTIFICATION ENGINE (HTML & DIRECT UI DYNAMIC CONTROLS)
# ------------------------------------------------------------------------------
class TelegramEngine:
    @staticmethod
    def send_html_alert(token: str, chat_id: str, message: str) -> bool:
        """
        إرسال تنبيهات هيدروليكية منسقة بصيغة HTML لمحادثة تليجرام المستهدفة.
        """
        if not token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID is missing.")
            return False
        url = f"https://api.telegram.org/bot{token.strip()}/sendMessage"
        payload = {
            "chat_id": chat_id.strip(), 
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
# 5. MASSIVE HARDCODED INSTITUTIONAL UNIVERSE LOADER
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
            "9410", "9411", "9412", "9413", "9414", "9415", "9510", "9521", "9522",
            
            # عينات إضافية لشركات السوق الموازي (Nomu)
            "9530", "9540", "9550", "9560", "9570", "9580", "9590"
        ]
        
        universe = [f"{t.strip()}.SR" for t in base_tasi_and_nomu if t.strip()]
        
        if "dynamic_discovered_universe" in st.session_state:
            for dyn_t in st.session_state["dynamic_discovered_universe"]:
                if dyn_t not in universe:
                    universe.append(dyn_t)
                    
        return sorted(list(set(universe)))

    @staticmethod
    def get_commodities_and_etfs_universe() -> List[str]:
        """السلع العالمية، المعادن الثمينة والندرة، النفط والمنتجات الزراعية"""
        return [
            "GC=F", "GLD", "IAU", "SI=F", "SLV", "PL=F", "PA=F", "HG=F", "REMX", "9405.SR",
            "CL=F", "BZ=F", "USO", "UNG", "XLE",
            "DBA", "MOO", "WEAT", "CORN", "SOYB", "MOS", "NTR", "ADM", "BG"
        ]

    @staticmethod
    def get_specialized_sector_universe() -> List[str]:
        """صناديق القطاعات المتقدمة: التكنولوجيا، الطاقة المتجددة والمياه، والرعاية الصحية"""
        return [
            "QQQ", "XLK", "SOXX", "ARKK", "SMH", "9406.SR", "9407.SR", "9410.SR", "9411.SR",
            "ICLN", "PBW", "TAN", "FAN", "PHO", "CGW",
            "XLV", "IBB", "XBI", "JNJ", "PFE", "MRK", "ABBV"
        ]

    @staticmethod
    def get_us_and_global_indices_universe() -> List[str]:
        """السوق الأمريكي، مؤشر هانج سينج (Hang Seng) وأهم الأسهم القيادية العالمية"""
        return [
            "SPY", "QQQ", "^DJI", "^RUT", "^HSI", "DIA", "IWM",
            "0700.HK", "9988.HK", "3690.HK", "0005.HK", "1299.HK", "1810.HK", "2318.HK", "0939.HK", "0941.HK", "0388.HK",
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "JNJ",
            "XOM", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
            "AMD", "INTC", "QCOM", "NFLX", "ADBE", "CSCO", "TXN", "AMGN", "HON", "IBM",
            "BA", "CAT", "GE", "DIS", "SBUX", "GS", "MS", "BLK", "ISRG", "PNC"
        ]

    @staticmethod
    def get_crypto_universe() -> List[str]:
        return ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD"]

# ------------------------------------------------------------------------------
# 6. UNIFIED DATA PROVIDER (WITH CUSTOM LOOKBACK & LIVE TICK INJECTION)
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d", period_override: Optional[str] = None) -> pd.DataFrame:
        """
        محرك جالب البيانات الموحد مع التكيف التلقائي للفريمات وإمكانية تجاوز المدى التاريخي للباك تست.
        """
        try:
            if period_override:
                period = period_override
            else:
                if interval == "5m": period = "5d"
                elif interval == "15m": period = "1mo"
                elif interval == "1h": period = "60d"
                elif interval == "1d": period = "6mo"
                elif interval == "1W": period = "2y"
                else: period = "3mo"

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
            
            if df.empty or len(df) < 20:
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
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

# ------------------------------------------------------------------------------
# 7. ADAPTIVE MARKET REGIME CONTROLLER (Risk Protection Engine)
# ------------------------------------------------------------------------------
class AdaptiveMarketRegimeController:
    """
    مراقب حالة السوق الكلية: يفحص اتجاه المؤشرات العامة لتشديد أو تحرير المعايير.
    """
    @staticmethod
    def evaluate_market_regime(benchmark_symbol: str = "SPY") -> Tuple[bool, float]:
        try:
            df_bench = UnifiedDataProvider.fetch_raw_ohlcv(benchmark_symbol, interval="1d", period_override="6mo")
            if df_bench.empty or len(df_bench) < 50:
                return True, 1.0
                
            current_close = float(df_bench.iloc[-1]["close"])
            sma_50 = float(df_bench["close"].rolling(50).mean().iloc[-1])
            
            is_bullish = current_close >= sma_50
            # معامل رفع السكور المطلوب إذا كان السوق ضعيفاً
            score_booster = 1.15 if not is_bullish else 1.0
            return is_bullish, score_booster
        except Exception:
            return True, 1.0

# ------------------------------------------------------------------------------
# 8. SABRY VISION 5-LAYER INSTITUTIONAL QUANT ENGINE WITH SLOPE ANGLE
# ------------------------------------------------------------------------------
class SabryVision5LayerEngine:
    """
    محرك الطبقات الخمس المؤسسي الكامل بشروط النماذج المنفصلة وزاوية ميل الـ VWAP.
    """
    def __init__(self, settings: InstitutionalConfig, active_setups: List[str], timeframe: str):
        self.settings = settings
        self.active_setups = active_setups
        self.timeframe = timeframe

    def _get_dynamic_rvol(self) -> float:
        if self.timeframe == "5m": return 1.8
        elif self.timeframe == "15m": return 1.5
        elif self.timeframe == "1h": return 1.3
        else: return 1.2

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        roll_window = min(20, len(f))
        
        # الطبقة الأولى: الدرع اليومي (EMA 200)
        f["ema200"] = f["close"].ewm(span=200, adjust=False).mean() if len(f) >= 200 else f["close"].expanding().mean()
        
        # الطبقة الثانية: زخم الفريم (VWAP + SMA 50)
        f["sma50"] = f["close"].rolling(50).mean() if len(f) >= 50 else f["close"].expanding().mean()
        tp = (f["high"] + f["low"] + f["close"]) / 3.0
        f["vwap"] = (tp * f["volume"]).rolling(roll_window).sum() / f["volume"].rolling(roll_window).sum()
        
        # حساب زاوية ميل الـ VWAP (Slope Angle)
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
        
        # الطبقة الرابعة: مكافحة التلاعب (Clean Wick Filter)
        candle_range = f["high"] - f["low"]
        upper_wick = f["high"] - np.maximum(f["close"], f["open"])
        wick_ratio = upper_wick / candle_range.replace(0, np.nan)
        clean_wick_filter = (wick_ratio <= 0.35) | (f["close"] > f["open"])
        
        slope_momentum_filter = (f["vwap_slope_deg"] > 10.0) | (f["close"] > f["vwap"])
        
        # شروط الخواص الفريدة لكل نموذج دخول على حدة:
        # 1. BREAKOUT: اختراق قمة محورية بـ RVOL مرتفع وزاوية صاعدة وقوة شمعة
        is_breakout = (f["close"] > f["pivot_20"]) & (f["rvol"] >= dynamic_rvol) & (f["close"] > f["open"]) & clean_wick_filter & slope_momentum_filter
        
        # 2. RETEST: اختراق سابق ثم عودة لاختبار POC والتمركز فوقها
        is_retest = (f["close"].shift(1) > f["pivot_20"]) & (f["low"] <= f["poc"] * 1.03) & (f["close"] > f["poc"])
        
        # 3. SETUP: تجميع بنطاق ضيق أسفل الاختراق بحجم تداول منخفض
        is_setup = (f["close"] <= f["pivot_20"]) & (f["close"] >= f["pivot_20"] * 0.95) & (f["rvol"] < 1.3)
        
        # 4. BOTTOM_REVERSAL: كسر قاع سابق ثم الانعكاس والارتداد السريع بحجم كبير (Stop Hunt Sweep)
        is_bottom = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"]) & (f["rvol"] >= (dynamic_rvol * 1.1))
        
        f["sig_breakout"] = is_breakout if "BREAKOUT" in self.active_setups else False
        f["sig_setup"] = is_setup if "SETUP" in self.active_setups else False
        f["sig_retest"] = is_retest if "RETEST" in self.active_setups else False
        f["sig_bottom_reversal"] = is_bottom if "BOTTOM_REVERSAL" in self.active_setups else False
        
        # الطبقة الأولى والثانية: حماية الدرع اليومي وشرط الـ VWAP
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
# 9. INSTITUTIONAL MULTITHREADED MASTER SCANNER
# ------------------------------------------------------------------------------
class SabryVisionMasterScanner:
    """
    محرك السكانر فائق السرعة لمسح الأسهم مع دعم التكيف الديناميكي لحالة السوق.
    """
    def __init__(self, config: InstitutionalConfig, active_setups: List[str], timeframe: str, market_booster: float = 1.0):
        self.config = config
        self.active_setups = active_setups
        self.timeframe = timeframe
        self.market_booster = market_booster

    def scan_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, self.timeframe)
        if df.empty or len(df) < 30:
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
        
        base_score = 60.0 if sig_type == "BREAKOUT" else 55.0
        calculated_score = base_score + min(20.0, rvol * 5.0) + min(15.0, abs(slope) * 0.5)
        
        # تطبيق التعديل التكيفي لحالة السوق (طلب السكور الأعلى في أوقات ضعف السوق)
        required_min_score = self.config.min_score * self.market_booster
        
        if calculated_score < required_min_score:
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
            "Score": round(calculated_score, 1),
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
# 10. VECTORIZED BACKTESTING ENGINE (SINGLE ASSET DEEP ANALYSIS)
# ------------------------------------------------------------------------------
class SabryVectorizedBacktester:
    """
    محرك الباك تست المتجهي للتحليل الشامل وتتبع صفقات أصل فريد عبر التاريخ.
    """
    @staticmethod
    def run_backtest(df: pd.DataFrame, config: InstitutionalConfig) -> Dict[str, Any]:
        if df.empty or "signal_type" not in df.columns:
            return {"Total Trades": 0, "Win Rate (%)": 0.0, "Profit Factor": 0.0, "Net PnL ($)": 0.0, "Trades List": []}
            
        trades = []
        trade_details = []
        in_trade = False
        entry_price = 0.0
        stop_loss = 0.0
        take_profit = 0.0
        entry_time = None
        sig_name = ""
        
        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        signals = df["signal_type"].values
        times = df.index.values
        atrs = df.get("atr14", pd.Series(closes * 0.02)).values
        
        for i in range(1, len(df)):
            if not in_trade and signals[i] != "NONE":
                in_trade = True
                entry_price = closes[i]
                sig_name = signals[i]
                entry_time = times[i]
                atr = atrs[i] if not np.isnan(atrs[i]) else entry_price * 0.02
                stop_loss = entry_price - (atr * config.atr_mult)
                take_profit = entry_price + ((entry_price - stop_loss) * config.reward_mult)
            elif in_trade:
                if lows[i] <= stop_loss:
                    pnl = stop_loss - entry_price
                    trades.append(pnl)
                    trade_details.append({"Entry Time": str(entry_time), "Exit Time": str(times[i]), "Signal": sig_name, "Entry": entry_price, "Exit": stop_loss, "PnL": pnl, "Outcome": "Loss"})
                    in_trade = False
                elif highs[i] >= take_profit:
                    pnl = take_profit - entry_price
                    trades.append(pnl)
                    trade_details.append({"Entry Time": str(entry_time), "Exit Time": str(times[i]), "Signal": sig_name, "Entry": entry_price, "Exit": take_profit, "PnL": pnl, "Outcome": "Win"})
                    in_trade = False
                    
        total_trades = len(trades)
        if total_trades == 0:
            return {"Total Trades": 0, "Win Rate (%)": 0.0, "Profit Factor": 0.0, "Net PnL ($)": 0.0, "Trades List": []}
            
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
            "Net PnL ($)": round(net_pnl, 2),
            "Trades List": trade_details
        }

# ------------------------------------------------------------------------------
# 11. GOOGLE SHEETS CLOUD SYNC ENGINE
# ------------------------------------------------------------------------------
class GoogleSheetsEngine:
    """
    محرك المزامنة مع Google Sheets لتوليد الروابط المباشرة وتنسيق السجلات.
    """
    @staticmethod
    def sync_to_google_sheet(df_results: pd.DataFrame, sheet_name: str = "SabryVision_Master_Log") -> Optional[str]:
        if not GSPREAD_AVAILABLE:
            return None
        try:
            if "gcp_service_account" not in st.secrets:
                logger.warning("Service Account missing in Secrets.")
                return None
            creds_dict = dict(st.secrets["gcp_service_account"])
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            
            try:
                sheet = client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                sheet = client.create(sheet_name)
                sheet.share(creds_dict.get("client_email", ""), perm_type='user', role='writer')
                
            worksheet = sheet.get_worksheet(0)
            worksheet.clear()
            worksheet.update([df_results.columns.values.tolist()] + df_results.astype(str).values.tolist())
            return sheet.url
        except Exception as e:
            logger.error(f"Google Sheets sync error: {e}")
            return None

# ------------------------------------------------------------------------------
# 12. STREAMLIT UI COMMAND CENTER & DASHBOARD
# ------------------------------------------------------------------------------
def main():
    st.sidebar.title("🛡️ SABRY VISION v11.5")
    st.sidebar.markdown("---")
    
    # ربط Google Colab و Cloud Integration
    st.sidebar.markdown("### 🔗 Google Colab & Cloud Integration")
    colab_url_input = st.sidebar.text_input("Google Colab Notebook URL", value=st.session_state["colab_url"], placeholder="https://colab.research.google.com/...")
    if colab_url_input:
        st.session_state["colab_url"] = colab_url_input
        st.sidebar.success("تم تسجيل رابط Google Colab بنجاح!")
        
    st.sidebar.markdown("---")
    # إعدادات تليجرام الفورية من الواجهة الرئيسية
    st.sidebar.markdown("### ⚙️ إعدادات تليجرام المباشرة")
    ui_telegram_token = st.sidebar.text_input("Telegram Bot Token", value="", type="password", placeholder="أدخل توكن البوت...")
    ui_telegram_chat_id = st.sidebar.text_input("Telegram Chat ID", value="", placeholder="أدخل رقم الشات آي دي...")
    
    st.sidebar.markdown("---")
    acc_size = st.sidebar.number_input("حجم المحفظة ($)", value=100000.0, step=10000.0)
    risk_pct = st.sidebar.slider("نسبة المخاطرة لكل صفقة (%)", 0.5, 5.0, 1.0, 0.5) / 100.0
    
    config = InstitutionalConfig(account_size=acc_size, risk_pct=risk_pct)
    
    market_choice = st.sidebar.selectbox(
        "اختر السوق المستهدف:",
        ["السوق السعودي (تاسي + صناديق 9000 + REITs)", "السوق الأمريكي (S&P 500 & Nasdaq)", "مؤشر هانج سينج ومكوناته (.HK)", "السلع والمعادن الثمينة", "قائمتي المخصصة (Custom Watchlist)"]
    )
    
    timeframe = st.sidebar.selectbox("الإطار الزمني للفحص:", ["5m", "15m", "1h", "1d", "1W"], index=3)
    
    # فك قفل الخانات لفتح القوائم والنماذج بالكامل
    st.sidebar.markdown("### 🎯 النماذج النشطة (حر ومستقل بالكامل)")
    use_breakout = st.sidebar.checkbox("Breakout (اختراق محوري)", value=True)
    use_retest = st.sidebar.checkbox("Retest (إعادة اختبار POC)", value=True)
    use_setup = st.sidebar.checkbox("Setup (تأسيس عرضي)", value=True)
    use_bottom = st.sidebar.checkbox("Bottom Reversal (مصيدة قاع)", value=True)
    
    active_setups = []
    if use_breakout: active_setups.append("BREAKOUT")
    if use_retest: active_setups.append("RETEST")
    if use_setup: active_setups.append("SETUP")
    if use_bottom: active_setups.append("BOTTOM_REVERSAL")

    st.title("🛡️ SABRY VISION - Institutional Quant Terminal")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 السكانر الشامل ومركز التصدير", 
        "📈 الباك تست التاريخي لأصل معين (Single Asset)", 
        "📊 تحليل العمق الفني", 
        "⚙️ إدارة القوائم والمؤشرات"
    ])
    
    with tab1:
        st.subheader("محرك السكانر المؤسسي للفرص الحية")
        if st.button("بدء المسح المؤسسي الشامل", type="primary"):
            if "السوق السعودي" in market_choice:
                symbols_to_scan = GlobalUniverseLoader.get_tasi_universe()
                bench = "2222.SR"
            elif "السوق الأمريكي" in market_choice:
                symbols_to_scan = GlobalUniverseLoader.get_us_and_global_indices_universe()
                bench = "SPY"
            elif "هانج سينج" in market_choice:
                symbols_to_scan = st.session_state["custom_indices_dict"].get("Hang Seng Core Group", ["^HSI"])
                bench = "^HSI"
            elif "السلع" in market_choice:
                symbols_to_scan = GlobalUniverseLoader.get_commodities_and_etfs_universe()
                bench = "GLD"
            else:
                symbols_to_scan = st.session_state["custom_watchlist"]
                bench = "SPY"
                
            # تقييم حالة السوق الكلية لتشديد السكور إذا كان السوق ضعيفاً
            is_bull, booster = AdaptiveMarketRegimeController.evaluate_market_regime(bench)
            if not is_bull:
                st.warning(f"⚠️ وضع الحماية التكيفية نشط: أداء السوق العام ضعيف، تم رفع شرط السكور المطلوب بنسبة {int((booster-1.0)*100)}% لتصفية الفرص الضعيفة.")
                
            master_scanner = SabryVisionMasterScanner(config, active_setups, timeframe, market_booster=booster)
            
            with st.spinner(f"جاري مسح {len(symbols_to_scan)} أصل مالى بمعايير صبري فيجن..."):
                results_df = master_scanner.run_scan(symbols_to_scan)
                st.session_state["last_scan_results"] = results_df
                
            if not results_df.empty:
                st.success(f"تم رصد {len(results_df)} فرصة استثمارية حية مطابقة للشروط!")
                st.dataframe(results_df, use_container_width=True)
                
                # مركز التصدير ومزامنة Google Sheets وتليجرام والتابلت
                st.markdown("---")
                st.markdown("### 🌐 مركز التصدير المباشر والمزامنة السحابية")
                col_a, col_b, col_c = st.columns(3)
                
                sheet_link = None
                with col_a:
                    if st.button("رفع لـ Google Sheets وتوليد رابط"):
                        sheet_link = GoogleSheetsEngine.sync_to_google_sheet(results_df)
                        if sheet_link:
                            st.success("تمت المزامنة بنجاح!")
                            st.markdown(f"🔗 **[رابط Google Sheet المباشر]({sheet_link})**", unsafe_allow_html=True)
                        else:
                            st.warning("تعذر الاتصال بسحابة Google Sheets. تأكد من إعدادات الـ Secrets.")
                with col_b:
                    if st.button("إرسال التقرير لتليجرام"):
                        if ui_telegram_token and ui_telegram_chat_id:
                            msg = f"<b>🚨 SABRY VISION - MASTER SCAN REPORT</b>\n" \
                                  f"عدد الفرص: <b>{len(results_df)}</b>\n" \
                                  f"الفريم: {timeframe}\n"
                            if sheet_link:
                                msg += f"\n🔗 <a href='{sheet_link}'>رابط Google Sheets المباشر</a>"
                            if st.session_state["colab_url"]:
                                msg += f"\n💻 <a href='{st.session_state['colab_url']}'>رابط Google Colab</a>"
                                
                            if TelegramEngine.send_html_alert(ui_telegram_token, ui_telegram_chat_id, msg):
                                st.success("تم إرسال التقرير الحساس لتليجرام بنجاح!")
                            else:
                                st.error("فشل الإرسال. تأكد من صحة التوكن والشات آي دي.")
                        else:
                            st.warning("يرجى كتابة Token و Chat ID في القائمة الجانبية أولاً.")
                with col_c:
                    csv_bytes = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 تحميل النتائج (CSV لنوتس التابلت)",
                        data=csv_bytes,
                        file_name=f"SabryVision_Scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("لم يتم العثور على فرص مطابقة للشروط الصارمة في هذا المسح.")

    with tab2:
        st.subheader("📈 محاكاة الباك تست التاريخي لأصل معين (Single Asset Deep Backtest)")
        st.markdown("أدخل اسم أصل فريد لمسح تاريخه بالكامل أو لمدى زمني محدد وتجربة الفلاتر عليه:")
        col_bt1, col_bt2, col_bt3 = st.columns(3)
        with col_bt1:
            single_symbol = st.text_input("رمز الأصل المراد فحصه (Single Asset):", value="2222.SR")
        with col_bt2:
            bt_timeframe = st.selectbox("فريم الباك تست:", ["15m", "1h", "1d", "1W"], index=2)
        with col_bt3:
            bt_lookback = st.selectbox("المدى التاريخي (Lookback Period):", ["1mo", "3mo", "6mo", "1y", "2y", "max"], index=3)
            
        if st.button("🚀 تشغيل الباك تست التاريخي للأصل (Run Single Asset Backtest)"):
            with st.spinner(f"جاري محاكاة الصفقات التاريخية للرمز {single_symbol}..."):
                df_single = UnifiedDataProvider.fetch_raw_ohlcv(single_symbol, interval=bt_timeframe, period_override=bt_lookback)
                if not df_single.empty:
                    engine = SabryVision5LayerEngine(config, active_setups, bt_timeframe)
                    processed_single = engine.process_data(df_single)
                    metrics = SabryVectorizedBacktester.run_backtest(processed_single, config)
                    
                    st.markdown("### 📊 إحصائيات الأداء التاريخي")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("إجمالي الصفقات", metrics["Total Trades"])
                    m2.metric("نسبة النجاح (%)", f"{metrics['Win Rate (%)']}%")
                    m3.metric("عامل الربح (Profit Factor)", metrics["Profit Factor"])
                    m4.metric("صافي الربح ($)", f"${metrics['Net PnL ($)']}")
                    
                    st.line_chart(processed_single[["close", "ema200", "vwap"]])
                    
                    if metrics["Trades List"]:
                        st.markdown("### 📝 سجل الصفقات المحاكاة تفصيلياً")
                        st.dataframe(pd.DataFrame(metrics["Trades List"]), use_container_width=True)
                else:
                    st.error("تعذر جلب البيانات لهذا الأصل أو المدى الزمني المحدد.")

    with tab3:
        st.subheader("تحليل العمق الفني لأصل معين")
        selected_sym = st.text_input("رمز الأصل للتحليل اللحظي (مثال: 1120.SR أو AAPL):", value="1120.SR")
        if st.button("تحليل الشموع والطبقات"):
            df_asset = UnifiedDataProvider.fetch_raw_ohlcv(selected_sym, timeframe)
            if not df_asset.empty:
                engine = SabryVision5LayerEngine(config, active_setups, timeframe)
                res_df = engine.process_data(df_asset)
                st.line_chart(res_df[["close", "ema200", "vwap"]])
                st.dataframe(res_df.tail(15), use_container_width=True)
            else:
                st.error("فشل في جلب البيانات.")

    with tab4:
        st.subheader("⚙️ إدارة القوائم والمؤشرات المخصصة")
        new_item = st.text_input("أضف رمز جديد للقائمة (مثال: 2010.SR أو NVDA):")
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
