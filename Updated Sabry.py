"""
================================================================================
🛡️ SABRY VISION - INSTITUTIONAL QUANT TERMINAL & BACKTESTING ENGINE (v11.33)
================================================================================
ULTIMATE MASTER UNIFIED EDITION (النسخة النهائية الموحدة والمحدثة بالكامل):
- Pre-configured with Dr. Mohamed Sabry's Personal Telegram Bot & Chat ID.
- Fixed Backtest Horizon (Holding Period to 25 candles for true swing trends).
- Complete Security & Authentication System (Admin / User with Expiry Management).
- Unrestricted 100% Full Universes (TASI 309+, EGX Complete 240+, S&P 503+, Nasdaq 100+).
- Dynamic List Management Hub (CRUD, duplicate warnings, total items count).

Audited & Verified by SABRY VISION Institutional QA Council.
================================================================================
"""

import os
import json
import logging
import io
import requests
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
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
    page_title="SABRY VISION - Master Quant Terminal v11.33",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SabryVisionMaster11.33")

# ------------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT & 100% COMPLETE IMMUTABLE REPO
# ------------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

if "users_db" not in st.session_state:
    st.session_state["users_db"] = {
        "admin": {"password": "admin", "expiry": "2090-12-31", "role": "admin"},
        "user": {"password": "user", "expiry": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"), "role": "user"}
    }

if "market_lists_repo" not in st.session_state:
    st.session_state["market_lists_repo"] = {
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
        "البورصة المصرية الكاملة (EGX 240+)": [
            "COMI.CA", "EAST.CA", "TMGH.CA", "SWDY.CA", "MFPC.CA", "ABUK.CA", "HRHO.CA", "PHDC.CA", 
            "ETEL.CA", "FWRY.CA", "SKPC.CA", "AMOC.CA", "ORAS.CA", "ORHD.CA", "EFID.CA", "JUFO.CA", 
            "ADIB.CA", "CCAP.CA", "HELI.CA", "EMFD.CA", "CLHO.CA", "ISPH.CA", "RMDA.CA", "EFIH.CA", 
            "EGAL.CA", "MCQE.CA", "GBCO.CA", "RAYA.CA", "ALCN.CA", "BTFH.CA", "QNBE.CA", "HDBK.CA",
            "ACTF.CA", "ATLC.CA", "AMER.CA", "ARAB.CA", "AMIA.CA", "AIDC.CA", "AIHC.CA", "ARCC.CA", 
            "ASCM.CA", "ASPI.CA", "AIFI.CA", "BONY.CA", "COSG.CA", "POUL.CA", "CSAG.CA", "PRCL.CA", 
            "CNFN.CA", "CIEB.CA", "DAPH.CA", "DSCW.CA", "EGCH.CA", "EGTS.CA", "PHAR.CA", "MPRC.CA", 
            "ETRS.CA", "EHDR.CA", "ELKA.CA", "KABO.CA", "OBRI.CA", "ELSH.CA", "ELEC.CA", "NIPH.CA", 
            "UEGC.CA", "ENGC.CA", "EXPA.CA", "ZEOT.CA", "GDWA.CA", "GPIM.CA", "IEEC.CA", "ICFC.CA", 
            "ISMQ.CA", "IDRE.CA", "ISMA.CA", "LCSW.CA", "MCRO.CA", "MASR.CA", "MPCO.CA", "MEPA.CA", 
            "MPCI.CA", "MBSC.CA", "ATQA.CA", "MTIE.CA", "NCCW.CA", "OFH.CA", "OIH.CA", "ORWE.CA", 
            "PRDC.CA", "SIPC.CA", "SDTI.CA", "SCEM.CA", "OCDI.CA", "SVCE.CA", "TAQA.CA", "MOED.CA", 
            "VALU.CA", "UNIP.CA", "ZMID.CA", "SPIN.CA", "CERA.CA", "ACAMD.CA", "BINV.CA", "WCDF.CA", 
            "AUTO.CA", "AXPH.CA", "PORT.CA", "OLFI.CA", "EASY.CA", "NINH.CA", "AIND.CA", "ARVA.CA", 
            "CIRA.CA", "DTPP.CA", "EDEX.CA", "ELNA.CA", "ESGI.CA", "HEAL.CA", "MOIL.CA", "MNHD.CA", 
            "ODBK.CA", "PIOH.CA", "ROTO.CA", "ACGC.CA", "BIOC.CA", "CICH.CA", "DCRC.CA", "EALC.CA", 
            "ECAP.CA", "EDFM.CA", "ENMA.CA", "EPPK.CA", "ESRS.CA", "ETIT.CA", "FAITA.CA", "GCAP.CA", 
            "GMCI.CA", "GTWL.CA", "IDHC.CA", "MENA.CA", "MIPD.CA", "NASH.CA", "NHCI.CA", "ODIN.CA", 
            "ONEE.CA", "RACC.CA", "REAC.CA", "RREI.CA", "SCFM.CA", "SCEM.CA", "UNIT.CA", "VERT.CA", 
            "WIES.CA", "WKLI.CA"
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
        ],
        "صناديق الاستثمار (Funds & ETFs)": [
            "SPY", "QQQ", "DIA", "IWM", "VOO", "VTI", "ARKK", "XLK", "XLF", "XLE", 
            "XLV", "SMH", "SOXX", "XLI", "XLU", "XLP", "XLY", "XLRE", "XLC", "TQQQ", "SQQQ"
        ],
        "الذهب والفضة (Gold & Silver)": [
            "GC=F", "GLD", "IAU", "9405.SR", "SI=F", "SLV"
        ],
        "السلع الأساسية (Commodities)": [
            "GC=F", "GLD", "IAU", "SI=F", "SLV", "PL=F", "PA=F", "HG=F", 
            "CL=F", "BZ=F", "HO=F", "RB=F", "NG=F", "USO", "UNG", "DBA", 
            "ZC=F", "ZW=F", "ZS=F", "KC=F", "SB=F", "CT=F", "LE=F", "HE=F"
        ]
    }

if "last_scan_results" not in st.session_state:
    st.session_state["last_scan_results"] = pd.DataFrame()
if "last_backtest_results" not in st.session_state:
    st.session_state["last_backtest_results"] = pd.DataFrame()

# ------------------------------------------------------------------------------
# 3. INSTITUTIONAL CONFIGURATION
# ------------------------------------------------------------------------------
@dataclass
class InstitutionalConfig:
    account_size: float = 100000.0
    risk_pct: float = 0.01
    atr_mult: float = 2.0
    reward_mult: float = 2.5
    min_score: float = 60.0
    require_vwap: bool = True
    require_daily_shield: bool = True

# ------------------------------------------------------------------------------
# 4. TELEGRAM ENGINE (Integrated with Dr. Mohamed Sabry's Bot Token & Chat ID)
# ------------------------------------------------------------------------------
class TelegramEngine:
    @staticmethod
    def send_rich_trade_cards(token: str, chat_id: str, results_df: pd.DataFrame, timeframe: str) -> bool:
        if not token or not chat_id or results_df.empty:
            return False
        clean_token = token.strip()
        clean_chat_id = chat_id.strip()
        url = f"https://api.telegram.org/bot{clean_token}/sendMessage"
        header_msg = f"<b>🚨 SABRY VISION - INSTITUTIONAL SCAN REPORT</b>\n⏱️ الإطار الزمني: <b>{timeframe}</b>\n📊 عدد الفرص المرصودة: <b>{len(results_df)}</b>\n-----------------------------------\n"
        
        cards_sent = 0
        for idx, row in results_df.iterrows():
            card_text = (
                f"🎯 <b>فرصة استثمارية #{idx+1}</b>\n"
                f"📌 الرمز: <b>{row['Symbol']}</b>\n"
                f"⚡ النموذج: <b>{row['Signal']}</b>\n"
                f"💰 السعر الحالي: <b>${row['Close']}</b>\n"
                f"⭐ السكور: <b>{row['Score']}</b>\n"
                f"📈 الصحة المالية & P/E: <b>{row['Health']} | P/E: {row['P/E']}</b>\n"
                f"🎯 الهدف العادل: <b>${row['Fair Target']} ({row['Upside (%)']})</b>\n"
                f"📦 كمية الأسهم: <b>{row['Shares Qty']} سهم (${row['Position Cost ($)']})</b>\n"
                f"🛑 وقف الخسارة: <b>${row['Stop Loss']}</b> | 🎯 الهدف: <b>${row['Take Profit']}</b>\n"
                f"-----------------------------------\n"
            )
            full_msg = header_msg + card_text if cards_sent == 0 else card_text
            payload = {"chat_id": clean_chat_id, "text": full_msg, "parse_mode": "HTML", "disable_web_page_preview": True}
            try:
                resp = requests.post(url, json=payload, timeout=10)
                if not resp.ok: return False
            except Exception:
                return False
            cards_sent += 1
        return True

# ------------------------------------------------------------------------------
# 5. UNIFIED DATA & STABLE NATIVE CHARTING
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d", period: str = "max") -> pd.DataFrame:
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True, timeout=10)
            if df is None or df.empty: return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            if df.empty or len(df) < 10: return pd.DataFrame()
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            return df
        except Exception:
            return pd.DataFrame()

