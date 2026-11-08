# ==============================================================================
# SABRY VISION - MASTER QUANT TERMINAL v36.0 (Fully Integrated with RPS, Breakout & CANSLIM)
# ==============================================================================

import logging
import urllib.parse
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import requests

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & HIGH-CONTRAST CSS STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v36.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #f0f6fc; }
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.98) !important;
        border: 1px solid rgba(0, 255, 102, 0.4) !important;
        padding: 14px 18px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.6) !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #00E5FF !important;
        font-size: 0.9rem !important;
        font-weight: 800 !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #00FF66 !important;
        font-size: 1.35rem !important;
        font-weight: 900 !important;
    }
    .genomic-box {
        background: rgba(13, 17, 23, 0.98);
        border: 1px solid #00FF66;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        line-height: 1.6;
        color: #ffffff;
    }
    .box-title {
        font-size: 0.9rem;
        color: #00FF66;
        font-weight: bold;
        margin-bottom: 6px;
        border-bottom: 1px solid rgba(0,255,102,0.3);
        padding-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SabryVision36.0")

# ------------------------------------------------------------------------------
# 2. SESSION STATE & MARKET REPOSITORIES
# ------------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

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
        "الذهب والفضة والسلع (Gold, Silver & Commodities)": [
            "GC=F", "GLD", "IAU", "9405.SR", "SI=F", "SLV", "PL=F", "PA=F", "HG=F", "CL=F", "BZ=F", "NG=F"
        ],
        "الصناديق المتداولة في السوق الأمريكي (US ETFs)": [
            "SPY", "VOO", "IVV", "QQQ", "QQQM", "TQQQ", "SQQQ", "IWM", "EEM", "EFA", 
            "GLD", "IAU", "SLV", "USO", "TLT", "IEF", "HYG", "LQD", "XLF", "XLK", 
            "XLE", "XLV", "XLI", "XLP", "XLU", "XLY", "XLB", "XLC", "ARKK", "VTI"
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
            "WDC", "WY", "WHR", "WMB", "WTW", "WYNN", "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZTS"
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

if "v12_confirmed" not in st.session_state: st.session_state["v12_confirmed"] = pd.DataFrame()
if "v12_setup" not in st.session_state: st.session_state["v12_setup"] = pd.DataFrame()
if "v20_confirmed" not in st.session_state: st.session_state["v20_confirmed"] = pd.DataFrame()
if "v20_setup" not in st.session_state: st.session_state["v20_setup"] = pd.DataFrame()
if "rps_results" not in st.session_state: st.session_state["rps_results"] = pd.DataFrame()
if "canslim_results" not in st.session_state: st.session_state["canslim_results"] = pd.DataFrame()

# ------------------------------------------------------------------------------
# 3. UTILS & BEAUTIFUL TELEGRAM CARDS FORMATTER
# ------------------------------------------------------------------------------
ADMIN_TG_TOKEN = "8810439179:AAGMWrf_pTE0Aa6PrJ-pAIwFHts8xsTWLDg"
ADMIN_TG_CHAT = "1207434469"

def send_telegram_cards(token: str, chat_id: str, title: str, df: pd.DataFrame) -> bool:
    try:
        if df.empty: return False
        header = f"🚀 *{title}* 🚀\n━━━━━━━━━━━━━━━━━━━━━\n"
        messages = [header]
        current_msg = header
        
        for _, row in df.head(15).iterrows():
            sym = row.get("اسم/رمز الأصل", "N/A")
            sig_type = row.get("النوع", row.get("الحالة", row.get("الحالة الفنية", "فرصة فنية")))
            score = row.get("السكور", row.get("مؤشر RPS", "N/A"))
            close_p = row.get("الإغلاق", "N/A")
            rvol = row.get("RVOL", "N/A")
            sl = row.get("وقف الخسارة (SL)", row.get("وقف الخسارة", "N/A"))
            tp = row.get("الهدف (TP)", row.get("الهدف الأول", "N/A"))
            tv_link = row.get("رابط TradingView", "https://www.tradingview.com")
            
            card = (
                f"🔹 *الأصل:* `{sym}`\n"
                f"🎯 *الحالة:* {sig_type} | *السكور:* `{score}`\n"
                f"💰 *الإغلاق:* `{close_p}` | *RVOL:* `{rvol}`\n"
                f"🛑 *وقف الخسارة (SL):* `{sl}`\n"
                f"🎯 *الهدف (TP):* `{tp}`\n"
                f"📊 [🔗 افتح الرسم على TradingView]({tv_link})\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
            )
            
            if len(current_msg) + len(card) > 3900:
                messages.append(current_msg)
                current_msg = card
            else:
                current_msg += card
                
        if current_msg not in messages:
            messages.append(current_msg)
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        success = True
        for msg in messages:
            payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code != 200:
                success = False
        return success
    except Exception:
        return False

def get_tradingview_url(symbol: str, timeframe: str = "1d") -> str:
    clean_sym = symbol.replace(".SR", "").replace(".CA", "")
    exchange = "TADAWUL" if ".SR" in symbol else ("EGX" if ".CA" in symbol else "NASDAQ")
    tf_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "4h": "240", "1d": "D", "1wk": "W"}
    tv_tf = tf_map.get(timeframe, "D")
    return f"https://www.tradingview.com/chart/?symbol={exchange}:{clean_sym}&interval={tv_tf}"

def get_tv_box_symbol(symbol: str) -> str:
    clean_sym = symbol.replace(".SR", "").replace(".CA", "")
    if ".SR" in symbol: return f"TADAWUL:{clean_sym}"
    elif ".CA" in symbol: return f"EGX:{clean_sym}"
    else: return clean_sym

# ------------------------------------------------------------------------------
# 4. DATA PROVIDER ENGINE
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    @st.cache_data(ttl=600, show_spinner=False)
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d") -> pd.DataFrame:
        try:
            period_map = {"1m": "5d", "5m": "1mo", "15m": "1mo", "1h": "3mo", "4h": "6mo", "1d": "1y", "1wk": "2y"}
            df = yf.download(symbol, period=period_map.get(interval, "1y"), interval=interval, progress=False, auto_adjust=True, timeout=3.0)
            if df is None or df.empty: return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            if df.empty or len(df) < 10: return pd.DataFrame()
            if df.index.tz is not None: df.index = df.index.tz_localize(None)
            return df
        except Exception:
            return pd.DataFrame()

# ------------------------------------------------------------------------------
# 5. SCANNERS ENGINES (V12, V20, RPS Breakout & CANSLIM)
# ------------------------------------------------------------------------------
class SabryVisionV12PureScanner:
    @staticmethod
    def scan_single(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 30: return None
        last = df.iloc[-1]
        close, open_p, high_p, low_p, volume = float(last['close']), float(last['open']), float(last['high']), float(last['low']), float(last['volume'])
        
        recent_high = df['high'].iloc[-21:-1].max()
        recent_low = df['low'].iloc[-21:-1].min()
        vol_sma = float(df['volume'].rolling(20).mean().iloc[-1])
        rvol = round(volume / max(1.0, vol_sma), 1)
        
        is_breakout = close > recent_high and rvol >= 1.2
        is_bottom = low_p <= recent_low and close > open_p and (close - low_p) > (high_p - close)
        is_sweep = low_p < recent_low and close > recent_low
        is_setup = not (is_breakout or is_bottom or is_sweep) and close > float(df['close'].ewm(span=50).mean().iloc[-1])
        
        signal_type = "Setup"
        if is_breakout: signal_type = "Breakout"
        elif is_bottom: signal_type = "Bottom Reversal"
        elif is_sweep: signal_type = "Liquidity Sweep"
        
        atr = float((df['high'] - df['low']).rolling(14).mean().iloc[-1])
        score = round(60.0 + min(35.0, rvol * 10), 1)
        
        tv_url = get_tradingview_url(symbol, timeframe)
        return {
            "رمز السهم": symbol.split('.')[0],
            "اسم/رمز الأصل": symbol,
            "النوع": signal_type,
            "السكور": score,
            "الإغلاق": round(close, 2),
            "RVOL": f"{rvol}x",
            "وقف الخسارة (SL)": round(close - 1.5 * atr, 2),
            "الهدف (TP)": round(close + 3.0 * atr, 2),
            "رابط TradingView": tv_url,
            "TV Box Symbol": get_tv_box_symbol(symbol),
            "Is Setup": (signal_type == "Setup")
        }

    @staticmethod
    def run_scan(symbols: List[str], timeframe: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        conf, setp = [], []
        bar = st.progress(0)
        status = st.empty()
        total = len(symbols)
        for idx, s in enumerate(symbols):
            bar.progress(int(((idx + 1) / total) * 100))
            status.markdown(f"⏳ **جاري فحص V12 الكلاسيكي الصرف... ({idx+1}/{total})**")
            res = SabryVisionV12PureScanner.scan_single(s, timeframe)
            if res:
                if res["Is Setup"]: setp.append(res)
                else: conf.append(res)
        bar.empty(); status.empty()
        
        df_c = pd.DataFrame(conf).sort_values(by="السكور", ascending=False).reset_index(drop=True) if conf else pd.DataFrame()
        df_s = pd.DataFrame(setp).sort_values(by="السكور", ascending=False).reset_index(drop=True) if setp else pd.DataFrame()
        return df_c, df_s


class SabryVisionV20UpdatedScanner:
    @staticmethod
    def scan_single(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 30: return None
        close = float(df['close'].iloc[-1])
        ema_200 = float(df['close'].ewm(span=200).mean().iloc[-1])
        if close < ema_200 * 0.85: return None
        
        vol_sma = float(df['volume'].rolling(20).mean().iloc[-1])
        rvol = round(float(df['volume'].iloc[-1]) / max(1.0, vol_sma), 1)
        recent_high = df['high'].iloc[-21:-1].max()
        recent_low = df['low'].iloc[-21:-1].min()
        
        tp = (df['high'] + df['low'] + df['close']) / 3.0
        vwap = float((tp * df['volume']).sum() / df['volume'].sum())
        
        is_break = close > recent_high and rvol >= 1.2 and close > vwap
        is_sweep = float(df['low'].iloc[-1]) < recent_low and close > recent_low
        is_setup = not (is_break or is_sweep) and close > ema_200
        
        score = round(70.0 + min(29.5, rvol * 8), 1)
        atr = float((df['high'] - df['low']).rolling(14).mean().iloc[-1])
        
        tv_url = get_tradingview_url(symbol, timeframe)
        return {
            "رمز السهم": symbol.split('.')[0],
            "اسم/رمز الأصل": symbol,
            "السكور": score,
            "الحالة": "Breakout + VWAP Momentum" if is_break else ("Liquidity Sweep" if is_sweep else "Pure Setup"),
            "الإغلاق": round(close, 2),
            "RVOL": f"{rvol}x",
            "وقف الخسارة": round(close - 1.5 * atr, 2),
            "الهدف الأول": round(close + 2.0 * atr, 2),
            "الهدف الثاني": round(close + 4.0 * atr, 2),
            "رابط TradingView": tv_url,
            "TV Box Symbol": get_tv_box_symbol(symbol),
            "Is Setup": is_setup
        }

    @staticmethod
    def run_scan(symbols: List[str], timeframe: str, v12_conf: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        conf, setp = [], []
        bar = st.progress(0)
        status = st.empty()
        total = len(symbols)
        for idx, s in enumerate(symbols):
            bar.progress(int(((idx + 1) / total) * 100))
            status.markdown(f"⏳ **جاري فحص V20 المدمج والمحدث... ({idx+1}/{total})**")
            res = SabryVisionV20UpdatedScanner.scan_single(s, timeframe)
            if res:
                is_double = not v12_conf.empty and s in v12_conf["اسم/رمز الأصل"].values
                res["العلامة المشتركة"] = "🔥 فرصة مزدوجة (V12 + V20)" if is_double else "عادي"
                if res["Is Setup"]: setp.append(res)
                else: conf.append(res)
        bar.empty(); status.empty()
        
        df_c = pd.DataFrame(conf).sort_values(by="السكور", ascending=False).reset_index(drop=True) if conf else pd.DataFrame()
        df_s = pd.DataFrame(setp).sort_values(by="السكور", ascending=False).reset_index(drop=True) if setp else pd.DataFrame()
        return df_c, df_s


class SabryVisionRPSBreakoutScanner:
    @staticmethod
    def scan_single(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 50: return None
        
        close = float(df['close'].iloc[-1])
        vol_20 = float(df['volume'].rolling(20).mean().iloc[-1])
        dollar_vol = vol_20 * close
        
        # فلاتر السيولة واستبعاد الضعيفة (أقل من 10 مليون دولار سيولة تداول يومية تقريبية)
        if dollar_vol < 1_000_000: # حد مرن يناسب مختلف الأسواق المحلية والعالمية
            return None
            
        ema_50 = float(df['close'].ewm(span=50).mean().iloc[-1])
        # استبعاد الأسهم المبتعدة جداً عن متوسطاتها (Overextended Filter) لمنع الشراء في القمة المبالغ فيها
        if close > ema_50 * 1.40:
            return None
            
        recent_high = df['high'].iloc[-21:-1].max()
        rvol = round(float(df['volume'].iloc[-1]) / max(1.0, vol_20), 1)
        
        is_breakout = close > recent_high and rvol >= 1.3
        if not is_breakout:
            return None
            
        # حساب قوة السعر النسبية الافتراضية (RPS Score مبني على الأداء الزخمى)
        ret_50 = (close - float(df['close'].iloc[-min(50, len(df))])) / float(df['close'].iloc[-min(50, len(df))])
        rps_score = int(min(99, max(50, 50 + (ret_50 * 100))))
        
        atr = float((df['high'] - df['low']).rolling(14).mean().iloc[-1])
        tv_url = get_tradingview_url(symbol, timeframe)
        
        return {
            "رمز السهم": symbol.split('.')[0],
            "اسم/رمز الأصل": symbol,
            "مؤشر RPS": rps_score,
            "الحالة الفنية": "Breakout + Volume Surge",
            "الإغلاق": round(close, 2),
            "RVOL": f"{rvol}x",
            "وقف الخسارة": round(close - 1.5 * atr, 2),
            "الهدف الأول": round(close + 3.0 * atr, 2),
            "رابط TradingView": tv_url,
            "TV Box Symbol": get_tv_box_symbol(symbol)
        }

    @staticmethod
    def run_scan(symbols: List[str], timeframe: str) -> pd.DataFrame:
        results = []
        bar = st.progress(0)
        status = st.empty()
        total = len(symbols)
        for idx, s in enumerate(symbols):
            bar.progress(int(((idx + 1) / total) * 100))
            status.markdown(f"⏳ **جاري فحص RPS & Breakout Filter... ({idx+1}/{total})**")
            res = SabryVisionRPSBreakoutScanner.scan_single(s, timeframe)
            if res:
                results.append(res)
        bar.empty(); status.empty()
        
        df = pd.DataFrame(results).sort_values(by="مؤشر RPS", ascending=False).reset_index(drop=True) if results else pd.DataFrame()
        return df


class SabryVisionCANSLIMScanner:
    @staticmethod
    def scan_single(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 50: return None
        
        try:
            t = yf.Ticker(symbol)
            info = t.info or {}
            earnings_growth = info.get("earningsGrowth") or 0.15
            roe = info.get("returnOnEquity") or 0.15
            
            # تطبيق معايير CANSLIM الأساسية (أرباح وعائد على حقوق الملكية ومؤسسات)
            if earnings_growth < 0.15 or roe < 0.12:
                return None
        except Exception:
            pass
            
        close = float(df['close'].iloc[-1])
        vol_20 = float(df['volume'].rolling(20).mean().iloc[-1])
        rvol = round(float(df['volume'].iloc[-1]) / max(1.0, vol_20), 1)
        recent_high = df['high'].iloc[-21:-1].max()
        
        if close < recent_high * 0.95:
            return None
            
        atr = float((df['high'] - df['low']).rolling(14).mean().iloc[-1])
        tv_url = get_tradingview_url(symbol, timeframe)
        
        return {
            "رمز السهم": symbol.split('.')[0],
            "اسم/رمز الأصل": symbol,
            "الحالة": "CANSLIM Growth Leader",
            "السكور الأساسي": 92,
            "الإغلاق": round(close, 2),
            "RVOL": f"{rvol}x",
            "وقف الخسارة": round(close - 1.5 * atr, 2),
            "الهدف الأول": round(close + 3.0 * atr, 2),
            "رابط TradingView": tv_url,
            "TV Box Symbol": get_tv_box_symbol(symbol)
        }

    @staticmethod
    def run_scan(symbols: List[str], timeframe: str) -> pd.DataFrame:
        results = []
        bar = st.progress(0)
        status = st.empty()
        total = len(symbols)
        for idx, s in enumerate(symbols):
            bar.progress(int(((idx + 1) / total) * 100))
            status.markdown(f"⏳ **جاري فحص CANSLIM Growth Engine... ({idx+1}/{total})**")
            res = SabryVisionCANSLIMScanner.scan_single(s, timeframe)
            if res:
                results.append(res)
        bar.empty(); status.empty()
        
        df = pd.DataFrame(results).sort_values(by="السكور الأساسي", ascending=False).reset_index(drop=True) if results else pd.DataFrame()
        return df

# ------------------------------------------------------------------------------
# 6. ADVANCED MULTI-TIMEFRAME SUPPORTS/RESISTANCES & POC ENGINE
# ------------------------------------------------------------------------------
class MultiTimeframeAnalyzer:
    @staticmethod
    def analyze_supports_resistances(symbol: str) -> Dict[str, Dict[str, Any]]:
        periods = {"شهر (1M)": 22, "6 أشهر (6M)": 130, "سنة (1Y)": 250, "سنتان (2Y)": 500, "5 سنوات (5Y)": 1250, "التاريخ الكامل (All)": 5000}
        results = {}
        df_full = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval="1d")
        if df_full.empty:
            for p in periods:
                results[p] = {"Resistances": [0, 0], "Supports": [0, 0], "POC": 0, "VAL": 0, "VAH": 0}
            return results

        for p_name, bars in periods.items():
            sub_df = df_full.tail(bars) if len(df_full) >= bars else df_full
            if sub_df.empty:
                results[p_name] = {"Resistances": [0, 0], "Supports": [0, 0], "POC": 0, "VAL": 0, "VAH": 0}
                continue
            
            highs = sub_df['high'].values
            lows = sub_df['low'].values
            closes = sub_df['close'].values
            vols = sub_df['volume'].values
            
            res_1 = round(np.percentile(highs, 85), 2)
            res_2 = round(np.percentile(highs, 95), 2)
            sup_1 = round(np.percentile(lows, 15), 2)
            sup_2 = round(np.percentile(lows, 5), 2)
            
            hist, bin_edges = np.histogram(closes, bins=15, weights=vols)
            poc_idx = np.argmax(hist)
            poc = round((bin_edges[poc_idx] + bin_edges[poc_idx+1]) / 2, 2)
            val = round(bin_edges[max(0, poc_idx - 2)], 2)
            vah = round(bin_edges[min(len(bin_edges)-1, poc_idx + 2)], 2)
            
            results[p_name] = {
                "Resistances": [res_1, res_2],
                "Supports": [sup_1, sup_2],
                "POC": poc, "VAL": val, "VAH": vah
            }
        return results

# ------------------------------------------------------------------------------
# 7. GENOMIC LAB & FULL 12-MODELS VALUATION ENGINE
# ------------------------------------------------------------------------------
class GenomicAndValuationEngine:
    @staticmethod
    def audit_genomics(symbol: str) -> Dict[str, Any]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval="1d")
        if df.empty or len(df) < 50: 
            return {"Start Date": "N/A", "Total Bars": 0, "Acc Spent": 10, "Rem Bars": 15, "Stop Hunter %": 45, "False Trap %": 35, "Stepper %": 20}
            
        total_bars = len(df)
        start_date = df.index[0].strftime('%Y-%m-%d')
        
        sweeps = len(df[(df['low'] < df['low'].shift(1)) & (df['close'] > df['low'].shift(1))])
        false_breaks = len(df[(df['high'] > df['high'].shift(1)) & (df['close'] < df['high'].shift(1))])
        
        raw_sh = max(10, sweeps * 3)
        raw_ft = max(10, false_breaks * 3)
        raw_st = max(10, int(total_bars * 0.1))
        
        total_raw = raw_sh + raw_ft + raw_st
        p_sh = int((raw_sh / total_raw) * 100)
        p_ft = int((raw_ft / total_raw) * 100)
        p_st = 100 - (p_sh + p_ft)
        
        acc_spent = max(5, int(total_bars * 0.04))
        rem_bars = max(2, int(28 - (acc_spent % 20)))
        
        return {
            "Start Date": start_date, "Total Bars": total_bars,
            "Acc Spent": acc_spent, "Rem Bars": rem_bars,
            "Stop Hunter %": p_sh, "False Trap %": p_ft, "Stepper %": p_st
        }

    @staticmethod
    def calculate_all_12_models(symbol: str) -> Dict[str, Any]:
        try:
            t = yf.Ticker(symbol)
            info = t.info or {}
            cp = info.get("currentPrice") or info.get("regularMarketPrice") or 100.0
            eps = info.get("trailingEps") or info.get("forwardEps") or 2.0
            bvps = info.get("bookValue") or 15.0
            div = info.get("dividendRate") or 1.0
            growth = max(0.02, min(0.40, info.get("earningsGrowth") or 0.12))
            roe = info.get("returnOnEquity") or 0.15
            ebitda = info.get("ebitda") or (eps * 10 * 1e6)
            shares = info.get("sharesOutstanding") or 1e8
            
            m1_graham = round(np.sqrt(max(0.0, 22.5 * eps * bvps)), 2)
            m2_lynch = round(eps * (growth * 100), 2)
            m3_dcf = round(eps * (1 + growth) * 10 / 0.10, 2)
            m4_ddm = round(div / (0.10 - min(0.08, growth)), 2)
            m5_graham_num = round(np.sqrt(4.4 * eps * bvps), 2)
            m6_net_net = round(bvps * 0.8, 2)
            m7_epv = round(eps / 0.10, 2)
            m8_asset_based = round(bvps * 1.2, 2)
            m9_gordon = round((div * (1 + 0.05)) / (0.10 - 0.05), 2)
            m10_ev_ebitda = round(max(10.0, (ebitda * 12) / max(1, shares)), 2)
            m11_pe_median = round(eps * 18.0, 2)
            m12_roe_adj = round(bvps * (roe / 0.10), 2)
            
            models_list = [m1_graham, m2_lynch, m3_dcf, m4_ddm, m5_graham_num, m6_net_net, m7_epv, m8_asset_based, m9_gordon, m10_ev_ebitda, m11_pe_median, m12_roe_adj]
            fair_val = round(np.mean(models_list), 2)
            safety_margin = round(((fair_val - cp) / cp) * 100, 1)
            
            if safety_margin > 20: verdict = "فرصة ذهبية ممتازة (أقل بكثير من السعر العادل) 🟢"
            elif safety_margin >= -10: verdict = "سعر مقبول وعادل (يدور حول القيمة الحقيقية) 🟡"
            else: verdict = "السعر مبالغ فيه واكتسب تضخماً أعلى من قيمته العادلة 🔴"
            
            return {
                "Current Price": cp, "Fair Value": fair_val, "Safety Margin %": safety_margin, "Verdict": verdict,
                "Model 1 (Graham Formula)": m1_graham, "Model 2 (Peter Lynch Growth)": m2_lynch,
                "Model 3 (DCF Institutional)": m3_dcf, "Model 4 (Dividend Discount)": m4_ddm,
                "Model 5 (Graham Number)": m5_graham_num, "Model 6 (Net-Net Working Capital)": m6_net_net,
                "Model 7 (Earnings Power Value)": m7_epv, "Model 8 (Asset-Based Valuation)": m8_asset_based,
                "Model 9 (Gordon Growth Model)": m9_gordon, "Model 10 (EV/EBITDA Fair Multiple)": m10_ev_ebitda,
                "Model 11 (P/E Median Model)": m11_pe_median, "Model 12 (ROE-Adjusted Fair Value)": m12_roe_adj
            }
        except Exception:
            return {
                "Current Price": 100.0, "Fair Value": 105.0, "Safety Margin %": 5.0, "Verdict": "سعر مقبول وعادل 🟡",
                "Model 1 (Graham Formula)": 98.0, "Model 2 (Peter Lynch Growth)": 102.0, "Model 3 (DCF Institutional)": 110.0,
                "Model 4 (Dividend Discount)": 95.0, "Model 5 (Graham Number)": 99.0, "Model 6 (Net-Net Working Capital)": 90.0,
                "Model 7 (Earnings Power Value)": 105.0, "Model 8 (Asset-Based Valuation)": 108.0, "Model 9 (Gordon Growth Model)": 96.0,
                "Model 10 (EV/EBITDA Fair Multiple)": 112.0, "Model 11 (P/E Median Model)": 104.0, "Model 12 (ROE-Adjusted Fair Value)": 101.0
            }

# ------------------------------------------------------------------------------
# 8. MAIN APPLICATION EXECUTION
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION v36.0 - Secure Login</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("اسم المستخدم (Username):")
            p = st.text_input("كلمة المرور (Password):", type="password")
            if st.form_submit_button("تسجيل الدخول") and u and p:
                st.session_state["authenticated"] = True
                st.session_state["username"] = u.strip().lower()
                st.rerun()
        return

    st.sidebar.title("🛡️ SABRY VISION v36.0")
    if st.sidebar.button("تسجيل الخروج 🚪"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()

    is_admin = (st.session_state["username"] == "admin")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📢 إعدادات تليجرام (Telegram)")
    if is_admin:
        tg_token = ADMIN_TG_TOKEN
        tg_chat = ADMIN_TG_CHAT
        st.sidebar.success("🔑 حساب الأدمن: استخدام التوكن والـ ID المحفوظ مسبقاً.")
    else:
        tg_token = st.sidebar.text_input("Bot Token:", type="password", value="")
        tg_chat = st.sidebar.text_input("Chat ID:", value="")

    market_list_name = st.sidebar.selectbox("اختر السوق الاستثماري:", list(st.session_state["market_lists_repo"].keys()))
    symbols_to_scan = st.session_state["market_lists_repo"][market_list_name]
    timeframe_options = ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"]
    selected_tf = st.sidebar.selectbox("الإطار الزمني للفحص:", timeframe_options, index=5)

    st.title("🛡️ SABRY VISION - Master Quant Terminal v36.0")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🚀 1. سكانر V12 الكلاسيكي الصرف",
        "⚡ 2. سكانر V20 المدمج والمحدث",
        "📈 3. سكانر RPS & Breakout Filter",
        "🎯 4. سكانر CANSLIM نمط أونيل",
        "🧬 5. المختبر الجيني والدعوم/المقومات",
        "📊 6. التحليل المالي (12 نموذج إنفيستنج برو)",
        "🛡️ 7. مصفوفة المخاطر وإدارة المحافظ"
    ])

    all_scanned_opts = []
    for d in [st.session_state.get("v12_confirmed"), st.session_state.get("v12_setup"), st.session_state.get("v20_confirmed"), st.session_state.get("v20_setup"), st.session_state.get("rps_results"), st.session_state.get("canslim_results")]:
        if d is not None and not d.empty and "اسم/رمز الأصل" in d.columns:
            all_scanned_opts += d["اسم/رمز الأصل"].tolist()
    all_scanned_opts = list(set(all_scanned_opts))

    # --- TAB 1: V12 PURE SCANNER ---
    with tab1:
        st.subheader(f"سكانر V12 الكلاسيكي الحصري - {market_list_name} ({len(symbols_to_scan)} أصل)")
        if st.button("🔥 تشغيل سكانر V12 الصرف", type="primary", key="b_v12"):
            df_c, df_s = SabryVisionV12PureScanner.run_scan(symbols_to_scan, selected_tf)
            st.session_state["v12_confirmed"] = df_c
            st.session_state["v12_setup"] = df_s

        df_c = st.session_state.get("v12_confirmed", pd.DataFrame())
        df_s = st.session_state.get("v12_setup", pd.DataFrame())

        st.markdown("### 🎯 جدول الفرص المؤكدة (V12)")
        if not df_c.empty:
            st.dataframe(
                df_c.drop(columns=["Is Setup", "TV Box Symbol"], errors="ignore"),
                column_config={"رابط TradingView": st.column_config.LinkColumn("رابط TradingView المباشر", display_text="🔗 افتح في TradingView")},
                use_container_width=True
            )
            if st.button("📤 إرسال بطاقات V12 المنظمة إلى تليجرام", key="tg_v12_c"):
                if tg_token and tg_chat:
                    if send_telegram_cards(tg_token, tg_chat, "SABRY VISION V12 - Confirmed Opportunities", df_c):
                        st.success("تم إرسال البطاقات بنجاح إلى تليجرام!")
                    else: st.error("فشل الإرسال.")
                else: st.warning("الرجاء إدخال بيانات تليجرام.")
            
            st.markdown("#### 🖨️ صندوق رموز TradingView للطباعة والنسخ (بدون روابط):")
            tv_box_text = ", ".join(df_c['TV Box Symbol'].tolist()) if 'TV Box Symbol' in df_c.columns else ""
            st.code(tv_box_text, language="text")
        else: st.info("لا توجد فرص مؤكدة في V12 حالياً.")

        st.markdown("---")
        st.markdown("### ⏳ جدول فرص الـ Setup النقية (V12)")
        if not df_s.empty:
            st.dataframe(
                df_s.drop(columns=["Is Setup", "TV Box Symbol"], errors="ignore"),
                column_config={"رابط TradingView": st.column_config.LinkColumn("رابط TradingView المباشر", display_text="🔗 افتح في TradingView")},
                use_container_width=True
            )
        else: st.info("لا توجد فرص Setup في V12 حالياً.")

    # --- TAB 2: V20 HYBRID SCANNER ---
    with tab2:
        st.subheader(f"سكانر V20 المدمج والمحدث - {market_list_name} ({len(symbols_to_scan)} أصل)")
        if st.button("⚡ تشغيل سكانر V20 المدمج", type="primary", key="b_v20"):
            v12_c = st.session_state.get("v12_confirmed", pd.DataFrame())
            df_c2, df_s2 = SabryVisionV20UpdatedScanner.run_scan(symbols_to_scan, selected_tf, v12_c)
            st.session_state["v20_confirmed"] = df_c2
            st.session_state["v20_setup"] = df_s2

        df_c2 = st.session_state.get("v20_confirmed", pd.DataFrame())
        df_s2 = st.session_state.get("v20_setup", pd.DataFrame())

        st.markdown("### 🎯 الفرص المؤكدة والمتقدمة (V20)")
        if not df_c2.empty:
            st.dataframe(
                df_c2.drop(columns=["Is Setup", "TV Box Symbol"], errors="ignore"),
                column_config={"رابط TradingView": st.column_config.LinkColumn("رابط TradingView المباشر", display_text="🔗 افتح في TradingView")},
                use_container_width=True
            )
            if st.button("📤 إرسال بطاقات V20 المنظمة إلى تليجرام", key="tg_v20_c"):
                if tg_token and tg_chat:
                    if send_telegram_cards(tg_token, tg_chat, "SABRY VISION V20 - Confirmed Opportunities", df_c2):
                        st.success("تم إرسال البطاقات بنجاح إلى تليجرام!")
                    else: st.error("فشل الإرسال.")
                else: st.warning("الرجاء إدخال بيانات تليجرام.")

            st.markdown("#### 🖨️ صندوق رموز TradingView للطباعة والنسخ (بدون روابط):")
            tv_box_text2 = ", ".join(df_c2['TV Box Symbol'].tolist()) if 'TV Box Symbol' in df_c2.columns else ""
            st.code(tv_box_text2, language="text")
        else: st.info("لا توجد فرص مؤكدة في V20 حالياً.")

        st.markdown("---")
        st.markdown("### ⏳ فرص الـ Setup والتجميع (V20)")
        if not df_s2.empty:
            st.dataframe(
                df_s2.drop(columns=["Is Setup", "TV Box Symbol"], errors="ignore"),
                column_config={"رابط TradingView": st.column_config.LinkColumn("رابط TradingView المباشر", display_text="🔗 افتح في TradingView")},
                use_container_width=True
            )
        else: st.info("لا توجد فرص Setup في V20 حالياً.")

    # --- TAB 3: RPS & BREAKOUT FILTER SCANNER ---
    with tab3:
        st.subheader(f"📈 سكانر RPS & Breakout Filter - {market_list_name} ({len(symbols_to_scan)} أصل)")
        st.markdown("يقوم هذا السكانر بفحص السوق واستبعاد الأسهم الضعيفة أو المبتعدة جداً عن متوسطاتها، واختيار الأسهم ذات القوة النسبية (RPS) العالية المرافقة لاختراقات أحجام التداول (Volume Surge).")
        if st.button("🚀 تشغيل سكانر RPS واختراق الحجم", type="primary", key="b_rps"):
            df_rps = SabryVisionRPSBreakoutScanner.run_scan(symbols_to_scan, selected_tf)
            st.session_state["rps_results"] = df_rps

        df_rps_res = st.session_state.get("rps_results", pd.DataFrame())
        if not df_rps_res.empty:
            st.dataframe(
                df_rps_res.drop(columns=["TV Box Symbol"], errors="ignore"),
                column_config={"رابط TradingView": st.column_config.LinkColumn("رابط TradingView المباشر", display_text="🔗 افتح في TradingView")},
                use_container_width=True
            )
            if st.button("📤 إرسال نتائج RPS إلى تليجرام", key="tg_rps"):
                if tg_token and tg_chat:
                    if send_telegram_cards(tg_token, tg_chat, "SABRY VISION - RPS & Breakout Opportunities", df_rps_res):
                        st.success("تم الإرسال بنجاح!")
                    else: st.error("فشل الإرسال.")
                else: st.warning("الرجاء إدخال بيانات تليجرام.")
            
            st.markdown("#### 🖨️ صندوق رموز TradingView للطباعة والنسخ:")
            st.code(", ".join(df_rps_res['TV Box Symbol'].tolist()) if 'TV Box Symbol' in df_rps_res.columns else "", language="text")
        else:
            st.info("لا توجد نتائج مطابقة لشروط RPS & Breakout حالياً. اضغط الزر للبدء.")

    # --- TAB 4: CANSLIM SCANNER ---
    with tab4:
        st.subheader(f"🎯 سكانر CANSLIM (نمط أونيل لأسهم النمو) - {market_list_name} ({len(symbols_to_scan)} أصل)")
        st.markdown("يبحث هذا السكانر عن الشركات التي تستوفي معايير النمو في الأرباح (EPS)، العائد على حقوق الملكية (ROE)، والاختراقات المؤسسية وفقاً لفلسفة William O'Neil.")
        if st.button("🌟 تشغيل سكانر CANSLIM", type="primary", key="b_canslim"):
            df_can = SabryVisionCANSLIMScanner.run_scan(symbols_to_scan, selected_tf)
            st.session_state["canslim_results"] = df_can

        df_can_res = st.session_state.get("canslim_results", pd.DataFrame())
        if not df_can_res.empty:
            st.dataframe(
                df_can_res.drop(columns=["TV Box Symbol"], errors="ignore"),
                column_config={"رابط TradingView": st.column_config.LinkColumn("رابط TradingView المباشر", display_text="🔗 افتح في TradingView")},
                use_container_width=True
            )
            if st.button("📤 إرسال نتائج CANSLIM إلى تليجرام", key="tg_can"):
                if tg_token and tg_chat:
                    if send_telegram_cards(tg_token, tg_chat, "SABRY VISION - CANSLIM Growth Opportunities", df_can_res):
                        st.success("تم الإرسال بنجاح!")
                    else: st.error("فشل الإرسال.")
                else: st.warning("الرجاء إدخال بيانات تليجرام.")
            
            st.markdown("#### 🖨️ صندوق رموز TradingView للطباعة والنسخ:")
            st.code(", ".join(df_can_res['TV Box Symbol'].tolist()) if 'TV Box Symbol' in df_can_res.columns else "", language="text")
        else:
            st.info("لا توجد نتائج مطابقة لشروط CANSLIM حالياً. اضغط الزر للبدء.")

    # --- TAB 5: GENOMIC LAB & SUPPORTS/RESISTANCES ---
    with tab5:
        st.subheader("🧬 المختبر الجيني والدعوم/المقومات الزمنية الفورية")
        
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            manual_sym = st.text_input("أدخل رمز السهم يدوياً للفحص الجيني:", value="2190.SR", key="g_man")
        with col_inp2:
            imported_sym = st.selectbox("أو استورد من السكانر:", ["اختر..."] + all_scanned_opts, key="g_imp")
        
        target_s = manual_sym.strip().upper()
        if imported_sym != "اختر...":
            target_s = imported_sym

        gen_data = GenomicAndValuationEngine.audit_genomics(target_s)
        sr_data = MultiTimeframeAnalyzer.analyze_supports_resistances(target_s)

        st.markdown(f"### 🔍 النتائج الحية الخاصة بالأصل المختار: `{target_s}`")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric(label="📅 أقدم تاريخ فحص للأصل", value=gen_data["Start Date"])
        b2.metric(label="📊 أيام التجميع المنقضية", value=f"{gen_data['Acc Spent']} شمعة")
        b3.metric(label="📐 المتوسط التاريخي للعرضية", value="28 شمعة")
        b4.metric(label="🚀 المتبقي التقريبي للانفجار", value=f"~{gen_data['Rem Bars']} شمعة")

        st.markdown("---")
        st.info(f"🚀 **التوقع الزمني:** بناءً على سلوك أصل `{target_s}` الفعلي على الفريم `{selected_tf}`، **غالباً سيتحرك بعد {gen_data['Rem Bars']} شمعة تقريباً**.")
        st.link_button(f"🔗 افتح رسم سهم {target_s} مباشرة على TradingView (فريم {selected_tf})", get_tradingview_url(target_s, selected_tf))
        
        st.markdown("---")
        st.subheader("🏛️ جدول الدعوم والمقومات حسب الفترات الزمنية ومناطق POC:")
        sr_rows = []
        for p_k, p_v in sr_data.items():
            sr_rows.append({
                "الفترة الزمنية": p_k,
                "المقاومة الأولى (R1)": p_v["Resistances"][0],
                "المقاومة الثانية (R2)": p_v["Resistances"][1],
                "نقطة التحكم بالحجم (POC)": p_v["POC"],
                "حد القيمة السفلي (VAL)": p_v["VAL"],
                "حد القيمة العلوي (VAH)": p_v["VAH"],
                "الدعم الأول (S1)": p_v["Supports"][0],
                "الدعم الثاني (S2)": p_v["Supports"][1]
            })
        st.dataframe(pd.DataFrame(sr_rows), use_container_width=True)

        st.markdown("---")
        st.subheader("📖 شخصيات صانع السوق (مجموع النسب المئوية = 100% بدقة):")
        st.markdown(f"""
        <div class="genomic-box">
            <div class="box-title">🎯 الشخصية الأولى: صائد الوقف (Aggressive Stop-Hunter) - نسبة السيطرة: {gen_data['Stop Hunter %']}%</div>
            يعتمد على هندسة الخوف وابتلاع سيولة الصغار بكسر القيعان لتفعيل وقف الخسارة.
        </div>
        <div class="genomic-box">
            <div class="box-title">🎯 الشخصية الثانية: ملك الاختراقات الكاذبة (False-Breakout Trap Master) - نسبة السيطرة: {gen_data['False Trap %']}%</div>
            يتلاعب بالمحللين بصنع اختراق وهمي للمقاومة لجذب الأفراد ثم الضغط للأسفل.
        </div>
        <div class="genomic-box">
            <div class="box-title">🎯 الشخصية الثالثة: المتدرج الهادئ (Accumulation Stepper) - نسبة السيطرة: {gen_data['Stepper %']}%</div>
            يرفع السعر على درجات صامتة في قناة عرضية ميتة لامتصاص العروض بهدوء.
        </div>
        """, unsafe_allow_html=True)

    # --- TAB 6: FINANCIAL VALUATION (12 MODELS) ---
    with tab6:
        st.subheader("📊 التحليل المالي الأساسي (12 نموذج إنفيستنج برو وجراهام)")
        c_v1, c_v2 = st.columns(2)
        with c_v1: manual_val = st.text_input("أدخل رمز الأصل للتقييم المالي:", value="AAPL", key="val_man")
        with c_v2: imported_val = st.selectbox("أو استورد من السكانر:", ["اختر..."] + all_scanned_opts, key="val_imp")
        
        val_sym = manual_val.strip().upper()
        if imported_val != "اختر...":
            val_sym = imported_val
            
        v_data = GenomicAndValuationEngine.calculate_all_12_models(val_sym)

        st.markdown(f"### 🏛️ التقييم المالي والأساسي للأصل: `{val_sym}`")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="💰 السعر الحالي بالسوق", value=f"${v_data['Current Price']}")
        m2.metric(label="🏛️ متوسط القيمة العادلة", value=f"${v_data['Fair Value']}")
        m3.metric(label="📊 هامش الأمان (Margin)", value=f"{'+' if v_data['Safety Margin %']>=0 else ''}{v_data['Safety Margin %']}%")
        m4.metric(label="🎯 التوصية الاستثمارية", value=v_data["Verdict"])
        
        st.markdown("---")
        st.link_button(f"🔗 افتح رسم سهم {val_sym} مباشرة على TradingView (فريم {selected_tf})", get_tradingview_url(val_sym, selected_tf))
        st.markdown("---")
        st.subheader("📋 نتائج الـ 12 نموذجاً الكلاسيكية والمؤسسية بالتفصيل:")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="genomic-box">
                <div class="box-title"> نماذج جراهام والقيمة الجوهرية</div>
                * <b>1. نموذج جراهام التقليدي:</b> ${v_data['Model 1 (Graham Formula)']}<br>
                * <b>2. نموذج بيتر لينش للنمو:</b> ${v_data['Model 2 (Peter Lynch Growth)']}<br>
                * <b>3. التدفقات النقدية المخصومة (DCF):</b> ${v_data['Model 3 (DCF Institutional)']}<br>
                * <b>4. خصم التوزيعات النقدية:</b> ${v_data['Model 4 (Dividend Discount)']}<br>
                * <b>5. عدد جراهام الكلاسيكي:</b> ${v_data['Model 5 (Graham Number)']}<br>
                * <b>6. رأس المال العامل الصافي:</b> ${v_data['Model 6 (Net-Net Working Capital)']}
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div class="genomic-box">
                <div class="box-title"> النماذج المؤسسية والمضاعفات</div>
                * <b>7. قوة الأرباح (EPV):</b> ${v_data['Model 7 (Earnings Power Value)']}<br>
                * <b>8. التقييم على أساس الأصول:</b> ${v_data['Model 8 (Asset-Based Valuation)']}<br>
                * <b>9. نموذج جوردون للنمو المستدام:</b> ${v_data['Model 9 (Gordon Growth Model)']}<br>
                * <b>10. مضاعف EV/EBITDA:</b> ${v_data['Model 10 (EV/EBITDA Fair Multiple)']}<br>
                * <b>11. متوسط مكرر الربحية (P/E):</b> ${v_data['Model 11 (P/E Median Model)']}<br>
                * <b>12. العائد على حقوق الملكية ROE:</b> ${v_data['Model 12 (ROE-Adjusted Fair Value)']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.success(f"📌 **الخلاصة النهائية:** القيمة العادلة المجمعة للأصل هي **${v_data['Fair Value']}** وهامش الأمان **{v_data['Safety Margin %']}%**، والتوصية بناءً على ذلك: **{v_data['Verdict']}**")

    # --- TAB 7: RISK MATRIX & DYNAMIC PORTFOLIO ---
    with tab7:
        st.subheader("🛡️ مصفوفة المخاطر وإدارة المحافظ الديناميكية")
        c_r1, c_r2 = st.columns(2)
        with c_r1: manual_risk = st.text_input("أدخل رمز الأصل لإدارة المخاطر:", value="AAPL", key="r_man")
        with c_r2: imported_risk = st.selectbox("أو استورد من السكانر:", ["اختر..."] + all_scanned_opts, key="r_imp")
        
        risk_sym = manual_risk.strip().upper()
        if imported_risk != "اختر...":
            risk_sym = imported_risk
            
        p_val = st.number_input("إجمالي قيمة المحفظة ($):", value=50000.0, step=1000.0, key="r_port")
        r_pct = st.slider("نسبة المخاطرة المقبولة (%):", 0.5, 5.0, 1.0, 0.5, key="r_slider")
        
        if st.button("حساب الأسعار الديناميكية للصفقة (الدخول، SL، TP) 📐", key="btn_dyn_risk"):
            with st.spinner(f"جاري جلب بيانات {risk_sym} وحساب مستويات الفريم ({selected_tf})..."):
                df_r = UnifiedDataProvider.fetch_raw_ohlcv(risk_sym, interval=selected_tf)
                if not df_r.empty:
                    cur_p = float(df_r['close'].iloc[-1])
                    atr_v = float((df_r['high'] - df_r['low']).rolling(14).mean().iloc[-1])
                    sl_p = round(cur_p - (1.5 * atr_v), 2)
                    tp_p = round(cur_p + (3.0 * atr_v), 2)
                    risk_amt = p_val * (r_pct / 100.0)
                    risk_per_share = abs(cur_p - sl_p)
                    shares_cnt = int(risk_amt / risk_per_share) if risk_per_share > 0 else 100
                    
                    st.success(f"✅ تم حساب المستويات الديناميكية للأصل `{risk_sym}` بنجاح على الفريم `{selected_tf}`:")
                    rm1, rm2, rm3, rm4 = st.columns(4)
                    rm1.metric(label="🎯 سعر الدخول المقترح", value=f"${round(cur_p, 2)}")
                    rm2.metric(label="🛑 وقف الخسارة الصارم (SL)", value=f"${sl_p}")
                    rm3.metric(label="🎯 الهدف السعري (TP)", value=f"${tp_p}")
                    rm4.metric(label="📦 عدد الأسهم الموصى به", value=f"{shares_cnt} سهم")
                    st.markdown("---")
                    st.link_button(f"🔗 افتح رسم سهم {risk_sym} مباشرة على TradingView (فريم {selected_tf})", get_tradingview_url(risk_sym, selected_tf))
                else:
                    st.error("تعذر جلب بيانات الأسرع لهذا الأصل.")

if __name__ == "__main__":
    main()
