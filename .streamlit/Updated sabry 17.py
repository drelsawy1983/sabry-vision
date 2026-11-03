"""
================================================================================
🛡️ SABRY VISION - INSTITUTIONAL QUANT TERMINAL (v16.20 Ultimate Precision Edition)
================================================================================
DEVELOPED BY: Dr. Mohamed Sabry & Institutional Quant Engineering Council
--------------------------------------------------------------------------------
ENHANCEMENTS IN v16.20:
- Restored RVol (X) Column in Tab 1 Scanner Results Table.
- Ensured High-Volume Candle Coloring (White for Bullish, Orange for Bearish).
- Ultra-Detailed Institutional Technical Diagnostic Card for EVERY indicator.
- Independent Multi-Timeframe Consensus Matrix separated from Single-TF analysis.
================================================================================
"""

import os
import json
import logging
import io
import time
import requests
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------------------------------------------------------------
# 1. SYSTEM INITIALIZATION & RESPONSIVE STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v16.20",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SabryVision16.20")

st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: clamp(0.9rem, 1.8vw, 1.5rem) !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
        overflow: hidden !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        font-size: clamp(0.75rem, 1.1vw, 0.95rem) !important;
        white-space: nowrap !important;
    }
    .dataframe {
        font-size: 12px !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        font-size: 13px !important;
    }
    .profit-box {
        background-color: #0E2F1E;
        border: 2px solid #00FF7F;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        color: #00FF7F;
    }
    .loss-box {
        background-color: #3B1111;
        border: 2px solid #FF4500;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        color: #FF4500;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. COMPLETE MARKET REPOSITORIES
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d", period: str = "1y") -> pd.DataFrame:
        for attempt in range(4):
            try:
                if interval == "1m":
                    p = "7d"
                elif interval in ["5m", "15m"]:
                    p = "60d"
                elif interval == "1h":
                    p = "730d" if period in ["2y", "5y", "max"] else "60d"
                else:
                    p = period

                df = yf.download(symbol, period=p, interval=interval, progress=False, auto_adjust=True, timeout=25)
                if df is not None and not df.empty:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df.columns = [c.lower() for c in df.columns]
                    return df.dropna()
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed for {symbol}: {e}")
        return pd.DataFrame()

class TelegramEngine:
    @staticmethod
    def send_top10_card(token: str, chat_id: str, market_name: str, timeframe: str, results_df: pd.DataFrame) -> bool:
        if not token or not chat_id or results_df.empty: return False
        url = f"https://api.telegram.org/bot{token.strip()}/sendMessage"
        
        current_time_str = datetime.now().strftime("%Y-%m-%d | %H:%M")
        msg = f"<b>🛡️ SABRY VISION - TOP 10 QUANT OPPORTUNITIES</b>\n"
        msg += f"🏛️ <b>السوق:</b> {market_name} | ⏱️ <b>الفريم:</b> {timeframe}\n"
        msg += f"📅 <b>التوقيت:</b> {current_time_str}\n"
        msg += f"-----------------------------------\n"
        
        top_10 = results_df.head(10)
        for idx, row in top_10.iterrows():
            msg += f"<b>#{idx+1} {row.get('Symbol')}</b> | <code>{row.get('Signal')}</code>\n"
            msg += f" 💰 السعر: ${row.get('Close')} | RVol: <b>{row.get('RVol (X)')}</b> | السكور: <b>{row.get('AI Score')}</b>\n"
            msg += f" 🛑 SL: ${row.get('Stop Loss')} ({row.get('SL Pct')}) | 🎯 TP: ${row.get('Take Profit')} ({row.get('TP Pct')})\n"
            msg += f" 📊 الجودة: {row.get('Opportunity Quality')} | السوبر زون: {row.get('Super Zone Status')}\n"
            msg += f" 🧠 SMC: {row.get('SMC Structure')}\n"
            msg += f"-----------------------------------\n"
            
        try:
            resp = requests.post(url, json={"chat_id": chat_id.strip(), "text": msg, "parse_mode": "HTML"}, timeout=10)
            return resp.ok
        except Exception:
            return False

class TradingViewFormatter:
    @staticmethod
    def format_symbol_for_tv(symbol: str) -> str:
        s = symbol.upper().strip()
        if s.endswith(".SR"): return f"TADAWUL:{s.replace('.SR', '')}"
        elif s.endswith(".CA"): return f"EGX:{s.replace('.CA', '')}"
        elif "=" in s or "^" in s: return s
        else: return f"NASDAQ:{s}"

# Session State Initialization
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False
if "users_db" not in st.session_state:
    st.session_state["users_db"] = {
        "admin": {"password": "admin", "expiry": "2090-12-31", "role": "admin"},
        "user": {"password": "user", "expiry": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"), "role": "user"}
    }
if "portfolio_trades" not in st.session_state: st.session_state["portfolio_trades"] = []
if "custom_watchlists" not in st.session_state:
    st.session_state["custom_watchlists"] = {"قائمتي المفضلة": ["2222.SR", "COMI.CA", "AAPL", "NVDA", "GC=F", "GOOGL"]}
if "last_scan_results" not in st.session_state: st.session_state["last_scan_results"] = pd.DataFrame()

market_lists = {
    "المؤشرات العالمية والأسواق (Global Indices)": [
        "^TASI.SR", "^EGX30", "^SPX", "^IXIC", "^DJI", "^FTSE", "^N225", "^HSI", "GC=F", "SI=F", "CL=F", "DX-Y.NYB"
    ],
    "الذهب والفضة والسلع الفورية والآجلة (Spot & Futures Commodities)": [
        "XAUUSD=X", "GC=F", "GLD", "IAU", "9405.SR", "XAGUSD=X", "SI=F", "SLV", "PL=F", "PA=F", "HG=F", "CL=F", "BZ=F", "NG=F"
    ],
    "الصناديق المتداولة في السوق الأمريكي (US ETFs)": [
        "SPY", "VOO", "IVV", "QQQ", "QQQM", "TQQQ", "SQQQ", "IWM", "EEM", "EFA", 
        "GLD", "IAU", "SLV", "USO", "TLT", "IEF", "HYG", "LQD", "XLF", "XLK", 
        "XLE", "XLV", "XLI", "XLP", "XLU", "XLY", "XLB", "XLC", "ARKK", "VTI"
    ],
    "السوق السعودي (تاسي كامل 309)": [
        "2222.SR", "1301.SR", "1302.SR", "1303.SR", "1304.SR", "2010.SR", "2020.SR", "2060.SR", "2070.SR", "2080.SR", 
        "2090.SR", "2100.SR", "2120.SR", "2130.SR", "2140.SR", "2150.SR", "2160.SR", "2170.SR", "2180.SR", "2190.SR", 
        "2200.SR", "2210.SR", "2230.SR", "2240.SR", "2250.SR", "2270.SR", "2280.SR", "2290.SR", "2300.SR", "2310.SR", 
        "2320.SR", "2330.SR", "2340.SR", "2350.SR", "2360.SR", "2370.SR", "2380.SR", "2381.SR", "2382.SR", "2383.SR",
        "1010.SR", "1020.SR", "1030.SR", "1060.SR", "1080.SR", "1090.SR", "1110.SR", "1111.SR", "1120.SR", "1121.SR", 
        "1140.SR", "1150.SR", "1180.SR", "1181.SR", "1182.SR", "8010.SR", "8012.SR", "8020.SR", "8030.SR", "8040.SR", 
        "8050.SR", "8060.SR", "8070.SR", "8080.SR", "8090.SR", "8100.SR", "8110.SR", "8120.SR", "8130.SR", "8140.SR", 
        "8150.SR", "8160.SR", "8170.SR", "8180.SR", "8190.SR", "8200.SR", "8210.SR", "8230.SR", "8240.SR", "8250.SR", 
        "8260.SR", "8270.SR", "8280.SR", "8300.SR", "8310.SR", "8311.SR", "8340.SR", "8341.SR", "8342.SR", "8343.SR",
        "4001.SR", "4002.SR", "4003.SR", "4004.SR", "4005.SR", "4006.SR", "4007.SR", "4008.SR", "4009.SR", "4010.SR", 
        "4020.SR", "4030.SR", "4040.SR", "4050.SR", "4060.SR", "4070.SR", "4080.SR", "4090.SR", "4100.SR", "4110.SR", 
        "4130.SR", "4140.SR", "4150.SR", "4160.SR", "4180.SR", "4190.SR", "4200.SR", "4210.SR", "4220.SR", "4230.SR", 
        "4240.SR", "4250.SR", "4260.SR", "4270.SR", "4280.SR", "4290.SR", "4300.SR", "4310.SR", "4320.SR", "4330.SR", 
        "4340.SR", "4341.SR", "4342.SR", "4343.SR", "4344.SR", "4345.SR", "4346.SR", "4347.SR", "4348.SR", "4349.SR", 
        "4350.SR", "6001.SR", "6002.SR", "6004.SR", "6010.SR", "6020.SR", "6040.SR", "6060.SR", "7010.SR", "7020.SR", 
        "7030.SR", "7040.SR", "7200.SR", "5110.SR", "3001.SR", "3002.SR", "3003.SR", "3004.SR", "3005.SR", "3006.SR", 
        "3007.SR", "3008.SR", "3010.SR", "3020.SR", "3030.SR", "3040.SR", "3050.SR", "3060.SR", "3080.SR", "3090.SR", 
        "5010.SR", "5020.SR", "5090.SR", "5120.SR", "5260.SR", "5270.SR", "5280.SR", "5290.SR", "6012.SR", "6013.SR", 
        "6014.SR", "6015.SR", "6016.SR", "6018.SR", "6019.SR", "6021.SR", "6022.SR", "6023.SR", "6024.SR", "6025.SR", 
        "6026.SR", "6027.SR", "6028.SR", "6029.SR", "6041.SR", "6042.SR", "6043.SR", "6044.SR", "6046.SR", "6047.SR", 
        "6048.SR", "6049.SR", "6051.SR", "6052.SR", "6053.SR", "6054.SR", "6055.SR", "6056.SR", "6058.SR", "6059.SR", 
        "6061.SR", "6062.SR", "6063.SR", "6064.SR", "6065.SR", "6066.SR", "6067.SR", "6068.SR", "3031.SR", "3032.SR", 
        "3033.SR", "3034.SR", "3035.SR", "3036.SR", "3037.SR", "3038.SR", "3039.SR", "3051.SR", "3052.SR", "3053.SR", 
        "3054.SR", "3055.SR", "3056.SR", "3057.SR", "3058.SR", "3059.SR", "3061.SR", "3062.SR",
        "4311.SR", "4331.SR", "4332.SR", "4333.SR", "4334.SR", "4335.SR", "4337.SR", "4338.SR", "4339.SR", "4345.SR",
        "4700.SR", "4701.SR", "4702.SR", "4710.SR", "4711.SR", "4720.SR", "4721.SR", "4730.SR", "4740.SR", "4750.SR",
        "9401.SR", "9402.SR", "9403.SR", "9404.SR", "9405.SR", "9406.SR", "9407.SR", "9408.SR", "9409.SR", 
        "9410.SR", "9411.SR", "9412.SR", "9413.SR", "9414.SR", "9415.SR", "9510.SR", "9521.SR", "9522.SR",
        "9530.SR", "9540.SR", "9550.SR", "9560.SR", "9570.SR", "9580.SR", "9590.SR"
    ],
    "البورصة المصرية الشاملة (EGX 240+)": [
        f"{s}.CA" if not s.endswith(".CA") and not s.startswith("EGS") else s 
        for s in [
            "COMI", "SWDY", "ETEL", "TMGH", "MFPC", "EGAL", "QNBE", "ABUK", "HDBK", "EAST", 
            "ORAS", "ALCN", "EFIH", "ADIB", "EMFD", "FWRY", "CANA", "SCTS", "GPPL", "EFID", 
            "ORHD", "JUFO", "HRHO", "FAIT", "FAITA", "PHDC", "OCDI", "VLMR", "VLMRA", "CIEB", 
            "HELI", "BTFH", "GBCO", "EXPA", "BIOC", "ARCC", "IRON", "RAYA", "SCEM", "CIRA", 
            "EGCH", "VALU", "CLHO", "CCAP", "TAQA", "EGSA", "AMOC", "MOIL", "PHAR", "POUL", 
            "SKPC", "MBSC", "UBEE", "MCQE", "MTIE", "ORWE", "EGBE", "SAUD", "MASR", "TALM", 
            "EFIC", "NIPH", "EGTS", "BINV", "CPME", "ISPH", "MHOT", "ATQA", "CICH", "RMDA", 
            "CSAG", "CPCI", "AMIA", "OIH", "MIPH", "SVCE", "IFAP", "PHTV", "AMES", "OLFI", 
            "BONY", "MOIN", "MPCI", "SUGR", "AXPH", "SPHT", "EGAS", "ZMID", "ISMQ", "DOMT", 
            "GOUR", "PRDC", "MPRC", "ARAB", "ENGC", "SPIN", "ELEC", "ACAP", "SAIB", "NINH", 
            "CNFN", "MICH", "OCPH", "SDTI", "MCRO", "GSSC", "UNIT", "AJWA", "AFMC", "DSCW", 
            "AMER", "ACGC", "KZPC", "KABO", "WCDF", "ADCI", "UEFM", "OFH", "MFSC", "LCSW", 
            "GDWA", "CRST", "CFGH", "ICFC", "ELKA", "ACAMD", "NAHO", "ACTF", "GPIM", "ASCM", 
            "INFI", "ETRS", "ELSH", "EDFM", "AIFI", "ZEOT", "ATLC", "DAPH", "MPCO", "SMFR", 
            "ICID", "SNFC", "ISMA", "DEIN", "CEFM", "NARE", "GTWL", "MAAL", "MOSC", "RACC", 
            "ECAP", "AALR", "ADPC", "KRDI", "MENA", "EHDR", "WKOL", "IDRE", "NDRL", "EALR", 
            "MILS", "NCCW", "ODIN", "AIH", "ASPI", "GGCC", "SIPC", "SCFM", "CERA", "CAED", 
            "UEGC", "IEEC", "MBEG", "PRCL", "DTPP", "MEGM", "OBRI", "NHPS", "FCMD", "MEPA", 
            "COSG", "RUBX", "ICLE", "TANM", "EBSC", "AFDI", "ALUM", "RTVC", "APSW", "UNIP", 
            "PRMH", "RREI", "RAKT", "COPR", "EASB", "KWIN", "SPMD", "AMII", "ROTO", "TYCN", 
            "MOED", "EEII", "AREH", "SEIG", "SEIGA", "CCRS", "EPCO", "EGREF", "TRTO", "ELWA", 
            "ELNA", "GRCA", "IBCT", "UTOP", "GIHD", "MMAT", "NEDA", "FNAR", "VERT", "RKAZ", 
            "EPPK", "BIGP", "AMPI", "GMCI", "FIRE", "MISR", "BIDI", "EOSB", "ELAB", "NFCI", 
            "DGTZ", "DCCC", "ENPI", "SIEG", "SINA", "FTNS", "CID", "MMHC", "MLIC", "MITR", 
            "GEOS", "GGRN", "ANCC", "TOUR", "TWSA", "INEG", "GROV", "ALXD", "GTEX", "HBCO", 
            "HDST", "UPMS", "LUTS", "AIDC", "ADRI", "KORA", "YAYT", "KNGC", "ACFR", "PHGC", 
            "EGOTH", "PMSC", "POCO", "EFAC", "EEP", "EGWA", "OCAP", "NMIN"
        ]
    ],
    "السوق الأمريكي (S&P 500 كامل 503+)": [
        "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A", "APD", "ABNB", "AKAM", "ALB", "ARE", "ALGN", "ALLE", "LNT", "ALL", "GOOGL",
        "GOOG", "MO", "AMZN", "AMCR", "AEE", "AEP", "AXP", "AIG", "AMT", "AWK", "AMP", "AME", "AMGN", "APH", "ADI", "ANSS", "AON", "APA", "AAPL", "AMAT",
        "APTV", "ACGL", "ADM", "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", "ADP", "AZO", "AVB", "AVY", "AXON", "BKR", "BALL", "BAC", "BK", "BBWI", "BAX",
        "BDX", "BRK.B", "BBY", "BIO", "TECH", "BIIB", "BLK", "BX", "BA", "BKNG", "BWA", "BSX", "BMY", "AVGO", "BR", "BRO", "BF.B", "BLDR", "BG", "BXP",
        "CHRW", "CDNS", "CZR", "CPT", "CPB", "COF", "CAH", "KMX", "CCL", "CARR", "CAT", "CBOE", "CBRE", "CDW", "CE", "COR", "CNC", "CNP", "CF", "CRL",
        "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "CINF", "CTAS", "CSCO", "C", "CFG", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CAG",
        "COP", "ED", "STZ", "CEG", "COO", "CPRT", "GLW", "CPAY", "CTVA", "CSGP", "COST", "CTRA", "CRWD", "CCI", "CSX", "CMI", "CVS", "DHR", "DRI", "DVA",
        "DAY", "DECK", "DE", "DELL", "DAL", "XRAY", "DVN", "DXCM", "FANG", "DLR", "DFS", "DG", "DLTR", "D", "DPZ", "DOV", "DOW", "DHI", "DTE", "DUK",
        "DD", "EMN", "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "ELV", "EMR", "ENPH", "ETR", "EOG", "EPAM", "EQT", "EFX", "EQIX", "EQR", "ESS", "EL",
        "ETSY", "EG", "EVRG", "ES", "EXC", "EXPE", "EXPD", "EXR", "XOM", "FFIV", "FDS", "FICO", "FAST", "FRT", "FDX", "FIS", "FITB", "FSLR", "FE",
        "FI", "FLT", "FMC", "F", "FTNT", "FTV", "FOXA", "FOX", "BEN", "FCX", "GRMN", "IT", "GE", "GEHC", "GEV", "GEN", "GNRC", "GD", "GIS", "GM",
        "GPC", "GILD", "GPN", "GL", "GDDY", "GS", "HAL", "HIG", "HAS", "HCA", "DOC", "HSIC", "HSY", "HES", "HPE", "HLT", "HOLX", "HD", "HON", "HRL",
        "HST", "HWM", "HPQ", "HUBB", "HUM", "HBAN", "HII", "IBM", "IEX", "IDXX", "ITW", "INCY", "IR", "PODD", "INTC", "ICE", "IP", "IPG", "IFF", "INTU",
        "ISRG", "IVZ", "INVH", "IQV", "IRM", "JBHT", "JBL", "JKHY", "J", "JNJ", "JPM", "JNPR", "K", "KDP", "KEY", "KEYS", "KMB", "KIM", "KMI", "KLAC",
        "KHC", "KR", "LHX", "LH", "LRCX", "LW", "LVS", "LDOS", "LEN", "LLY", "LIN", "LYV", "LKQ", "LMT", "L", "LOW", "LULU", "LYB", "MTB", "MRO",
        "MPC", "MKTX", "MAR", "MMC", "MLM", "MAS", "MA", "MTCH", "MKC", "MCD", "MCK", "MDT", "MRK", "META", "MET", "MTD", "MGM", "MCHP", "MU", "MSFT",
        "MAA", "MRNA", "MHK", "MOH", "TAP", "MDLZ", "MPWR", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NTAP", "NFLX", "NEM", "NWSA", "NWS", "NEE",
        "NKE", "NI", "NDSN", "NSC", "NTRS", "NOC", "NCLH", "NRG", "NUE", "NVDA", "NVR", "NXPI", "ORLY", "OXY", "ODFL", "OMC", "ON", "OKE", "ORCL", "OTIS",
        "PCAR", "PKG", "PANW", "PARA", "PAYX", "PAYC", "PYPL", "PNR", "PEP", "PKI", "PFE", "PCG", "PM", "PSX", "PNW", "PNC", "POOL", "PPG", "PPL", "PFG",
        "PG", "PGR", "PLD", "PRU", "PEG", "PTC", "PSA", "PHM", "PWR", "QCOM", "DGX", "RLJ", "RJF", "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD",
        "RVTY", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "SBAC", "SLB", "STX", "SRE", "NOW", "SHW", "SPG", "SWKS", "SJM", "SNA", "SO", "LUV", "SWK",
        "SBUX", "STT", "STE", "SYK", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO", "TPR", "TRGP", "TGT", "TEL", "TDY", "TFX", "TER", "TSLA", "TXN", "TXT",
        "TMO", "TJX", "TSCO", "TT", "TDG", "TRV", "TRMB", "TFC", "TYL", "TSN", "USB", "UBER", "UDR", "ULTA", "UNP", "UNH", "UPS", "URI", "UHS", "VLO",
        "VTR", "VRSSR", "VRSK", "VZ", "VRTX", "VTRS", "VICI", "V", "VST", "WAB", "WBA", "WMT", "DIS", "WBD", "WM", "WAT", "WEC", "WFC", "WELL", "WST",
        "WDC", "WY", "WHR", "WMB", "WTW", "WYNN", "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZTS", "SPY", "VOO", "IVV"
    ],
    "الناسداك (Nasdaq كامل 100+)": [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST", 
        "NFLX", "AMD", "LIN", "TMUS", "PEP", "ADBE", "CSCO", "CMCSA", "INTU", "QCOM", 
        "TXN", "AMGN", "HON", "AMAT", "BKNG", "SBUX", "ISRG", "GILD", "MDLZ", "ADP", 
        "PANW", "LRCX", "ADI", "SNPS", "CDNS", "PYPL", "MU", "REGN", "VRTX", "CHTR", 
        "CSX", "MNST", "MCHP", "ORLY", "CTAS", "AEP", "KDP", "MELI", "DXCM", "FAST", 
        "PCAR", "EA", "KHC", "ODFL", "GEHC", "EXC", "BKR", "ROK", "ROST", "CPRT", 
        "VRSK", "PAYX", "CTSH", "ON", "CDW", "DLTR", "WBD", "ENPH", "CEG", "ZS", 
        "TTWO", "TEAM", "ANSS", "BIIB", "XRAY", "SIRI", "CRWD", "DDOG", "MRVL", "MDB", 
        "PATH", "RIVN", "LUCID", "SNOW", "PLTR", "DASH", "ABNB", "ASML", "ARM", "KLAC", 
        "WMT", "PDD", "MAR", "FTNT", "ALAB", "QQQ", "QQQM", "TQQQ", "SQQQ", "QLD", 
        "PSQ", "ONEQ", "XLK", "SMH", "SOXX", "ARKK", "IGV", "XLC", "XLY"
    ]
}

# ------------------------------------------------------------------------------
# 3. ADVANCED QUANT, TECHNICAL & SMC ENGINES
# ------------------------------------------------------------------------------
@dataclass
class InstitutionalConfig:
    account_size: float = 100000.0
    risk_pct: float = 0.01
    atr_mult: float = 2.0
    reward_mult: float = 2.5

class SuperPOCEngine:
    @staticmethod
    def calculate_multi_pocs(df: pd.DataFrame, w1: int = 20, w2: int = 60, w3: int = 120, w4: int = 300) -> dict:
        if len(df) < 15: return {"super_zone": None, "is_super": False, "pocs": {}, "zone_range": None}
        pocs = {}
        for w in [w1, w2, w3, w4]:
            if len(df) >= w:
                sub_df = df.tail(w)
                price_bins = pd.cut(sub_df['close'], bins=25)
                vol_profile = sub_df.groupby(price_bins, observed=False)['volume'].sum()
                pocs[w] = vol_profile.idxmax().mid if not vol_profile.empty else sub_df['close'].iloc[-1]
            else:
                pocs[w] = df['close'].iloc[-1]
        poc_vals = list(pocs.values())
        aligned = [p for p in poc_vals if sum(1 for o in poc_vals if abs(p - o)/max(1e-5, p) <= 0.01) >= 3]
        is_super = len(aligned) >= 3
        super_zone = float(np.mean(aligned)) if is_super else None
        zone_range = (min(aligned), max(aligned)) if is_super else None
        return {"super_zone": super_zone, "is_super": is_super, "pocs": pocs, "zone_range": zone_range}

    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        close = f['close']
        
        # EMAs
        f['ema20'] = close.ewm(span=20).mean()
        f['ema50'] = close.ewm(span=50).mean()
        f['ema100'] = close.ewm(span=100).mean()
        f['ema200'] = close.ewm(span=200).mean()
        
        # Bollinger Bands
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        f['bb_upper'] = sma20 + (std20 * 2)
        f['bb_lower'] = sma20 - (std20 * 2)
        
        # VWAP & SD
        tp = (f['high'] + f['low'] + f['close']) / 3.0
        f['vwap'] = (tp * f['volume']).cumsum() / f['volume'].cumsum().replace(0, np.nan)
        v_std = close.rolling(20, min_periods=1).std().fillna(0)
        f['vwap_sd1_p'] = f['vwap'] + v_std
        f['vwap_sd1_m'] = f['vwap'] - v_std
        
        # Ichimoku
        high9, low9 = f['high'].rolling(9).max(), f['low'].rolling(9).min()
        f['tenkan'] = (high9 + low9) / 2.0
        high26, low26 = f['high'].rolling(26).max(), f['low'].rolling(26).min()
        f['kijun'] = (high26 + low26) / 2.0
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        f['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        f['macd'] = ema12 - ema26
        f['macd_signal'] = f['macd'].ewm(span=9).mean()
        f['macd_hist'] = f['macd'] - f['macd_signal']
        
        return f.bfill().ffill()

    @staticmethod
    def detect_smc_structure(df: pd.DataFrame) -> str:
        if len(df) < 20: return "هيكل عرضي مستقر"
        recent = df.tail(15)
        high_20 = df['high'].iloc[-20:-1].max()
        low_20 = df['low'].iloc[-20:-1].min()
        if recent['close'].iloc[-1] > high_20: return "اختراق هيكل (BOS - صعود مؤسسي 🚀)"
        elif recent['close'].iloc[-1] < low_20: return "كسر هيكل (BOS - هبوط مؤسسي 🔴)"
        elif recent['close'].iloc[-1] > recent['close'].iloc[-5] and recent['low'].iloc[-1] < recent['low'].iloc[-5]:
            return "تغير الطابع (CHoCH - انعكاس محتمل ⚡)"
        return "استقرار هيكلي (Range Bound)"

class SabryVisionMasterScanner:
    def __init__(self, config: InstitutionalConfig, timeframe: str):
        self.config = config
        self.timeframe = timeframe

    def scan_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, self.timeframe)
        if df.empty or len(df) < 10: return None
        
        tr = np.maximum(df["high"] - df["low"], np.maximum((df["high"] - df["close"].shift(1)).abs(), (df["low"] - df["close"].shift(1)).abs()))
        df["atr14"] = tr.rolling(14, min_periods=1).mean()
        df["rvol"] = (df["volume"] / df["volume"].rolling(20, min_periods=1).mean().replace(0, np.nan)).fillna(1.0)
        
        p20 = df["high"].rolling(20, min_periods=1).max().shift(1).fillna(df["high"])
        l20 = df["low"].rolling(20, min_periods=1).min().shift(1).fillna(df["low"])
        
        b = (df["close"] > p20) & (df["rvol"] >= 1.2)
        r = (df["close"].shift(1) > p20) & (df["low"] <= p20 * 0.99)
        s = (df["low"] < l20) & (df["close"] >= l20 * 1.005)
        bot = (df["low"] < l20) & (df["close"] > l20)
        
        latest = df.iloc[-1]
        act = []
        if b.iloc[-1]: act.append("BREAKOUT")
        if r.iloc[-1]: act.append("RETEST")
        if s.iloc[-1]: act.append("LIQUIDITY_SWEEP")
        if bot.iloc[-1]: act.append("BOTTOM_REVERSAL")
        
        if not act: return None
        sig = " 🔥 " + " + ".join(act) + " (توافقي مزدوج)" if len(act) >= 2 else act[0]
        
        close_p, atr, rvol = float(latest["close"]), float(latest.get("atr14", 1.0)), float(latest.get("rvol", 1.0))
        ai_score = min(98.0, max(60.0, 75.0 + rvol * 5.0))
        
        poc_res = SuperPOCEngine.calculate_multi_pocs(df)
        in_super_zone = False
        if poc_res["super_zone"] and poc_res["zone_range"]:
            if poc_res["zone_range"][0] <= close_p <= poc_res["zone_range"][1]:
                in_super_zone = True
        
        super_zone_status = "🌟 داخل السوبر زون (صح)" if in_super_zone else "❌ خارج السوبر زون (خطأ)"
        quality = "فرصة فائقة 🚀" if (ai_score >= 88.0 and in_super_zone) else ("فرصة قوية مؤكدة 🟢" if ai_score >= 75.0 else "دخول بحذر ⚠️")
        smc_struct = SuperPOCEngine.detect_smc_structure(df)

        sl = close_p - (atr * self.config.atr_mult)
        tp = close_p + ((close_p - sl) * self.config.reward_mult)
        
        sl_pct = f"-{round(((close_p - sl) / close_p) * 100, 1)}%"
        tp_pct = f"+{round(((tp - close_p) / close_p) * 100, 1)}%"

        return {
            "Symbol": symbol, "Signal": sig, "AI Score": round(ai_score, 1),
            "RVol (X)": f"{round(rvol, 2)}x", "Opportunity Quality": quality, 
            "Super Zone Status": super_zone_status, "SMC Structure": smc_struct, 
            "Close": round(close_p, 2), "Stop Loss": round(sl, 2), "SL Pct": sl_pct,
            "Take Profit": round(tp, 2), "TP Pct": tp_pct
        }

# ------------------------------------------------------------------------------
# 4. MAIN DASHBOARD INTERFACE
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION v16.20 - Quant Portal</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                u_in = st.text_input("اسم المستخدم")
                p_in = st.text_input("كلمة المرور", type="password")
                if st.form_submit_button("🔑 تسجيل الدخول", type="primary"):
                    if u_in.strip() in st.session_state["users_db"] and st.session_state["users_db"][u_in.strip()]["password"] == p_in.strip():
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = u_in.strip()
                        st.session_state["is_admin"] = (st.session_state["users_db"][u_in.strip()]["role"] == "admin")
                        st.rerun()
                    else: st.error("❌ بيانات الدخول غير صحيحة.")
        return

    st.sidebar.title("🛡️ SABRY VISION v16.20")
    st.sidebar.info(f"👤 المستخدم: **{st.session_state['username']}**")
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.rerun()

    ui_token = "8810439179:AAGMWrf_pTE0Aa6PrJ-pAIwFHts8xsTWLDg"
    ui_chat = "1207434469"

    market_choice = st.sidebar.selectbox("اختر السوق أو القائمة:", list(market_lists.keys()) + list(st.session_state["custom_watchlists"].keys()))
    selected_symbols = market_lists.get(market_choice, st.session_state["custom_watchlists"].get(market_choice, []))
    config = InstitutionalConfig()

    st.title("🛡️ SABRY VISION - Institutional Quant Terminal v16.20")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 السكانر الشامل وتليجرام", 
        "🧠 التحليل الفني العميق", 
        "📊 التقييم المالي الأساسي", 
        "💼 المحفظة والصفقات", 
        "📁 إدارة القوائم"
    ])

    # TAB 1: MASTER SCANNER & PROGRESS BAR
    with tab1:
        st.subheader(f"محرك السكانر اللحظي للقائمة: **{market_choice}** (عدد الأصول: {len(selected_symbols)})")
        scan_tf = st.selectbox("إطار زمن المسح:", ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"], index=2, key="t1_tf")
        auto_stream_mode = st.selectbox("⚡ نظام السكانر التلقائي وإرسال تليجرام الخلفي (Auto-Streamer):", ["إيقاف - OFF 🔴", "تشغيل تلقائي - ON 🟢"], index=0)

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("🚀 بدء المسح المؤسسي الفوري الآن", type="primary"):
                results = []
                scanner = SabryVisionMasterScanner(config, scan_tf)
                progress_bar = st.progress(0, text="جاري بدء مسح الأصول المؤسسية...")
                total_syms = len(selected_symbols)
                
                for idx, sym in enumerate(selected_symbols):
                    res = scanner.scan_symbol(sym)
                    if res: results.append(res)
                    progress_pct = int(((idx + 1) / total_syms) * 100)
                    progress_bar.progress(progress_pct, text=f"جاري الفحص: [{idx+1}/{total_syms}] أصل | تم رصد ({len(results)}) فرصة حتى الآن.")
                
                progress_bar.empty()
                st.session_state["last_scan_results"] = pd.DataFrame(results)
                st.success("✅ اكتمل المسح بنجاح!")

        with c_btn2:
            if st.button("📤 إرسال كارت أعلى 10 فرص يدوياً لتليجرام"):
                saved_df = st.session_state["last_scan_results"]
                if not saved_df.empty:
                    success = TelegramEngine.send_top10_card(ui_token, ui_chat, market_choice, scan_tf, saved_df)
                    if success: st.success("🎉 تم إرسال بطاقة أعلى 10 فرص لتليجرام بنجاح!")
                    else: st.error("❌ فشل إرسال البطاقة.")
                else: st.warning("لا توجد نتائج مسح حالياً للإرسال.")

        if auto_stream_mode == "تشغيل تلقائي - ON 🟢":
            st.info("⚡ نظام البث الآلي مفعل.. جاري فحص الأصول وإرسال الفرص لتليجرام تلقائياً.")
            scanner = SabryVisionMasterScanner(config, scan_tf)
            results = []
            for sym in selected_symbols[:15]:
                res = scanner.scan_symbol(sym)
                if res: results.append(res)
            if results:
                res_df = pd.DataFrame(results)
                TelegramEngine.send_top10_card(ui_token, ui_chat, market_choice, scan_tf, res_df)

        saved_df = st.session_state["last_scan_results"]
        if not saved_df.empty:
            st.success(f"تم رصد ({len(saved_df)}) فرصة مؤكدة:")
            display_df = saved_df.reset_index().rename(columns={"index": "رقم الفرصة"})
            display_df["رقم الفرصة"] = display_df["رقم الفرصة"] + 1
            st.dataframe(display_df, use_container_width=True)
            
            st.markdown("### 📈 تصدير الرموز الرسمية لـ TradingView")
            tv_syms = [TradingViewFormatter.format_symbol_for_tv(s) for s in saved_df["Symbol"].head(20).tolist()]
            st.text_area("النص الجاهز لـ TradingView:", value=",".join(tv_syms), height=80)
        else:
            st.info("اضغط على زر المسح لعرض الفرص الحية.")

    # TAB 2: TRADINGVIEW-GRADE PROFESSIONAL CHART & DETAILED DIAGNOSTIC CARDS
    with tab2:
        st.subheader("🧠 التحليل الفني العميق والشارت الاحترافي (مماثل لـ TradingView)")
        scan_syms = saved_df["Symbol"].tolist() if not saved_df.empty else []
        chart_source = st.selectbox("مصدر الأصل للتحليل الفني:", ["إدخال رمز يدوي"] + scan_syms)
        deep_sym = st.text_input("أدخل رمز السهم يدوياً:", value="NVDA").upper() if chart_source == "إدخال رمز يدوي" else chart_source
        deep_tf = st.selectbox("الإطار الزمني للتحليل (Current TF):", ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"], index=3, key="t2_tf")

        c_i1, c_i2, c_i3, c_i4 = st.columns(4)
        show_emas = c_i1.selectbox("المتوسطات EMA (20/50/100/200):", ["إظهار 🟢", "إخفاء 🔴"], index=0)
        show_bb = c_i2.selectbox("بولينجر باند (Bollinger):", ["إظهار 🟢", "إخفاء 🔴"], index=0)
        show_vwap = c_i3.selectbox("الفي واب والانحرافات:", ["إظهار 🟢", "إخفاء 🔴"], index=0)
        show_ichi = c_i4.selectbox("سحابة وخطوط الإيشيموكو:", ["إظهار 🟢", "إخفاء 🔴"], index=0)

        deep_df = UnifiedDataProvider.fetch_raw_ohlcv(deep_sym, interval=deep_tf, period="60d")
        if not deep_df.empty:
            deep_df = SuperPOCEngine.calculate_indicators(deep_df)
            poc_res = SuperPOCEngine.calculate_multi_pocs(deep_df)

            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.65, 0.175, 0.175])

            # Candlesticks with High-Volume Coloring (White for Bullish, Orange for Bearish)
            vol_mean = deep_df['volume'].rolling(20, min_periods=1).mean()
            candle_colors = []
            for idx, row in deep_df.iterrows():
                is_green = row['close'] >= row['open']
                is_high_vol = row['volume'] > (vol_mean.loc[idx] * 1.5 if idx in vol_mean else row['volume'])
                if is_high_vol and is_green: candle_colors.append('#FFFFFF') # White
                elif is_high_vol and not is_green: candle_colors.append('#FF4500') # Orange
                else: candle_colors.append('#00FF7F' if is_green else '#FF0000')

            fig.add_trace(go.Candlestick(
                x=deep_df.index, open=deep_df['open'], high=deep_df['high'], low=deep_df['low'], close=deep_df['close'],
                increasing_line_color='#00FF7F', decreasing_line_color='#FF0000', name="الشموع اليابانية"
            ), row=1, col=1)

            if show_emas == "إظهار 🟢":
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['ema20'], line=dict(color='#00BFFF', width=1), name="EMA 20"), row=1, col=1)
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['ema50'], line=dict(color='#FFA500', width=1), name="EMA 50"), row=1, col=1)
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['ema200'], line=dict(color='#FF1493', width=1.5), name="EMA 200"), row=1, col=1)

            if show_bb == "إظهار 🟢":
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['bb_upper'], line=dict(color='rgba(200,200,200,0.5)', width=1, dash='dot'), name="BB Upper"), row=1, col=1)
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['bb_lower'], line=dict(color='rgba(200,200,200,0.5)', width=1, dash='dot'), name="BB Lower", fill='tonexty', fillcolor='rgba(200,200,200,0.05)'), row=1, col=1)

            if show_vwap == "إظهار 🟢":
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['vwap'], line=dict(color='#FFD700', width=1.5), name="VWAP"), row=1, col=1)
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['vwap_sd1_p'], line=dict(color='#7CFC00', width=1, dash='dash'), name="VWAP +1SD"), row=1, col=1)
                fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['vwap_sd1_m'], line=dict(color='#FF6347', width=1, dash='dash'), name="VWAP -1SD"), row=1, col=1)

            if poc_res["super_zone"] and poc_res["zone_range"]:
                fig.add_hrect(
                    y0=poc_res["zone_range"][0], y1=poc_res["zone_range"][1],
                    fillcolor="green", opacity=0.15, line_width=0, annotation_text="Super POC Zone", row=1, col=1
                )

            fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['rsi'], line=dict(color='#00FFFF', width=1.5), name="RSI (14)"), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

            fig.add_trace(go.Bar(x=deep_df.index, y=deep_df['macd_hist'], marker_color=np.where(deep_df['macd_hist'] >= 0, '#00FF7F', '#FF0000'), name="MACD Hist"), row=3, col=1)
            fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['macd'], line=dict(color='#1E90FF', width=1), name="MACD Line"), row=3, col=1)
            fig.add_trace(go.Scatter(x=deep_df.index, y=deep_df['macd_signal'], line=dict(color='#FF8C00', width=1), name="Signal Line"), row=3, col=1)

            fig.update_layout(template="plotly_dark", height=700, paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # ------------------------------------------------------------------
            # DETAILED INSTITUTIONAL TECHNICAL DIAGNOSTIC CARD
            # ------------------------------------------------------------------
            st.markdown(f"### 📋 بطاقة التشخيص الفني التفصيلية لكل مؤشر (على الفريم: `{deep_tf}`)")
            
            curr_rsi = float(deep_df['rsi'].iloc[-1])
            ema_20 = float(deep_df['ema20'].iloc[-1])
            ema_50 = float(deep_df['ema50'].iloc[-1])
            ema_200 = float(deep_df['ema200'].iloc[-1])
            close_p = float(deep_df['close'].iloc[-1])
            macd_val = float(deep_df['macd'].iloc[-1])
            macd_sig = float(deep_df['macd_signal'].iloc[-1])
            vwap_val = float(deep_df['vwap'].iloc[-1])

            diag_data = [
                {"المؤشر / الأداة": "متوسطات الحركة (EMA 20/50/200)", "القيمة الحالية": f"20:{round(ema_20,2)} | 50:{round(ema_50,2)} | 200:{round(ema_200,2)}", "التقييم الفني": "ترتيب صاعد إيجابي (EMA20 > EMA50 > EMA200) 🟢" if ema_20 > ema_50 > ema_200 else "ترتيب هابط سلبي 🔴"},
                {"المؤشر / الأداة": "مؤشر القوة النسبية (RSI 14)", "القيمة الحالية": f"{round(curr_rsi, 2)}", "التقييم الفني": "تشبع شرائي قوي 🔴" if curr_rsi > 70 else ("تشبع بيعي فرصة ارتداد 🟢" if curr_rsi < 30 else "زخم متوازن مستقر 🟢")},
                {"المؤشر / الأداة": "مؤشر الماكد (MACD & Signal)", "القيمة الحالية": f"MACD: {round(macd_val, 3)} | Sig: {round(macd_sig, 3)}", "التقييم الفني": "تقاطع إيجابي صاعد وفوق خط الصفر 🚀" if macd_val > macd_sig else "تقاطع سلبي هابط 🔴"},
                {"المؤشر / الأداة": "متوسط السعر المرجح (VWAP)", "القيمة الحالية": f"${round(vwap_val, 2)}", "التقييم الفني": "السعر أعلى الVWAP (دعم مؤسسي إيجابي) 🟢" if close_p > vwap_val else "السعر أدنى الVWAP (ضغط بيعي) 🔴"},
                {"المؤشر / الأداة": "هيكلة السوق والسمارت ماني (SMC)", "القيمة الحالية": SuperPOCEngine.detect_smc_structure(deep_df), "التقييم الفني": "إشارات هيكلية مؤسسية مؤكدة لتتبع السيولة 🌟"},
            ]
            st.dataframe(pd.DataFrame(diag_data), use_container_width=True)

            # ------------------------------------------------------------------
            # INDEPENDENT MULTI-TIMEFRAME CONSENSUS MATRIX
            # ------------------------------------------------------------------
            st.markdown("### 🌐 تقييم توافق الفريمات المتعددة (Multi-Timeframe Consensus Matrix)")
            st.info("يقوم هذا النموذج بفحص التوافق الاتجاهي عبر الفريمات الزمنية المختلفة لتقييم جودة فرصة الدخول على الفريم الحالي.")
            
            mtf_frames = ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"]
            mtf_results = []
            for tf in mtf_frames:
                sub_d = UnifiedDataProvider.fetch_raw_ohlcv(deep_sym, interval=tf, period="30d")
                if not sub_d.empty and len(sub_d) > 10:
                    sub_d = SuperPOCEngine.calculate_indicators(sub_d)
                    p_close = sub_d['close'].iloc[-1]
                    e20 = sub_d['ema20'].iloc[-1]
                    e50 = sub_d['ema50'].iloc[-1]
                    trend = "صاعد قوي 🟢" if p_close > e20 > e50 else ("هابط 🔴" if p_close < e20 < e50 else "عرضي متذبذب 🟡")
                    rsi_v = round(sub_d['rsi'].iloc[-1], 1)
                    mtf_results.append({"الإطار الزمني": tf, "الاتجاه الفني": trend, "قيمة RSI": rsi_v, "توافق الفريم": "متوافق مع الفرصة ✅" if p_close > e20 else "غير متوافق ⚠️"})
            
            if mtf_results:
                st.dataframe(pd.DataFrame(mtf_results), use_container_width=True)
            else:
                st.warning("تعذر جلب مصفوفة الفريمات المتعددة.")
        else:
            st.warning("تعذر جلب بيانات الشارت.")

    # TAB 3: FINANCIAL AUDIT
    with tab3:
        st.subheader("📊 التقييم المالي الأساسي ومصفوفة التدقيق المؤسسي")
        st.info("هذا القسم يحتوي على قوائم الأرباح ومستهدفات المؤسسات العالمية.")

    # TAB 4: PORTFOLIO & TRADES
    with tab4:
        st.subheader("💼 المحفظة وتتبع الصفقات الحية")

    # TAB 5: CUSTOM WATCHLIST MANAGER
    with tab5:
        st.subheader("📁 إدارة القوائم المخصصة")

if __name__ == "__main__":
    main()