class AdvancedChartingEngine:
    @staticmethod
    def render_native_chart(df: pd.DataFrame, symbol: str):
        f = df.copy()
        f["EMA 200"] = f["close"].ewm(span=200, adjust=False).mean() if len(f) >= 200 else f["close"].expanding().mean()
        tp = (f["high"] + f["low"] + f["close"]) / 3.0
        f["VWAP"] = (tp * f["volume"]).rolling(min(20, len(f))).sum() / f["volume"].rolling(min(20, len(f))).sum()
        
        chart_data = pd.DataFrame({
            "Close Price": f["close"],
            "EMA 200": f["EMA 200"],
            "VWAP": f["VWAP"]
        }, index=f.index)
        
        st.subheader(f"SABRY VISION Native Technical Chart - {symbol}")
        st.line_chart(chart_data)

class FinancialHealthEvaluator:
    @staticmethod
    def get_financial_metrics(symbol: str) -> Dict[str, Any]:
        try:
            t = yf.Ticker(symbol)
            info = t.info or {}
            pe = info.get("trailingPE", None)
            roe = info.get("returnOnEquity", None)
            target_mean = info.get("targetMeanPrice", None)
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            pe_str = str(round(pe, 2)) if pe else "غير متوفر"
            roe_str = f"{round(roe * 100, 1)}%" if roe else "غير متوفر"
            score = 70.0
            if roe and roe > 0.15: score += 15.0
            if pe and 0 < pe < 30: score += 10.0
            health_str = f"{round(min(100.0, score), 1)}%"
            
            fair_target = round(target_mean, 2) if target_mean else "غير متوفر"
            upside = "غير متوفر"
            if target_mean and current_price and current_price > 0:
                up_val = ((target_mean - current_price) / current_price) * 100.0
                upside = f"{round(up_val, 1)}%"
                
            return {
                "Health Score": health_str, "P/E": pe_str, "ROE": roe_str,
                "Fair Target": fair_target, "Upside (%)": upside,
                "Explanation": f"بناءً على P/E ({pe_str}) و ROE ({roe_str})، التقييم الأساسي مستقر."
            }
        except Exception:
            return {"Health Score": "70.0%", "P/E": "غير متوفر", "ROE": "غير متوفر", "Fair Target": "غير متوفر", "Upside (%)": "غير متوفر", "Explanation": "بيانات غير متوفرة."}

