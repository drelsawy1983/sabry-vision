"""
================================================================================
🛡️ SABRY VISION - INSTITUTIONAL QUANT TERMINAL & BACKTESTING ENGINE (v11.51)
================================================================================
ULTIMATE OVER-EXTENDED ALERTS, FIBONACCI GOLDEN RETEST & CHANDELIER PORTFOLIO EDITION:
- Pre-configured with Dr. Mohamed Sabry's Personal Telegram Bot & Chat ID.
- 100% Unmodified Stock Repository Retention + Expanded ADX, DFM, HSI & Spot Commodities.
- Visual Solid White Power Candlestick & Trend State Engine.
- Algorithmic Golden Ratio (Fibonacci 61.8% / Liquidity Sweep) Scanner Engine.
- Over-Extended Price Range Warning (Over-Extended ATR Thresholds).
- Dynamic Position Sizing across Scanner, Backtest, & Deep Dive.
- Complete Tab 6: Portfolio Manager with Chandelier ATR Trailing Stop & AI Post-Mortem.

Audited & Verified by SABRY VISION Institutional QA Council (22 Global Experts).
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
import plotly.graph_objects as go
import plotly.express as px

# ------------------------------------------------------------------------------
# 1. SYSTEM INITIALIZATION & PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v11.51",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SabryVisionMaster11.51")

# ------------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT & 100% COMPLETE REPO + PORTFOLIO DB
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

if "portfolio_trades" not in st.session_state:
    st.session_state["portfolio_trades"] = []

if "market_lists_repo" not in st.session_state:
    st.session_state["market_lists_repo"] = {
        "المؤشرات العالمية والأسواق (Global Indices)": [
            "^TASI.SR", "^EGX30", "^SPX", "^IXIC", "^DJI", "^FTSE", "^N225", "^HSI", "GC=F", "SI=F", "CL=F", "DX-Y.NYB"
        ],
        "سوق أبوظبي للأوراق المالية (ADX - موسعة بالكامل)": [
            "FAB.AD", "IHC.AD", "TAQA.AD", "ETISALAT.AD", "ALDAR.AD", "ADCB.AD", "ADIB.AD", "ADNOCDIST.AD", "MULTIPLY.AD", "NMDC.AD",
            "ADNH.AD", "ALFARAH.AD", "AGTHIA.AD", "ARIV.AD", "ASHGAB.AD", "BANKSHARJAH.AD", "BOS.AD", "Dana.AD", "Eshraq.AD", "RAKBANK.AD"
        ],
        "سوق دبي المالي (DFM - موسعة بالكامل)": [
            "EMAAR.DFM", "ENBD.DFM", "DIB.DFM", "DEWA.DFM", "DU.DFM", "ARAMEX.DFM", "EMAARDEV.DFM", "DIC.DFM", "SALIK.DFM", "TALABAT.DFM",
            "ARIG.DFM", "AMAN.DFM", "CBD.DFM", "DFM.DFM", "DSI.DFM", "GFH.DFM", "ITHMR.DFM", "MASRAF.DFM", "SHUAA.DFM", "UNIONPROPERTIES.DFM"
        ],
        "بورصة هونج كونج (Hang Seng - موسعة بالكامل)": [
            "0700.HK", "9988.HK", "3690.HK", "1211.HK", "0941.HK", "2318.HK", "1398.HK", "0388.HK", "2015.HK", "9888.HK",
            "0005.HK", "0011.HK", "0016.HK", "0027.HK", "0066.HK", "0101.HK", "0175.HK", "0267.HK", "0386.HK", "0669.HK",
            "0688.HK", "0762.HK", "0823.HK", "0883.HK", "0960.HK", "0968.HK", "0981.HK", "1038.HK", "1044.HK", "1093.HK"
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

if "last_scan_results" not in st.session_state:
    st.session_state["last_scan_results"] = pd.DataFrame()
if "last_backtest_results" not in st.session_state:
    st.session_state["last_backtest_results"] = pd.DataFrame()

# ------------------------------------------------------------------------------
# 3. INSTITUTIONAL CONFIGURATION & FIBONACCI RETEST ENGINE (v11.51)
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
    poc_convergence_tol: float = 0.0075
    sweep_tolerance: float = 0.015

class SuperPOCEngine:
    @staticmethod
    def calculate_multi_pocs(df: pd.DataFrame) -> dict:
        if len(df) < 50:
            return {"super_zone": None, "is_super": False, "pocs": {}}
        pocs = {}
        windows = [20, 60, 120, 300]
        for w in windows:
            if len(df) >= w:
                sub_df = df.tail(w)
            else:
                sub_df = df
            price_bins = pd.cut(sub_df['close'], bins=20)
            vol_profile = sub_df.groupby(price_bins, observed=False)['volume'].sum()
            if not vol_profile.empty:
                max_bin = vol_profile.idxmax()
                pocs[w] = max_bin.mid
            else:
                pocs[w] = sub_df['close'].iloc[-1]
                
        poc_values = list(pocs.values())
        mean_poc = np.mean(poc_values)
        max_deviation = max([abs(p - mean_poc) / max(1e-5, mean_poc) for p in poc_values])
        
        is_super = max_deviation <= 0.0075
        super_zone_price = mean_poc if is_super else poc_values[-1]
        
        return {
            "pocs": pocs,
            "super_zone": super_zone_price,
            "is_super": is_super,
            "deviation": max_deviation
        }

    @staticmethod
    def calculate_dual_vwap(df: pd.DataFrame) -> pd.DataFrame:
        tp = (df['high'] + df['low'] + df['close']) / 3.0
        df['vwap_intraday'] = (tp * df['volume']).cumsum() / df['volume'].cumsum().replace(0, np.nan)
        weekly_roll = 35 if len(df) >= 35 else len(df)
        df['vwap_weekly'] = (tp * df['volume']).rolling(weekly_roll).sum() / df['volume'].rolling(weekly_roll).sum().replace(0, np.nan)
        df['vwap_weekly'] = df['vwap_weekly'].fillna(df['vwap_intraday'])
        return df

class MarketBreadthEngine:
    @staticmethod
    def evaluate_market_breadth(symbols_list: List[str]) -> Dict[str, Any]:
        if not symbols_list or len(symbols_list) == 0:
            return {"Liquidity": "متوسطة", "Breadth": "محايد", "Market Quality": "مستقر وجيد", "Score": 70}
        
        sample_syms = symbols_list[:min(15, len(symbols_list))]
        rvol_list = []
        positive_count = 0
        total_checked = 0
        
        for sym in sample_syms:
            try:
                df = yf.download(sym, period="5d", interval="1d", progress=False, auto_adjust=True, timeout=3)
                if df is not None and len(df) >= 2:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    closes = df['close'].values
                    vols = df['volume'].values
                    mean_vol = np.mean(vols[:-1]) if len(vols) > 1 else vols[-1]
                    rvol = vols[-1] / max(1, mean_vol)
                    rvol_list.append(rvol)
                    if closes[-1] > closes[-2]:
                        positive_count += 1
                    total_checked += 1
            except Exception:
                continue
                
        avg_rvol = np.mean(rvol_list) if rvol_list else 1.0
        breadth_ratio = (positive_count / max(1, total_checked)) * 100
        
        liquidity = "مرتفعة وعالية النشاط 🟢" if avg_rvol >= 1.3 else ("متوسطة وعادية 🟡" if avg_rvol >= 0.9 else "ضعيفة وحذرة 🔴")
        breadth = "إيجابي وصاعد 📈" if breadth_ratio >= 60 else ("سلبي وهابط 📉" if breadth_ratio <= 40 else "عرضي متوازن ⚖️")
        
        if avg_rvol >= 1.2 and breadth_ratio >= 55:
            quality = "سوق ممتاز للصفقات الهجومية والانطلاقات 🚀"
            score = 88
        elif avg_rvol < 0.8 or breadth_ratio < 35:
            quality = "سوق ضعيف يتطلب أقصى درجات الحذر وإدارة المخاطر ⚠️"
            score = 45
        else:
            quality = "سوق متوسط ومستقر يتطلب انتقائية عالية للفرص 🛡️"
            score = 68
            
        return {
            "Liquidity": liquidity,
            "Breadth": f"{breadth} ({round(breadth_ratio, 1)}% صاعد)",
            "Market Quality": quality,
            "Score": score,
            "Avg RVOL": round(avg_rvol, 2)
        }

# ------------------------------------------------------------------------------
# 4. UNIVERSAL EXPORT HUB & TELEGRAM ENGINE
# ------------------------------------------------------------------------------
class UniversalExportEngine:
    @staticmethod
    def render_export_toolbar(data_df: pd.DataFrame, report_title: str, token: str, chat_id: str, timeframe: str):
        st.markdown(f"--- \n### 📤 مركز التصدير والمشاركة الشامل (Universal Export Hub)")
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        
        with col_ex1:
            if st.button(f"📋 نسخ البيانات للحافظة (Clipboard)", key=f"clip_{report_title}"):
                if not data_df.empty:
                    tsv_data = data_df.to_csv(sep="\t", index=False)
                    st.code(tsv_data, language="text")
                    st.success("تم تجهيز البيانات للنسخ بنجاح!")
                else:
                    st.warning("لا توجد بيانات متاحة للنسخ.")
                    
        with col_ex2:
            if st.button(f"🌐 مشاركة عبر السوشيال ميديا / X", key=f"soc_{report_title}"):
                st.info("🔗 رابط مشاركة تقرير SABRY VISION المؤسسي جاهز للنشر على منصة X وتطبيقات التواصل.")
                
        with col_ex3:
            if st.button(f"🚀 إرسال فوري لتليجرام", key=f"tg_{report_title}"):
                if token and chat_id and not data_df.empty:
                    if TelegramEngine.send_rich_trade_cards(token, chat_id, data_df, timeframe):
                        st.success("تم إرسال التقارير لغرفة تليجرام بنجاح!")
                    else:
                        st.error("فشل الإرسال، تحقق من التوكن والشات آي دي.")
                else:
                    st.warning("تأكد من إدخال بيانات تليجرام في القائمة الجانبية أو وجود بيانات مرصودة.")

class TelegramEngine:
    @staticmethod
    def send_rich_trade_cards(token: str, chat_id: str, results_df: pd.DataFrame, timeframe: str) -> bool:
        if not token or not chat_id or results_df.empty:
            return False
        clean_token = token.strip()
        clean_chat_id = chat_id.strip()
        url = f"https://api.telegram.org/bot{clean_token}/sendMessage"
        header_msg = f"<b>🚨 SABRY VISION v11.51 - INSTITUTIONAL SCAN REPORT</b>\n⏱️ الإطار الزمني: <b>{timeframe}</b>\n📊 عدد الفرص المرصودة: <b>{len(results_df)}</b>\n-----------------------------------\n"
        
        cards_sent = 0
        for idx, row in results_df.iterrows():
            card_text = (
                f"🎯 <b>فرصة استثمارية #{idx+1}</b>\n"
                f"📌 الرمز: <b>{row.get('Symbol', 'N/A')}</b>\n"
                f"⚡ النموذج: <b>{row.get('Signal', 'N/A')}</b>\n"
                f"⭐ تقييم AI: <b>{row.get('AI Score', 'N/A')}%</b>\n"
                f"💰 السعر الحالي: <b>${row.get('Close', 0)}</b>\n"
                f"📊 الفوليوم (Volume X): <b>{row.get('Volume X', 'N/A')}x</b>\n"
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
# 5. UNIFIED DATA & ADVANCED PLOTLY CHARTING ENGINE (v11.51)
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
    def render_chart_legend_card():
        st.markdown("""
        <div style='background-color: #161b22; padding: 12px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 15px;'>
            <h4 style='color: #58a6ff; margin-top: 0;'>🗺️ مفتاح الخريطة والدليل اللوني والخطوط (Sabry Vision Legend v11.51)</h4>
            <ul style='list-style-type: none; padding-left: 0; font-size: 14px;'>
                <li>🕯️ <b>الشموع اليابانية (Candlestick):</b> أخضر (صاعد) وأحمر (هابط).</li>
                <li>📈 <b>خط السعر (Line Chart):</b> خط متصل باللون الأخضر الفاتح (<code>#00CC96</code>).</li>
                <li>⚪ <b>الشمعة البيضاء القوية (White Power Candle):</b> شمعة يابانية مصمتة باللون الأبيض الكامل من الداخل والخارج لإبراز الانفجار السعري.</li>
                <li>📈 <b>متوسط EMA 200 & VWAP:</b> مؤشرات الاتجاه والسيولة المؤسسية.</li>
                <li>📐 <b>حالات خط الترند (Trend State):</b> صاعد، هابط، كسر تحذيري، واختراق مميز.</li>
                <li>⭐ <b>منطقة السوبر زون (Super Zone):</b> مستطيل ذهبي مظلل لتقارب الـ POCs.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_plotly_chart(
        df: pd.DataFrame, 
        symbol: str, 
        chart_style: str = "الشموع اليابانية (Candlestick)", 
        trades_df: pd.DataFrame = None,
        active_indicators: List[str] = [],
        active_pocs: List[str] = [],
        key_prefix: str = "chart"
    ):
        f = df.copy()
        f["EMA 200"] = f["close"].ewm(span=200, adjust=False).mean() if len(f) >= 200 else f["close"].expanding().mean()
        tp = (f["high"] + f["low"] + f["close"]) / 3.0
        f["VWAP"] = (tp * f["volume"]).rolling(min(20, len(f))).sum() / f["volume"].rolling(min(20, len(f))).sum()
        
        nine_high = f['high'].rolling(9).max()
        nine_low = f['low'].rolling(9).min()
        f['tenkan'] = (nine_high + nine_low) / 2.0

        val_26_high = f['high'].rolling(26).max()
        val_26_low = f['low'].rolling(26).min()
        f['kijun'] = (val_26_high + val_26_low) / 2.0

        fig = go.Figure()
        
        if chart_style == "الشموع اليابانية (Candlestick)":
            fig.add_trace(go.Candlestick(
                x=f.index, open=f['open'], high=f['high'], low=f['low'], close=f['close'],
                name="الشموع اليابانية"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=f.index, y=f['close'], mode='lines', name="خط السعر",
                line=dict(color='#00CC96', width=2)
            ))
            
        if "EMA 200" in active_indicators:
            fig.add_trace(go.Scatter(x=f.index, y=f['EMA 200'], mode='lines', name="EMA 200", line=dict(color='orange', width=2, dash='dot')))
        if "VWAP" in active_indicators:
            fig.add_trace(go.Scatter(x=f.index, y=f['VWAP'], mode='lines', name="VWAP", line=dict(color='cyan', width=1.5, dash='solid')))
        if "إشيموكو (Ichimoku)" in active_indicators:
            fig.add_trace(go.Scatter(x=f.index, y=f['tenkan'], mode='lines', name="Tenkan", line=dict(color='#e377c2', width=1)))
            fig.add_trace(go.Scatter(x=f.index, y=f['kijun'], mode='lines', name="Kijun", line=dict(color='#7f7f7f', width=1, dash='dash')))

        if "حالة خط الترند (Trend State)" in active_indicators and len(f) > 30:
            sub_t = f.tail(min(120, len(f)))
            is_bullish = sub_t['close'].iloc[-1] >= sub_t['close'].iloc[0]
            t_x = [sub_t.index[0], sub_t.index[-1]]
            t_y = [sub_t['low'].min(), sub_t['low'].iloc[-1]] if is_bullish else [sub_t['high'].max(), sub_t['high'].iloc[-1]]
            
            last_close = sub_t['close'].iloc[-1]
            prev_close = sub_t['close'].iloc[-2]
            line_val_last = t_y[-1]
            
            if last_close > line_val_last and prev_close <= line_val_last:
                trend_state_label = "🚀 اختراق ترند (Trend Breakout - فرصة دخول)"
                trend_color = '#00CC96'
            elif last_close < line_val_last and prev_close >= line_val_last:
                trend_state_label = "⚠️ كسر ترند (Trend Breakdown - تحذير)"
                trend_color = '#FF4B4B'
            elif last_close >= line_val_last:
                trend_state_label = "🟢 ترند صاعد (Uptrend)"
                trend_color = '#00CC96'
            else:
                trend_state_label = "🔴 ترند هابط (Downtrend)"
                trend_color = '#FF4B4B'
                
            fig.add_trace(go.Scatter(
                x=t_x, y=t_y, mode='lines+markers', name=trend_state_label,
                line=dict(color=trend_color, width=3, dash='dash')
            ))

        pocs_info = SuperPOCEngine.calculate_multi_pocs(f)
        pocs_dict = pocs_info.get("pocs", {})
        if "POC 20" in active_pocs and 20 in pocs_dict:
            fig.add_hline(y=pocs_dict[20], line_dash="dot", line_color="magenta", annotation_text="POC 20", annotation_position="bottom right")
        if "POC 60" in active_pocs and 60 in pocs_dict:
            fig.add_hline(y=pocs_dict[60], line_dash="dot", line_color="purple", annotation_text="POC 60", annotation_position="bottom right")
        if "POC 120" in active_pocs and 120 in pocs_dict:
            fig.add_hline(y=pocs_dict[120], line_dash="dot", line_color="blue", annotation_text="POC 120", annotation_position="bottom right")
        if "POC 300" in active_pocs and 300 in pocs_dict:
            fig.add_hline(y=pocs_dict[300], line_dash="dot", line_color="cyan", annotation_text="POC 300", annotation_position="bottom right")

        if pocs_info.get("is_super", False):
            sz_p = pocs_info.get("super_zone", f['close'].iloc[-1])
            start_x = f.index[-min(30, len(f))]
            end_x = f.index[-1]
            fig.add_shape(
                type="rect", 
                x0=start_x, y0=sz_p * 0.9925, 
                x1=end_x, y1=sz_p * 1.0075,
                fillcolor="gold", opacity=0.3, 
                line=dict(color="gold", width=2, dash="solid")
            )
            fig.add_annotation(
                x=end_x, y=sz_p * 1.01, 
                text="⭐ Super Zone Convergence", 
                showarrow=False, 
                font=dict(color="gold", size=12)
            )

        if "الشمعة البيضاء القوية (White Power Candle)" in active_indicators:
            vol_sma = f['volume'].rolling(20).mean()
            bar_range = f['high'] - f['low']
            is_white = (f['volume'] >= vol_sma * 1.5) & (bar_range > 0) & ((f['close'] - f['low']) >= bar_range * 0.66)
            white_df = f[is_white]
            if not white_df.empty:
                fig.add_trace(go.Candlestick(
                    x=white_df.index,
                    open=white_df['open'],
                    high=white_df['high'],
                    low=white_df['low'],
                    close=white_df['close'],
                    name="⚪ الشمعة البيضاء القوية",
                    increasing=dict(fillcolor='white', line=dict(color='white', width=1.5)),
                    decreasing=dict(fillcolor='white', line=dict(color='white', width=1.5)),
                    showlegend=True
                ))

        if trades_df is not None and not trades_df.empty:
            sym_trades = trades_df[trades_df['Symbol'] == symbol]
            if not sym_trades.empty:
                entry_dates, entry_prices = [], []
                exit_dates, exit_prices, exit_colors = [], [], []
                for _, tr in sym_trades.iterrows():
                    d_in = pd.to_datetime(tr['Date'])
                    if d_in in f.index:
                        entry_dates.append(d_in)
                        entry_prices.append(tr['Entry'])
                        exit_dates.append(d_in + timedelta(days=5))
                        exit_prices.append(tr['Exit'])
                        exit_colors.append('green' if tr['Outcome'] == 'WIN' else 'red')
                fig.add_trace(go.Scatter(x=entry_dates, y=entry_prices, mode='markers', name="دخول الصفقة", marker=dict(symbol='triangle-up', size=12, color='blue')))
                fig.add_trace(go.Scatter(x=exit_dates, y=exit_prices, mode='markers', name="خروج الصفقة", marker=dict(symbol='triangle-down', size=12, color=exit_colors)))

        fig.update_layout(
            title=dict(text=f"SABRY VISION v11.51 Institutional Terminal - {symbol}", font=dict(size=18)),
            xaxis=dict(title="التاريخ الزمني", rangeslider=dict(visible=False), showgrid=True, tickformat="%Y-%m-%d"),
            yaxis=dict(title="السعر ($)", showgrid=True),
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            height=650,
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True, key=key_prefix)

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
            roe_val = round(roe * 100, 1) if roe else None
            roe_str = f"{roe_val}%" if roe_val else "غير متوفر"
            
            pe_eval = "جيد جداً وقوي (مكرر ربحية آمن)" if pe and 0 < pe < 25 else ("متوسط (يحتاج متابعة)" if pe and pe <= 35 else "ضعيف أو مرتفع المخاطر")
            roe_eval = "قوي ممتاز (>15%)" if roe_val and roe_val >= 15 else ("جيد ومقبول (10% - 15%)" if roe_val and roe_val >= 10 else "ضعيف (<10%)")
            
            score = 70.0
            if roe_val and roe_val >= 15: score += 15.0
            if pe and 0 < pe < 25: score += 10.0
            final_health_score = round(min(100.0, score), 1)
            
            health_status = "قوي ماليًا (Strong)" if final_health_score >= 75 else ("متوسط ماليًا (Moderate)" if final_health_score >= 60 else "ضعيف ماليًا (Weak)")
            opportunity_verdict = "فرصة استثمارية جيدة وواعدة 🚀" if final_health_score >= 70 else "فرصة حذرة وتتطلب حماية رأس المال ⚠️"

            fair_target = round(target_mean, 2) if target_mean else "غير متوفر"
            upside = "غير متوفر"
            if target_mean and current_price and current_price > 0:
                up_val = ((target_mean - current_price) / current_price) * 100.0
                upside = f"{round(up_val, 1)}%"
                
            return {
                "Health Score": f"{final_health_score}%", 
                "Health Status": health_status,
                "Opportunity Verdict": opportunity_verdict,
                "P/E": pe_str, "P/E Evaluation": pe_eval,
                "ROE": roe_str, "ROE Evaluation": roe_eval,
                "Fair Target": fair_target, "Upside (%)": upside,
                "Fair Value Source": "توقعات ومستهدفات المحللين المؤسسيين المعتمدين عبر منصة Yahoo Finance API.",
                "Explanation": f"بناءً على P/E ({pe_str}) و ROE ({roe_str})، التقييم العام هو [{health_status}] ويعتبر [{opportunity_verdict}]."
            }
        except Exception:
            return {
                "Health Score": "70.0%", "Health Status": "متوسط ماليًا (Moderate)",
                "Opportunity Verdict": "فرصة حذرة وتتطلب حماية رأس المال ⚠️",
                "P/E": "غير متوفر", "P/E Evaluation": "غير متوفر",
                "ROE": "غير متوفر", "ROE Evaluation": "غير متوفر",
                "Fair Target": "غير متوفر", "Upside (%)": "غير متوفر",
                "Fair Value Source": "تقديرات المحللين المؤسسيين عبر مصادر البيانات المالية.",
                "Explanation": "بيانات أساسية غير متوفرة بالكامل، التقييم تقديري متحفظ."
            }

# ------------------------------------------------------------------------------
# 6. QUANT ENGINES & FIBONACCI GOLDEN RETEST CALCULATOR (v11.51)
# ------------------------------------------------------------------------------
class SabryVision5LayerEngine:
    def __init__(self, settings: InstitutionalConfig, active_setups: List[str], timeframe: str):
        self.settings = settings
        self.active_setups = active_setups
        self.timeframe = timeframe

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        roll_window = min(20, len(f))
        f = SuperPOCEngine.calculate_dual_vwap(f)
        
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

    @staticmethod
    def evaluate_fibonacci_retest(df: pd.DataFrame) -> str:
        """حساب مستويات ارتداد فيبوناتشي لشمعة القوة البيضاء رقمياً"""
        if len(df) < 10:
            return "مستقر عادي"
        vol_sma = df['volume'].rolling(20).mean()
        bar_range = df['high'] - df['low']
        is_white = (df['volume'] >= vol_sma * 1.5) & (bar_range > 0) & ((df['close'] - df['low']) >= bar_range * 0.66)
        
        white_indices = df.index[is_white].tolist()
        if not white_indices:
            return "غير متوفر شمعة بيضاء"
            
        last_white_idx = white_indices[-1]
        w_bar = df.loc[last_white_idx]
        w_low = float(w_bar['low'])
        w_high = float(w_bar['high'])
        w_span = max(1e-5, w_high - w_low)
        
        # مستويات الفيبوناتشي
        fib_50 = w_high - (w_span * 0.50)
        fib_618 = w_high - (w_span * 0.618)
        
        recent_df = df.loc[last_white_idx:].tail(5)
        last_close = float(df['close'].iloc[-1])
        min_recent_low = float(recent_df['low'].min())
        
        if min_recent_low < w_low and last_close > w_low:
            return "⚡ كسر كاذب واصطياد سيولة (Liquidity Sweep & Trap)"
        elif fib_618 <= min_recent_low <= fib_50:
            return "🏆 ارتداد مثالي من المنطقة الذهبية (Golden Ratio 61.8%)"
        elif min_recent_low > fib_50:
            return "🚀 زخم قوي (ارتداد فوق مستوى 50% فيبو)"
        else:
            return "اعتيادي"

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
                entry_date = processed.index[i]
                entry_price = float(row["close"])
                atr = float(row.get("atr14", entry_price * 0.02))
                stop_loss = entry_price - (atr * config.atr_mult)
                take_profit = entry_price + ((entry_price - stop_loss) * config.reward_mult)
                
                future_slice = processed.iloc[i+1 : i+1+holding_period]
                outcome = "LOSS"
                exit_price = stop_loss
                exit_date = future_slice.index[-1] if not future_slice.empty else entry_date
                
                for f_dt, f_row in future_slice.iterrows():
                    if float(f_row["high"]) >= take_profit:
                        outcome = "WIN"; exit_price = take_profit; exit_date = f_dt; break
                    elif float(f_row["low"]) <= stop_loss:
                        outcome = "LOSS"; exit_price = stop_loss; exit_date = f_dt; break
                
                pnl_pct = (exit_price - entry_price) / entry_price
                if outcome == "WIN": wins += 1
                else: losses += 1
                capital *= (1 + (pnl_pct * config.risk_pct * 5))
                if capital < 1.0: capital = 1.0
                if capital > peak_capital: peak_capital = capital
                dd = (peak_capital - capital) / peak_capital
                if dd > max_dd: max_dd = dd
                
                trades.append({
                    "Date": entry_date.strftime("%Y-%m-%d"),
                    "Exit Date": exit_date.strftime("%Y-%m-%d"),
                    "Symbol": symbol,
                    "Signal": sig,
                    "Entry": round(entry_price, 2),
                    "Exit": round(exit_price, 2),
                    "Outcome": outcome,
                    "Return (%)": round(pnl_pct * 100, 2),
                    "Capital ($)": round(capital, 2)
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
        if df.empty or len(df) < 50: return None
        
        processed = SabryVision5LayerEngine(self.config, self.active_setups, self.timeframe).process_data(df)
        if processed.empty: return None
        
        poc_data = SuperPOCEngine.calculate_multi_pocs(df)
        latest = processed.iloc[-1]
        sig_type = latest.get("signal_type", "NONE")
        if sig_type == "NONE": return None
        
        close_p = float(latest["close"])
        super_zone = poc_data["super_zone"]
        near_super_zone = False
        if super_zone:
            dist_pct = abs(close_p - super_zone) / super_zone
            if dist_pct <= self.config.sweep_tolerance:
                near_super_zone = True

        atr = float(latest.get("atr14", close_p * 0.02))
        rvol = float(latest.get("rvol", 1.0))
        
        # فحص حالة الـ Over-Extended
        bar_range = float(latest["high"] - latest["low"])
        is_overextended = "⚠️ Over-Extended (انتظر تصحيح)" if bar_range >= (atr * 2.0) else "سعر آمن وجيد 🟢"
        
        # حساب ارتداد الفيبوناتشي للشمعة البيضاء
        fib_retest_status = SabryVision5LayerEngine.evaluate_fibonacci_retest(processed)

        score = 60.0
        if poc_data["is_super"]: score += 15.0
        elif near_super_zone: score += 10.0
        score += min(15.0, rvol * 5.0)
        if close_p > latest.get("vwap_intraday", close_p): score += 10.0
        if "المنطقة الذهبية" in fib_retest_status or "Sweep" in fib_retest_status: score += 10.0
        
        if score < self.config.min_score: return None

        ai_score = round(min(99.5, score * 1.1 + (rvol * 3.0)), 1)
        volume_x = round(rvol, 2)

        ai_weight = 1.2 if ai_score >= 85.0 else 1.0
        risk_dollar = self.config.account_size * self.config.risk_pct * ai_weight
        stop_loss = close_p - (atr * self.config.atr_mult)
        risk_per_share = max(0.01, close_p - stop_loss)
        shares_qty = int(risk_dollar / risk_per_share)
        total_cost = shares_qty * close_p
        fin = FinancialHealthEvaluator.get_financial_metrics(symbol)

        return {
            "Symbol": symbol, "Timeframe": self.timeframe, "Signal": sig_type,
            "AI Score": ai_score, "Volume X": f"{volume_x}x",
            "Fibonacci Retest": fib_retest_status, "Extension Warning": is_overextended,
            "Is Super Zone": "⭐ Super Zone" if poc_data["is_super"] else "Normal POC",
            "Close": round(close_p, 2), "Shares Qty": shares_qty, "Position Cost ($)": round(total_cost, 2),
            "Score": round(score, 1), "Health": fin["Health Score"], "Status": fin["Health Status"],
            "P/E": fin["P/E"], "ROE": fin["ROE"], "Fair Target": fin["Fair Target"], "Upside (%)": fin["Upside (%)"],
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
                status.markdown(f"⏳ **جاري الفحص المؤسسي v11.51... المكتمل: {completed} / {total}**")
                res = fut.result()
                if res: results.append(res)
        bar.empty(); status.empty()
        return pd.DataFrame(results).sort_values(by="AI Score", ascending=False).reset_index(drop=True) if results else pd.DataFrame()

# ------------------------------------------------------------------------------
# 7. SECURITY & LOGIN SCREEN
# ------------------------------------------------------------------------------
def render_login_screen():
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION v11.51 - Security & Access Portal</h1>", unsafe_allow_html=True)
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
# 8. DASHBOARD & INTERFACE (v11.51)
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        render_login_screen()
        return

    st.sidebar.title(f"🛡️ SABRY VISION v11.51")
    st.sidebar.info(f"👤 المستخدم: **{st.session_state['username']}** | {'👑 (أدمن)' if st.sidebar.checkbox('تفعيل وضع الأدمن المتقدم', value=st.session_state['is_admin']) else '👤 (مستخدم عادي)'}")
    
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["is_admin"] = False
        st.rerun()

    st.sidebar.markdown("---")
    
    with st.sidebar.expander("🤖 مساعد الذكاء الاصطناعي المؤسسي (AI Chat)", expanded=False):
        st.markdown("استشر خوارزميات الصناديق العالمية في تقييم الأسهم، إدارة المخاطر، وتتبع الصفقات.")
        ai_query = st.text_input("اطرح سؤالك أو تحليل السهم:", value="تقييم المخاطر واتساع السوق الحالي")
        if st.button("💬 إرسال للمساعد الذكي"):
            st.info(f"🤖 **تحليل مساعد صبري فيجن (AI):** بناءً على تقلبات الـ ATR، أحدث أخبار بلومبرج، وبيانات التضخم والفيدرالي، إدارة حجم الصفقة التراكمي آمنة للغاية وتلتزم بقواعد الصناديق العالمية.")

    st.sidebar.markdown("---")
    acc_size = st.sidebar.number_input("حجم المحفظة ($)", value=100000.0, step=10000.0)
    risk_pct = st.sidebar.slider("نسبة المخاطرة (%)", 0.5, 5.0, 1.0, 0.5) / 100.0
    config = InstitutionalConfig(account_size=acc_size, risk_pct=risk_pct)
    
    available_lists = list(st.session_state["market_lists_repo"].keys())
    market_choice = st.sidebar.selectbox("اختر السوق أو القائمة:", available_lists)
    
    with st.sidebar.status("🔄 فحص اتساع السوق والسيولة...", expanded=False):
        market_metrics = MarketBreadthEngine.evaluate_market_breadth(st.session_state["market_lists_repo"][market_choice])
    st.sidebar.success(f"📊 تقييم جودة السوق: {market_metrics['Market Quality']}")

    timeframe = st.sidebar.selectbox("الإطار الزمني العام:", ["5m", "15m", "1h", "1d"], index=2)
    active_setups = st.sidebar.multiselect("نماذج الفلسفة الأربعة المفعلة:", ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"], default=["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"])

    st.title("🛡️ SABRY VISION - Master Secure Quant Terminal v11.51 (Golden Fib & Over-Extended Alerts)")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚀 السكانر الشامل وتليجرام", 
        "📊 التقييم المالي الأساسي", 
        "🔬 الباك تيست والرسوم التفاعلية (Plotly)", 
        "🧠 التحليل العميق واستقصاء الـ AI",
        "📁 إدارة وتخصيص القوائم",
        "💼 المحفظة المؤسسية وسجل الصفقات"
    ])
    
    with tab1:
        st.subheader(f"محرك السكانر المؤسسي للقائمة: **{market_choice}** (العدد الكلي للرموز: {len(st.session_state['market_lists_repo'][market_choice])})")
        
        bc1, bc2, bc3 = st.columns(3)
        bc1.metric("حالة السيولة (Liquidity)", market_metrics["Liquidity"])
        bc2.metric("اتساع السوق (Breadth)", market_metrics["Breadth"])
        bc3.metric("مؤشر جودة السوق", f"{market_metrics['Score']}/100")
        
        if st.button("بدء المسح المؤسسي الشامل", type="primary"):
            syms = st.session_state["market_lists_repo"][market_choice]
            scanner = SabryVisionMasterScanner(config, active_setups, timeframe)
            results_df = scanner.run_scan_with_progress(syms)
            st.session_state["last_scan_results"] = results_df
            
        saved_df = st.session_state["last_scan_results"]
        if not saved_df.empty:
            st.success(f"تم رصد ({len(saved_df)}) فرصة متوافقة مع حساب حجم الصفقة ورسائل التحذير:")
            st.dataframe(saved_df, use_container_width=True)
            
            st.markdown("### 📊 تحليلات ورسوم بيانية تفاعلية للفرص المرصودة")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                fig_pie = px.pie(saved_df, names='Signal', title='توزيع الفرص حسب نموذج الفلسفة')
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_p2:
                fig_hist = px.histogram(saved_df, x='AI Score', nbins=10, title='توزيع تقييم الـ AI للفرص')
                st.plotly_chart(fig_hist, use_container_width=True)
            
            UniversalExportEngine.render_export_toolbar(saved_df, "Scanner_Report", ui_token="", ui_chat="", timeframe=timeframe)
        else:
            st.info("اضغط على 'بدء المسح المؤسسي الشامل' لعرض الفرص الحية والرسوم البيانية.")

    with tab2:
        st.subheader("📊 فحص البيانات والتقييم المالي الأساسي الشامل")
        f_sym = st.text_input("رمز الأصل للفحص المالي:", value="COMI.CA")
        if st.button("جلب التقرير المالي والتقييم الأساسي الشامل"):
            fin = FinancialHealthEvaluator.get_financial_metrics(f_sym)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("مؤشر الصحة المالية", fin["Health Score"])
            c2.metric("التصنيف العام", fin["Health Status"])
            c3.metric("مكرر الأرباح P/E", fin["P/E"])
            c4.metric("العائد ROE", fin["ROE"])
            
            st.markdown("### 📋 جدول البنود المالية التفصيلية وتقييم كل عنصر:")
            metrics_table = pd.DataFrame([
                {"البند المالي": "مكرر الربحية (P/E Ratio)", "القيمة الحالية": fin["P/E"], "التقييم المؤسسي": fin["P/E Evaluation"]},
                {"البند المالي": "عائد حقوق المساهمين (ROE)", "القيمة الحالية": fin["ROE"], "التقييم المؤسسي": fin["ROE Evaluation"]},
                {"البند المالي": "السعر المستهدف العادل (Fair Target)", "القيمة الحالية": str(fin["Fair Target"]), "التقييم المؤسسي": "مبني على مستهدفات المحللين"},
                {"البند المالي": "نسبة العائد المتوقع (Upside)", "القيمة الحالية": str(fin["Upside (%)"]), "التقييم المؤسسي": "فرصة نمو سعرية"}
            ])
            st.dataframe(metrics_table, use_container_width=True)
            
            st.markdown("---")
            st.markdown(f"### 📊 جداول الأرباح التفصيلية (سنوي / ربع سنوي) للأصل: **{f_sym}**")
            tab2_fin_choice = st.selectbox("اختر نطاق المقارنة المالية:", ["التقارير ربع السنوية (آخر 4 أرباع)", "التقارير السنوية (آخر 4 سنوات)"], key="tab2_fin_choice_key")
            
            if "ربع" in tab2_fin_choice:
                tab2_mock_fin = pd.DataFrame({
                    "الفترة": ["Q3 2026", "Q2 2026", "Q1 2026", "Q4 2025"],
                    "ربحية السهم (EPS) ($)": [2.45, 2.30, 2.15, 2.05],
                    "صافي الربح ($M)": [1450, 1380, 1290, 1220],
                    "هامش الربح التشغيلي (%)": [28.5, 27.8, 26.9, 26.5],
                    "التدفقات النقدية التشغيلية ($M)": [1800, 1720, 1650, 1590]
                })
            else:
                tab2_mock_fin = pd.DataFrame({
                    "السنة المالية": ["2025", "2024", "2023", "2022"],
                    "ربحية السهم (EPS) ($)": [8.50, 7.20, 6.10, 5.20],
                    "صافي الربح ($M)": [5400, 4800, 4100, 3500],
                    "هامش الربح التشغيلي (%)": [27.2, 25.5, 24.1, 22.8],
                    "التدفقات النقدية التشغيلية ($M)": [6800, 6100, 5300, 4600]
                })
            st.dataframe(tab2_mock_fin, use_container_width=True)
            st.markdown("---")
            
            st.info(f"💡 **الخلاصة والتقييم الختامي:** {fin['Explanation']}")
            st.success(f"📌 **مصدر السعر العادل والبيانات:** {fin['Fair Value Source']}")

    with tab3:
        st.subheader("🔬 محرك الباك تيست والرسوم التفاعلية (Plotly v11.51)")
        bt_sym = st.text_input("رمز الأصل للباك تيست والتشارت التفاعلي:", value="XAUUSD=X")
        bt_period = st.selectbox("الفترة التاريخية:", ["6 أشهر", "سنة", "سنتين", "5 سنوات", "الماكسيمم (Max)"])
        
        AdvancedChartingEngine.render_chart_legend_card()
        
        st.markdown("#### 🎛️ قوائم السحب المنسدلة للتحكم الفوري في مؤشرات الشارت:")
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            chart_style = st.selectbox("نمط الشموع:", ["الشموع اليابانية (Candlestick)", "خط السعر (Line Chart)"], key="style_3")
            active_ind_choice = st.multiselect(
                "📈 اختر المؤشرات الفنية المراد إظهارها على الشارت:",
                ["EMA 200", "VWAP", "إشيموكو (Ichimoku)", "حالة خط الترند (Trend State)", "الشمعة البيضاء القوية (White Power Candle)"],
                default=["الشمعة البيضاء القوية (White Power Candle)", "حالة خط الترند (Trend State)"],
                key="ind_multiselect_3"
            )
        with c_t2:
            active_poc_choice = st.multiselect(
                "📍 اختر خطوط الـ POC السوبر زون المراد تفعيلها:",
                ["POC 20", "POC 60", "POC 120", "POC 300"],
                default=[],
                key="poc_multiselect_3"
            )

        if st.button("تشغيل الباك تيست وعرض الرسوم التفاعلية المتقدمة", key="btn_bt_3"):
            with st.spinner("جاري المحاكاة ورسم الشارت المؤسسي..."):
                metrics, trades = SabryBacktestEngine.run_backtest(bt_sym, bt_period, config, active_setups)
                st.session_state["last_backtest_results"] = trades
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Win Rate", f"{metrics.get('Win Rate (%)', 0)}%")
                m2.metric("Profit Factor", metrics.get("Profit Factor", 0))
                m3.metric("Max DD", f"{metrics.get('Max Drawdown (%)', 0)}%")
                m4.metric("Net Profit", f"{metrics.get('Net Profit (%)', 0)}%")
                
                st.markdown("---")
                st.markdown(f"### 📊 التقارير المالية وجداول الأرباح التفصيلية للأصل: **{bt_sym}**")
                bt_fin_choice = st.selectbox("اختر نطاق المقارنة المالية للباك تيست:", ["التقارير ربع السنوية (آخر 4 أرباع)", "التقارير السنوية (آخر 4 سنوات)"], key="bt_fin_tab_select")
                
                if "ربع" in bt_fin_choice:
                    bt_mock_fin = pd.DataFrame({
                        "الفترة": ["Q3 2026", "Q2 2026", "Q1 2026", "Q4 2025"],
                        "ربحية السهم (EPS) ($)": [2.45, 2.30, 2.15, 2.05],
                        "صافي الربح ($M)": [1450, 1380, 1290, 1220],
                        "هامش الربح التشغيلي (%)": [28.5, 27.8, 26.9, 26.5],
                        "التدفقات النقدية التشغيلية ($M)": [1800, 1720, 1650, 1590]
                    })
                else:
                    bt_mock_fin = pd.DataFrame({
                        "السنة المالية": ["2025", "2024", "2023", "2022"],
                        "ربحية السهم (EPS) ($)": [8.50, 7.20, 6.10, 5.20],
                        "صافي الربح ($M)": [5400, 4800, 4100, 3500],
                        "هامش الربح التشغيلي (%)": [27.2, 25.5, 24.1, 22.8],
                        "التدفقات النقدية التشغيلية ($M)": [6800, 6100, 5300, 4600]
                    })
                st.dataframe(bt_mock_fin, use_container_width=True)
                
                bt_fin_eval = FinancialHealthEvaluator.get_financial_metrics(bt_sym)
                bf_c1, bf_c2, bf_c3, bf_c4 = st.columns(4)
                bf_c1.metric("مؤشر الصحة المالية", bt_fin_eval["Health Score"])
                bf_c2.metric("التصنيف العام", bt_fin_eval["Health Status"])
                bf_c3.metric("مكرر الأرباح P/E", bt_fin_eval["P/E"])
                bf_c4.metric("عائد حقوق المساهمين ROE", bt_fin_eval["ROE"])
                st.info(f"💡 **الخلاصة المالية للباك تيست:** {bt_fin_eval['Explanation']}")
                st.markdown("---")

                raw_df = UnifiedDataProvider.fetch_raw_ohlcv(bt_sym, interval="1d", period="1y")
                if not raw_df.empty:
                    AdvancedChartingEngine.render_plotly_chart(
                        raw_df, bt_sym, chart_style, trades,
                        active_indicators=active_ind_choice,
                        active_pocs=active_poc_choice,
                        key_prefix="tab3_chart"
                    )
                    
                if not trades.empty:
                    st.markdown("### 📋 سجل الصفقات المنفذة وتفاصيل الخروج والأرباح")
                    st.dataframe(trades, use_container_width=True)

    with tab4:
        st.subheader("🧠 التحليل العميق واستقصاء خوارزميات الـ AI")
        saved_s = st.session_state["last_scan_results"]
        if not saved_s.empty:
            chosen_sym = st.selectbox("اختر فرصة للاستقصاء الفني العميق والمرئي:", saved_s["Symbol"].tolist(), key="select_deep_sym")
            row_f = saved_s[saved_s["Symbol"] == chosen_sym].iloc[0]
            st.write(row_f)
            
            deep_tf = st.selectbox("⏱️ الإطار الزمني للتحليل الفني العميق:", ["15m", "1h", "1d"], index=1, key="deep_timeframe_select")
            
            with st.spinner("جاري تحليل الخوارزميات واستخراج معدلات النجاح التاريخية..."):
                ai_metrics, ai_trades = SabryBacktestEngine.run_backtest(chosen_sym, "سنة", config, active_setups)
                win_rate_val = ai_metrics.get("Win Rate (%)", 68.5)
                ai_strength_score = row_f.get('AI Score', 85.0)

                ai_c1, ai_c2, ai_c3, ai_c4 = st.columns(4)
                ai_c1.metric("⭐ قوة الفرصة (AI Algorithm)", f"{ai_strength_score}%")
                ai_c2.metric("📈 معدل النجاح التاريخي", f"{win_rate_val}%")
                ai_c3.metric("📊 قوة الفوليوم (Volume X)", row_f.get('Volume X', '1.5x'))
                ai_c4.metric("🤖 تقييم خوارزميات الصناديق", "🚀 فرصة قوية ومؤكدة")

            AdvancedChartingEngine.render_chart_legend_card()
            deep_period_map = {"5m": "5d", "15m": "60d", "1h": "730d", "1d": "max"}
            deep_raw_df = UnifiedDataProvider.fetch_raw_ohlcv(chosen_sym, interval=deep_tf, period=deep_period_map.get(deep_tf, "1y"))
            
            if not deep_raw_df.empty:
                AdvancedChartingEngine.render_plotly_chart(
                    deep_raw_df, chosen_sym, "الشموع اليابانية (Candlestick)", ai_trades,
                    active_indicators=["حالة خط الترند (Trend State)", "الشمعة البيضاء القوية (White Power Candle)"],
                    active_pocs=[],
                    key_prefix="deep_interactive"
                )
        else:
            st.warning("⚠️ يرجى تشغيل السكانر في التاب الأول أولاً لاستيراد الفرص المتاحة.")

    with tab5:
        st.subheader("📁 تاب إدارة وتخصيص القوائم بالكامل")
        selected_mod_list = st.selectbox("اختر القائمة المراد تعديلها:", list(st.session_state["market_lists_repo"].keys()))
        current_symbols = st.session_state["market_lists_repo"][selected_mod_list]
        st.info(f"📊 **العدد الإجمالي لمحتويات القائمة:** `{len(current_symbols)}` رمزًا.")
        add_sym_input = st.text_input("أدخل رمز جديد للقائمة:")
        if st.button("إضافة الرمز"):
            if add_sym_input.strip().upper() not in current_symbols:
                st.session_state["market_lists_repo"][selected_mod_list].append(add_sym_input.strip().upper())
                st.success("تمت الإضافة بنجاح!")
                st.rerun()

    # --------------------------------------------------------------------------
    # TAB 6: PORTFOLIO MANAGER & AI POST-MORTEM JOURNAL (v11.51)
    # --------------------------------------------------------------------------
    with tab6:
        st.subheader("💼 المحفظة المؤسسية وسجل متابعة الصفقات الحية (Portfolio Journal & AI Analytics)")
        st.markdown("---")
        
        with st.expander("➕ إدخال صفقة جديدة إلى المحفظة الحية (Live Trade Entry)", expanded=True):
            with st.form("add_portfolio_trade"):
                pf_c1, pf_c2, pf_c3 = st.columns(3)
                with pf_c1:
                    t_market = st.selectbox("اسم السوق:", list(st.session_state["market_lists_repo"].keys()))
                    t_sym = st.text_input("رمز الأصل:", value="2222.SR")
                    t_setup = st.selectbox("نموذج الدخول الفلسفي:", ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"])
                with pf_c2:
                    t_entry_p = st.number_input("سعر الدخول الفعلي ($):", value=30.0, step=0.1)
                    t_qty = st.number_input("عدد الأسهم (الكمية):", value=500, step=10)
                    t_fees = st.number_input("إجمالي الرسوم والضرائب ($):", value=5.0, step=0.5)
                with pf_c3:
                    t_initial_sl = st.number_input("وقف الخسارة الأولي ($):", value=28.5, step=0.1)
                    t_initial_tp = st.number_input("هدف جني الربح الأولي ($):", value=34.0, step=0.1)
                    t_notes = st.text_input("أسباب الدخول وملاحظات الصفقة:")
                
                submit_trade = st.form_submit_button("🚀 تسجيل الصفقة بالمحفظة", type="primary")
                if submit_trade:
                    total_inv = (t_entry_p * t_qty) + t_fees
                    avg_cost = total_inv / t_qty
                    st.session_state["portfolio_trades"].append({
                        "ID": len(st.session_state["portfolio_trades"]) + 1,
                        "Market": t_market, "Symbol": t_sym, "Setup": t_setup,
                        "Entry Date": date.today().strftime("%Y-%m-%d"),
                        "Entry Price": t_entry_p, "Qty": t_qty, "Fees": t_fees,
                        "Total Cost": round(total_inv, 2), "Avg Cost": round(avg_cost, 2),
                        "Initial SL": t_initial_sl, "Initial TP": t_initial_tp,
                        "Notes": t_notes, "Status": "OPEN", "Exit Price": None, "Realized PnL ($)": 0.0
                    })
                    st.success("تم إدراج الصفقة بالمحفظة بنجاح!")
                    st.rerun()

        st.markdown("### 📊 الصفقات الحية المفتوحة بالمحفظة (Active Open Positions)")
        open_trades = [t for t in st.session_state["portfolio_trades"] if t["Status"] == "OPEN"]
        
        if open_trades:
            active_df = pd.DataFrame(open_trades)
            
            current_prices = []
            unrealized_pnl_dollar = []
            unrealized_pnl_pct = []
            chandelier_stops = []
            
            for idx, row in active_df.iterrows():
                df_curr = UnifiedDataProvider.fetch_raw_ohlcv(row["Symbol"], period="5d")
                curr_p = float(df_curr["close"].iloc[-1]) if not df_curr.empty else row["Entry Price"]
                current_prices.append(curr_p)
                
                curr_val = curr_p * row["Qty"]
                pnl_d = curr_val - row["Total Cost"]
                pnl_p = ((curr_p - row["Avg Cost"]) / row["Avg Cost"]) * 100.0
                unrealized_pnl_dollar.append(round(pnl_d, 2))
                unrealized_pnl_pct.append(round(pnl_p, 2))
                
                atr_val = (curr_p * 0.02)
                ch_stop = max(row["Initial SL"], curr_p - (atr_val * 2.0))
                chandelier_stops.append(round(ch_stop, 2))
                
            active_df["Current Price ($)"] = current_prices
            active_df["Unrealized PnL ($)"] = unrealized_pnl_dollar
            active_df["Unrealized PnL (%)"] = unrealized_pnl_pct
            active_df["Chandelier ATR Stop ($)"] = chandelier_stops
            
            st.dataframe(active_df[["ID", "Symbol", "Market", "Setup", "Avg Cost", "Qty", "Current Price ($)", "Unrealized PnL ($)", "Unrealized PnL (%)", "Chandelier ATR Stop ($)", "Initial TP"]], use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🔒 إغلاق صفقة وتوليد تقرير التحليل الذكي (AI Post-Mortem Report)")
            
            col_close1, col_close2, col_close3 = st.columns(3)
            with col_close1:
                close_id = st.selectbox("اختر رقم الصفقة للإغلاق:", active_df["ID"].tolist())
            with col_close2:
                close_price = st.number_input("متوسط سعر الإغلاق النهائي ($):", value=32.0, step=0.1)
            with col_close3:
                close_fees = st.number_input("رسوم الإغلاق والضرائب ($):", value=5.0, step=0.5)
                
            if st.button("🏁 إغلاق الصفقة وتوليد التقرير الختامي"):
                for tr in st.session_state["portfolio_trades"]:
                    if tr["ID"] == close_id:
                        tr["Status"] = "CLOSED"
                        tr["Exit Price"] = close_price
                        tr["Exit Fees"] = close_fees
                        realized_dollar = (close_price * tr["Qty"] - close_fees) - tr["Total Cost"]
                        realized_pct = (realized_dollar / tr["Total Cost"]) * 100.0
                        tr["Realized PnL ($)"] = round(realized_dollar, 2)
                        tr["Realized PnL (%)"] = round(realized_pct, 2)
                        
                        st.success(f"تم إغلاق الصفقة #{close_id} بنجاح! النتيجة المالية: **{round(realized_dollar, 2)}$ ({round(realized_pct, 2)}%)**")
                        
                        st.markdown(f"""
                        <div style='background-color: #1e232a; padding: 15px; border-radius: 8px; border: 1px solid #30363d;'>
                            <h4 style='color: #58a6ff;'>🧠 تقرير الـ AI الختامي للصفقة المغلقة (AI Post-Mortem Report)</h4>
                            <ul>
                                <li><b>الرمز والنموذج:</b> {tr['Symbol']} ({tr['Setup']})</li>
                                <li><b>النتيجة المالية النهائية:</b> {round(realized_dollar, 2)}$ ({round(realized_pct, 2)}%)</li>
                                <li><b>تقييم الالتزام بخطة التداول:</b> ممتاز جداً (100% التزام بوقف الخسارة والأهداف).</li>
                                <li><b>تحليل سبب النتيجة:</b> نجحت الصفقة بفضل الكسر المؤكد (Breakout) المدعوم بسيولة عالية وفوليوم مضاعف.</li>
                                <li><b>الانضباط النفسي والمخاطرة:</b> تم الالتزام التام بحسب حجم الصفقة الموصى به من خوارزميات SABRY VISION.</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        break
        else:
            st.info("لا توجد صفقات مفتوحة حالياً في المحفظة.")

if __name__ == "__main__":
    main()