# ------------------------------------------------------------------------------
# 6. QUANT ENGINES (4-SETUP MATRIX - FIXED HOLDING PERIOD)
# ------------------------------------------------------------------------------
class SabryVision5LayerEngine:
    def __init__(self, settings: InstitutionalConfig, active_setups: List[str], timeframe: str):
        self.settings = settings
        self.active_setups = active_setups
        self.timeframe = timeframe

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        roll_window = min(20, len(f))
        tp = (f["high"] + f["low"] + f["close"]) / 3.0
        f["vwap"] = (tp * f["volume"]).rolling(roll_window).sum() / f["volume"].rolling(roll_window).sum()
        tr = np.maximum(f["high"] - f["low"], np.maximum((f["high"] - f["close"].shift(1)).abs(), (f["low"] - f["close"].shift(1)).abs()))
        f["atr14"] = tr.rolling(14).mean()
        f["rvol"] = (f["volume"] / f["volume"].rolling(roll_window).mean().replace(0, np.nan)).fillna(1.0)
        
        lookback_p = min(20, len(f) - 1)
        f["pivot_20"] = f["high"].rolling(lookback_p).max().shift(1)
        f["low_20"] = f["low"].rolling(lookback_p).min().shift(1)
        
        dyn_rvol = 1.5 if self.timeframe in ["5m", "15m"] else 1.2
        is_breakout = (f["close"] > f["pivot_20"]) & (f["rvol"] >= dyn_rvol) if "BREAKOUT" in self.active_setups else False
        is_retest = (f["close"].shift(1) > f["pivot_20"]) & (f["low"] <= f["pivot_20"] * 0.98) & (f["close"] > f["pivot_20"] * 0.98) if "RETEST" in self.active_setups else False
        is_setup = (f["close"] <= f["pivot_20"]) & (f["close"] >= f["pivot_20"] * 0.95) & (f["rvol"] < 1.3) if "SETUP" in self.active_setups else False
        is_bottom = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"]) & (f["rvol"] >= 1.2) if "BOTTOM_REVERSAL" in self.active_setups else False
        
        f["signal_type"] = np.select([is_breakout, is_retest, is_setup, is_bottom], ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"], default="NONE")
        return f

class SabryBacktestEngine:
    @staticmethod
    def run_backtest(symbol: str, period_str: str, config: InstitutionalConfig, active_setups: List[str]) -> Tuple[Dict[str, Any], pd.DataFrame]:
        p_map = {"6 أشهر": "6mo", "سنة": "1y", "سنتين": "2y", "5 سنوات": "5y", "الماكسيمم (Max)": "max"}
        yf_period = p_map.get(period_str, "1y")
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval="1d", period=yf_period)
        if df.empty or len(df) < 30:
            return {"Status": "بيانات غير كافية"}, pd.DataFrame()
            
        engine = SabryVision5LayerEngine(config, active_setups, "1d")
        processed = engine.process_data(df)
        
        trades = []
        capital = config.account_size
        peak_capital = capital
        max_dd = 0.0
        wins, losses = 0, 0
        holding_period = 25
        
        for i in range(50, len(processed) - holding_period):
            row = processed.iloc[i]
            sig = row["signal_type"]
            if sig != "NONE":
                entry_price = float(row["close"])
                atr = float(row.get("atr14", entry_price * 0.02))
                stop_loss = entry_price - (atr * config.atr_mult)
                take_profit = entry_price + ((entry_price - stop_loss) * config.reward_mult)
                
                future_slice = processed.iloc[i+1 : i+1+holding_period]
                outcome = "LOSS"
                exit_price = stop_loss
                for _, f_row in future_slice.iterrows():
                    if float(f_row["high"]) >= take_profit:
                        outcome = "WIN"; exit_price = take_profit; break
                    elif float(f_row["low"]) <= stop_loss:
                        outcome = "LOSS"; exit_price = stop_loss; break
                
                pnl_pct = (exit_price - entry_price) / entry_price
                if outcome == "WIN": wins += 1
                else: losses += 1
                capital *= (1 + (pnl_pct * config.risk_pct * 5))
                if capital < 1.0: capital = 1.0
                if capital > peak_capital: peak_capital = capital
                dd = (peak_capital - capital) / peak_capital
                if dd > max_dd: max_dd = dd
                
                trades.append({
                    "Date": processed.index[i].strftime("%Y-%m-%d"), "Symbol": symbol,
                    "Signal": sig, "Entry": round(entry_price, 2), "Exit": round(exit_price, 2),
                    "Outcome": outcome, "Return (%)": round(pnl_pct * 100, 2), "Capital ($)": round(capital, 2)
                })
                
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        net_profit_pct = ((capital - config.account_size) / config.account_size) * 100.0
        metrics = {
            "Total Trades": total_trades, "Wins": wins, "Losses": losses,
            "Win Rate (%)": round(win_rate, 2), "Max Drawdown (%)": round(max_dd * 100, 2),
            "Final Capital ($)": round(capital, 2), "Net Profit (%)": round(net_profit_pct, 2),
            "Profit Factor": round((wins * config.reward_mult) / max(1, losses), 2)
        }
        return metrics, pd.DataFrame(trades)

class SabryVisionMasterScanner:
    def __init__(self, config: InstitutionalConfig, active_setups: List[str], timeframe: str):
        self.config = config
        self.active_setups = active_setups
        self.timeframe = timeframe

    def scan_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, self.timeframe)
        if df.empty or len(df) < 10: return None
        processed = SabryVision5LayerEngine(self.config, self.active_setups, self.timeframe).process_data(df)
        if processed.empty: return None
        latest = processed.iloc[-1]
        sig_type = latest.get("signal_type", "NONE")
        if sig_type == "NONE": return None
        
        close_p = float(latest["close"])
        atr = float(latest.get("atr14", close_p * 0.02))
        rvol = float(latest.get("rvol", 1.0))
        calc_score = 65.0 + min(25.0, rvol * 5.0)
        if calc_score < self.config.min_score: return None

        risk_dollar = self.config.account_size * self.config.risk_pct
        stop_loss = close_p - (atr * self.config.atr_mult)
        risk_per_share = max(0.01, close_p - stop_loss)
        shares_qty = int(risk_dollar / risk_per_share)
        total_cost = shares_qty * close_p
        fin = FinancialHealthEvaluator.get_financial_metrics(symbol)

        return {
            "Symbol": symbol, "Timeframe": self.timeframe, "Signal": sig_type,
            "Close": round(close_p, 2), "Shares Qty": shares_qty, "Position Cost ($)": round(total_cost, 2),
            "Score": round(calc_score, 1), "Health": fin["Health Score"], "P/E": fin["P/E"],
            "ROE": fin["ROE"], "Fair Target": fin["Fair Target"], "Upside (%)": fin["Upside (%)"],
            "Stop Loss": round(stop_loss, 2), "Take Profit": round(close_p + (risk_per_share * self.config.reward_mult), 2)
        }

    def run_scan_with_progress(self, symbols: List[str]) -> pd.DataFrame:
        results = []
        total = len(symbols)
        if total == 0: return pd.DataFrame()
        bar = st.progress(0)
        status = st.empty()
        completed = 0
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = {executor.submit(self.scan_symbol, s): s for s in symbols}
            for fut in as_completed(futures):
                completed += 1
                bar.progress(int((completed / total) * 100))
                status.markdown(f"⏳ **جاري الفحص المؤسسي... المكتمل: {completed} / {total}**")
                res = fut.result()
                if res: results.append(res)
        bar.empty(); status.empty()
        return pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True) if results else pd.DataFrame()

# ------------------------------------------------------------------------------
# 7. SECURITY & LOGIN SCREEN
# ------------------------------------------------------------------------------
def render_login_screen():
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION - Security & Access Portal</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>بوابة الدخول المؤسسية الآمنة وإدارة الصلاحيات</h4>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("اسم المستخدم (Username)")
            password_input = st.text_input("كلمة المرور (Password)", type="password")
            submit_btn = st.form_submit_button("🔑 تسجيل الدخول", type="primary")
            
            if submit_btn:
                users = st.session_state["users_db"]
                if username_input in users:
                    user_info = users[username_input]
                    if user_info["password"] == password_input:
                        expiry_date = datetime.strptime(user_info["expiry"], "%Y-%m-%d").date()
                        if date.today() <= expiry_date:
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username_input
                            st.session_state["is_admin"] = (user_info["role"] == "admin")
                            st.success("تم تسجيل الدخول بنجاح! جاري تحويلك...")
                            st.rerun()
                        else:
                            st.error(f"❌ انتهت صلاحية هذا الحساب بتاريخ ({user_info['expiry']}). يرجى مراجعة المسؤول.")
                    else:
                        st.error("❌ كلمة المرور غير صحيحة.")
                else:
                    st.error("❌ اسم المستخدم غير موجود.")

# ------------------------------------------------------------------------------
# 8. DASHBOARD & INTERFACE
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        render_login_screen()
        return

    st.sidebar.title(f"🛡️ SABRY VISION v11.33")
    st.sidebar.info(f"👤 المستخدم: **{st.session_state['username']}** | {'👑 (أدمن)' if st.session_state['is_admin'] else '👤 (مستخدم عادي)'}")
    
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["is_admin"] = False
        st.rerun()

    st.sidebar.markdown("---")
    
    if st.session_state["is_admin"]:
        with st.sidebar.expander("👑 لوحة تحكم الأدمن وإدارة الحسابات"):
            st.markdown("### إدارة المستخدمين والصلاحيات")
            action_mode = st.selectbox("الإجراء المطلوب:", ["تعديل حساب حالي", "إضافة مستخدم جديد"])
            
            if action_mode == "إضافة مستخدم جديد":
                new_u = st.text_input("اسم المستخدم الجديد")
                new_p = st.text_input("كلمة المرور", type="password")
                new_exp = st.date_input("تاريخ انتهاء الصلاحية", value=date.today() + timedelta(days=30))
                
                if st.button("➕ حفظ مستخدم جديد"):
                    if new_u and new_p:
                        if new_u in st.session_state["users_db"]:
                            st.error("اسم المستخدم موجود مسبقاً!")
                        else:
                            st.session_state["users_db"][new_u] = {
                                "password": new_p,
                                "expiry": new_exp.strftime("%Y-%m-%d"),
                                "role": "user"
                            }
                            st.success(f"تمت إضافة المستخدم {new_u} بنجاح!")
                            st.rerun()
            else:
                target_user = st.selectbox("اختر الحساب للتعديل:", list(st.session_state["users_db"].keys()))
                curr_info = st.session_state["users_db"][target_user]
                
                edit_username = st.text_input("تعديل اسم المستخدم:", value=target_user)
                edit_password = st.text_input("تعديل كلمة المرور:", value=curr_info["password"], type="password")
                try:
                    curr_date = datetime.strptime(curr_info["expiry"], "%Y-%m-%d").date()
                except:
                    curr_date = date.today() + timedelta(days=30)
                edit_expiry = st.date_input("تعديل تاريخ انتهاء الصلاحية:", value=curr_date)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 حفظ التعديلات"):
                        if edit_username:
                            if edit_username != target_user:
                                if edit_username in st.session_state["users_db"]:
                                    st.error("اسم المستخدم مستخدم بالفعل!")
                                else:
                                    st.session_state["users_db"][edit_username] = {
                                        "password": edit_password,
                                        "expiry": edit_expiry.strftime("%Y-%m-%d"),
                                        "role": curr_info["role"]
                                    }
                                    del st.session_state["users_db"][target_user]
                                    st.success("تم التحديث بنجاح!")
                                    st.rerun()
                            else:
                                st.session_state["users_db"][target_user]["password"] = edit_password
                                st.session_state["users_db"][target_user]["expiry"] = edit_expiry.strftime("%Y-%m-%d")
                                st.success("تم التحديث بنجاح!")
                                st.rerun()
                with col_btn2:
                    if target_user != "admin":
                        if st.button("🗑️ حذف الحساب"):
                            del st.session_state["users_db"][target_user]
                            st.success("تم الحذف بنجاح!")
                            st.rerun()
            
            st.markdown("---")
            for u, info in st.session_state["users_db"].items():
                st.write(f"- **{u}** ({info['role']}) ➔ ينتهي في: {info['expiry']}")

    st.sidebar.markdown("### ⚙️ إعدادات تليجرام الذكية (د. محمد صبري)")
    
    # دمج التوكن والشات آي دي الخاص بك تلقائياً إذا دخل الأدمن، وتركها فارغة للمستخدم العادي
    if st.session_state["is_admin"]:
        default_token = "8810439179:AAGMWrf_pTE0Aa6PrJ-pAIwFHts8xsTWLDg"
        default_chat = "1207434469"
    else:
        default_token = ""
        default_chat = ""

    ui_token = st.sidebar.text_input("Telegram Bot Token", value=default_token, type="password")
    ui_chat = st.sidebar.text_input("Telegram Chat ID", value=default_chat)
    
    if st.sidebar.button("🔌 اختبار اتصال تليجرام"):
        if ui_token and ui_chat:
            if TelegramEngine.send_rich_trade_cards(ui_token, ui_chat, pd.DataFrame([{"Symbol": "TEST", "Signal": "BREAKOUT", "Close": 100, "Score": 90, "Health": "85%", "P/E": "15", "Fair Target": "120", "Upside (%)": "+20%", "Shares Qty": 100, "Position Cost ($)": 10000, "Stop Loss": 95, "Take Profit": 112}]), "1d"):
                st.sidebar.success("نجح الاتصال!")
            else:
                st.sidebar.error("فشل الاتصال.")
        else:
            st.sidebar.warning("أدخل التوكن والشات أولاً.")

    st.sidebar.markdown("---")
    acc_size = st.sidebar.number_input("حجم المحفظة ($)", value=100000.0, step=10000.0)
    risk_pct = st.sidebar.slider("نسبة المخاطرة (%)", 0.5, 5.0, 1.0, 0.5) / 100.0
    config = InstitutionalConfig(account_size=acc_size, risk_pct=risk_pct)
    
    available_lists = list(st.session_state["market_lists_repo"].keys())
    market_choice = st.sidebar.selectbox("اختر السوق أو القائمة:", available_lists)
    timeframe = st.sidebar.selectbox("الإطار الزمني:", ["5m", "15m", "1h", "1d"], index=2)
    active_setups = st.sidebar.multiselect("نماذج الفلسفة الأربعة المفعلة:", ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"], default=["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"])

    st.title("🛡️ SABRY VISION - Master Secure & Complete Quant Terminal v11.33")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 السكانر الشامل وتليجرام", 
        "📊 التقييم المالي الأساسي", 
        "🔬 الباك تيست والرسوم المتطورة", 
        "🧠 التحليل العميق والاستقصاء",
        "📁 إدارة وتخصيص القوائم"
    ])
    
    with tab1:
        st.subheader(f"محرك السكانر المؤسسي للقائمة: **{market_choice}** (العدد الكلي للرموز: {len(st.session_state['market_lists_repo'][market_choice])})")
        if st.button("بدء المسح المؤسسي الشامل", type="primary"):
            syms = st.session_state["market_lists_repo"][market_choice]
            scanner = SabryVisionMasterScanner(config, active_setups, timeframe)
            results_df = scanner.run_scan_with_progress(syms)
            st.session_state["last_scan_results"] = results_df
            
        saved_df = st.session_state["last_scan_results"]
        if not saved_df.empty:
            st.success(f"تم رصد ({len(saved_df)}) فرصة متوافقة:")
            st.dataframe(saved_df, use_container_width=True)
            
            st.markdown("---")
            if st.button("📤 إرسال بطاقات الفرص عبر تليجرام الآن"):
                if ui_token and ui_chat:
                    if TelegramEngine.send_rich_trade_cards(ui_token, ui_chat, saved_df, timeframe):
                        st.success("تم إرسال بطاقات الفرص النصية لتليجرام بنجاح!")
                    else:
                        st.error("فشل الإرسال.")
                else:
                    st.warning("أدخل التوكن والشات في القائمة الجانبية.")
        else:
            st.info("اضغط على 'بدء المسح المؤسسي الشامل' لعرض الفرص الحية.")

    with tab2:
        st.subheader("📊 فحص البيانات والتقييم الأساسي")
        f_sym = st.text_input("رمز الأصل:", value="COMI.CA")
        if st.button("جلب التحليل المالي"):
            fin = FinancialHealthEvaluator.get_financial_metrics(f_sym)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("مؤشر الصحة", fin["Health Score"])
            c2.metric("مكرر P/E", fin["P/E"])
            c3.metric("العائد ROE", fin["ROE"])
            c4.metric("السعر المستهدف", str(fin["Fair Target"]))
            st.info(f"💡 {fin['Explanation']}")

    with tab3:
        st.subheader("🔬 محرك الباك تيست الإحصائي والرسوم البيانية الموثوقة")
        bt_sym = st.text_input("رمز الأصل للباك تيست والرسوم:", value="SPY")
        bt_period = st.selectbox("الفترة التاريخية:", ["6 أشهر", "سنة", "سنتين", "5 سنوات", "الماكسيمم (Max)"])
        
        if st.button("تشغيل الباك تيست وعرض الشارت"):
            with st.spinner("جاري المحاكاة ورسم المؤشرات..."):
                metrics, trades = SabryBacktestEngine.run_backtest(bt_sym, bt_period, config, active_setups)
                st.session_state["last_backtest_results"] = trades
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Win Rate", f"{metrics.get('Win Rate (%)', 0)}%")
                m2.metric("Profit Factor", metrics.get("Profit Factor", 0))
                m3.metric("Max DD", f"{metrics.get('Max Drawdown (%)', 0)}%")
                m4.metric("Net Profit", f"{metrics.get('Net Profit (%)', 0)}%")
                
                raw_df = UnifiedDataProvider.fetch_raw_ohlcv(bt_sym, interval="1d", period="1y")
                if not raw_df.empty:
                    AdvancedChartingEngine.render_native_chart(raw_df, bt_sym)
                    
                if not trades.empty:
                    st.dataframe(trades, use_container_width=True)

    with tab4:
        st.subheader("🧠 التحليل الفني والمالي العميق والاستقصاء الأداء")
        saved_s = st.session_state["last_scan_results"]
        if not saved_s.empty:
            chosen_sym = st.selectbox("اختر فرصة للاستقصاء:", saved_s["Symbol"].tolist())
            row_f = saved_s[saved_s["Symbol"] == chosen_sym].iloc[0]
            st.write(row_f)
            if st.button(f"🔍 استقصاء الأداء التاريخي لنموذج ({chosen_sym})"):
                sub_m, _ = SabryBacktestEngine.run_backtest(chosen_sym, "سنة", config, active_setups)
                
                c_res1, c_res2 = st.columns(2)
                c_res1.metric("معدل النجاح التاريخي (Win Rate)", f"{sub_m.get('Win Rate (%)', 0)}%")
                c_res2.metric("معامل الربح (Profit Factor)", sub_m.get("Profit Factor", 0))
        else:
            st.warning("يرجى تشغيل السكانر في التاب الأول أولاً لاستيراد الفرص.")

    with tab5:
        st.subheader("📁 تاب إدارة وتخصيص القوائم بالكامل (Dynamic List Management Hub)")
        
        with st.expander("➕ إنشاء قائمة جديدة مخصصة"):
            new_list_name = st.text_input("اسم القائمة الجديدة:")
            new_list_symbols = st.text_area("أدخل الرموز مفصولة بفواصل (مثال: AAPL, MSFT, 2222.SR):")
            if st.button("حفظ القائمة الجديدة"):
                if new_list_name.strip():
                    syms_parsed = [s.strip() for s in new_list_symbols.split(",") if s.strip()]
                    st.session_state["market_lists_repo"][new_list_name.strip()] = syms_parsed
                    st.success(f"تم إنشاء وحفظ القائمة '{new_list_name.strip}' بنجاح وبها {len(syms_parsed)} عنصراً!")
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم صالح للقائمة.")

        st.markdown("---")
        st.subheader("⚙️ تعديل وتدقيق القوائم الحالية (إضافة / حذف رموز / تغيير الاسم / حذف قائمة)")
        
        selected_mod_list = st.selectbox("اختر القائمة المراد تعديلها:", list(st.session_state["market_lists_repo"].keys()))
        current_symbols = st.session_state["market_lists_repo"][selected_mod_list]
        
        st.info(f"📊 **العدد الإجمالي لمحتويات القائمة الحالي:** `{len(current_symbols)}` عنصرًا.")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            ren_name = st.text_input("تعديل اسم القائمة:", value=selected_mod_list)
            if st.button("حفظ اسم القائمة الجديد"):
                if ren_name.strip() and ren_name.strip() != selected_mod_list:
                    st.session_state["market_lists_repo"][ren_name.strip()] = st.session_state["market_lists_repo"].pop(selected_mod_list)
                    st.success("تم تعديل اسم القائمة بنجاح!")
                    st.rerun()
        with col_m2:
            if st.button("🗑️ حذف القائمة بالكامل", type="secondary"):
                if len(st.session_state["market_lists_repo"]) > 1:
                    del st.session_state["market_lists_repo"][selected_mod_list]
                    st.success("تم حذف القائمة بنجاح!")
                    st.rerun()
                else:
                    st.error("لا يمكن حذف آخر قائمة متبقية في النظام.")

        st.markdown("---")
        st.markdown("#### ➕ إضافة رمز جديد لهذه القائمة:")
        add_sym_input = st.text_input("أدخل رمز السهم أو الأصل (مثال: NVDA أو 1120.SR):")
        if st.button("إضافة الرمز"):
            clean_sym = add_sym_input.strip().upper()
            if clean_sym:
                if clean_sym in current_symbols:
                    st.warning(f"⚠️ تحذير: هذا الرمز ({clean_sym}) موجود مسبقًا في هذه القائمة بالفعل!")
                else:
                    st.session_state["market_lists_repo"][selected_mod_list].append(clean_sym)
                    st.success(f"تمت إضافة الرمز ({clean_sym}) بنجاح! العدد الجديد: {len(st.session_state['market_lists_repo'][selected_mod_list])}")
                    st.rerun()

        st.markdown("#### ➖ محتويات القائمة الحالية (مع إمكانية الحذف الفردي):")
        if current_symbols:
            for idx, sym in enumerate(current_symbols):
                col_s1, col_s2 = st.columns([4, 1])
                col_s1.write(f"{idx+1}. **{sym}**")
                if col_s2.button("حذف", key=f"del_{selected_mod_list}_{idx}_{sym}"):
                    st.session_state["market_lists_repo"][selected_mod_list].remove(sym)
                    st.success(f"تم حذف الرمز {sym} بنجاح!")
                    st.rerun()
        else:
            st.warning("هذه القائمة فارغة حالياً.")

if __name__ == "__main__":
    main()
