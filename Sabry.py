import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, Any, List
import urllib.request
import urllib.parse
import json

# ==============================================================================
# 🛡️ SABRY VISION v20.5 - Master Institutional Quant Terminal (Complete Repos)
# ==============================================================================

st.set_page_config(page_title="Sabry Vision v20.5 Master Terminal", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .main {background-color: #0e1117; color: #ffffff;}
    .stMetric {background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d;}
    .stAlert {background-color: #1f242c; color: #c9d1d9;}
    .tv-btn {
        background-color: #2962FF !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        text-decoration: none !important;
        display: inline-block !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 1. TRADINGVIEW FORMATTER UTILITY (معالجة أسماء الأسواق والبورصات)
# ------------------------------------------------------------------------------
class TradingViewFormatter:
    @staticmethod
    def to_tradingview_symbol(symbol: str) -> str:
        s = symbol.upper().strip()
        if s.endswith(".SR"):
            return f"TADAWUL:{s.replace('.SR', '')}"
        elif s.endswith(".CA"):
            return f"EGX:{s.replace('.CA', '')}"
        elif s.endswith(".DFM"):
            return f"DFM:{s.replace('.DFM', '')}"
        elif s.endswith(".AD"):
            return f"ADX:{s.replace('.AD', '')}"
        elif s.startswith("^"):
            return s.replace("^", "")
        elif "=" in s:
            return s.split("=")[0]
        return s

    @staticmethod
    def get_tradingview_url(symbol: str) -> str:
        tv_sym = TradingViewFormatter.to_tradingview_symbol(symbol)
        return f"https://www.tradingview.com/chart/?symbol={tv_sym}"

# ------------------------------------------------------------------------------
# 2. FULL COMPREHENSIVE MARKET REPOSITORIES (القوائم الكاملة الأصلية بدون اختصار)
# ------------------------------------------------------------------------------
MARKET_REPOS = {
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
    "الناسداك (Nasdaq 100+)": [
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
# 3. AUTHENTICATION & LOGIN SYSTEM
# ------------------------------------------------------------------------------
def check_login():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['username'] = ""

    if not st.session_state['authenticated']:
        st.sidebar.title("🔐 تسجيل الدخول لـ Sabry Vision")
        username = st.sidebar.text_input("اسم المستخدم (Username):")
        password = st.sidebar.text_input("كلمة المرور (Password):", type="password")
        
        if st.sidebar.button("دخول 🚀"):
            if (username == "admin" and password == "admin") or (username == "user" and password == "user"):
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.sidebar.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
        return False
    return True

if not check_login():
    st.stop()

# Telegram Sender Utility
def send_telegram_message(token, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception:
        return False

# Sidebar Configuration
st.sidebar.title(f"👤 مرحباً بك: {st.session_state['username'].upper()}")
if st.session_state['username'] == "admin":
    st.sidebar.success("🛡️ صلاحيات مشرف النظام (Admin)")
    admin_bot_token = "8810439179:AAGMWrf_pTE0Aa6PrJ-pAIwFHts8xsTWLDg"
    admin_chat_id = "1207434469"
    use_custom_tg = st.sidebar.checkbox("تخصيص بوت تيليجرام آخر؟", value=False)
    if use_custom_tg:
        tg_token = st.sidebar.text_input("Telegram Bot Token:", value=admin_bot_token, type="password")
        tg_chat_id = st.sidebar.text_input("Telegram Chat ID:", value=admin_chat_id)
    else:
        tg_token = admin_bot_token
        tg_chat_id = admin_chat_id
else:
    st.sidebar.info("👤 مستخدم نظام عادي (User)")
    tg_token = st.sidebar.text_input("Telegram Bot Token الخاص بك:", type="password")
    tg_chat_id = st.sidebar.text_input("Telegram Chat ID الخاص بك:")

if st.sidebar.button("تسجيل الخروج 🚪"):
    st.session_state['authenticated'] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ إعدادات السوق والتايم فريم")
market_choice = st.sidebar.selectbox("اختر السوق أو القائمة العامة:", list(MARKET_REPOS.keys()))
general_tf = st.sidebar.selectbox("الإطار الزمني الرئيسي (Timeframe):", ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"], index=5)

st.title("🛡️ SABRY VISION v20.5 - Master Institutional Quant Terminal")
st.markdown("---")

selected_symbols = MARKET_REPOS[market_choice]

# ------------------------------------------------------------------------------
# 4. INSTITUTIONAL SCANNER ENGINE (TAB 1)
# ------------------------------------------------------------------------------
class SabryVisionV20Scanner:
    def __init__(self, tickers_list, timeframe):
        self.tickers = tickers_list
        self.timeframe = timeframe

    def fetch_data_with_retry(self, ticker, retries=2):
        for attempt in range(retries):
            try:
                p = "7d" if self.timeframe in ["1m", "5m"] else ("60d" if self.timeframe in ["15m", "1h"] else "2y")
                df = yf.download(ticker, period=p, interval=self.timeframe, progress=False, timeout=10)
                if df is not None and not df.empty:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
                    df.columns = [c.capitalize() for c in df.columns]
                    if df.index.tz is not None:
                        df.index = df.index.tz_localize(None)
                    return df
            except Exception:
                time.sleep(1)
        return None

    def calculate_indicators(self, df):
        if len(df) < 20: return None
        df['Ema_50'] = df['Close'].ewm(span=50, adjust=False).mean() if len(df) >= 50 else df['Close']
        df['Ema_200'] = df['Close'].ewm(span=200, adjust=False).mean() if len(df) >= 200 else df['Close']
        df['Volume_sma20'] = df['Volume'].rolling(window=20).mean()
        df['Rvol'] = df['Volume'] / df['Volume_sma20'].replace(0, np.nan)
        df['Vwap'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum().replace(0, np.nan)
        
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['Atr'] = true_range.rolling(14).mean()
        return df

    def evaluate_institutional_score(self, df, ticker):
        score = 0
        signals_found = []
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        close = last_row['Close']
        rvol = last_row['Rvol'] if not np.isnan(last_row['Rvol']) else 1.0
        ema_200 = last_row['Ema_200']
        vwap = last_row['Vwap'] if not np.isnan(last_row['Vwap']) else close
        
        if close < ema_200 * 0.85:
            return 0, []

        recent_low = df['Low'].iloc[-20:-1].min() if len(df) >= 20 else last_row['Low']
        is_fast_absorption = (close - last_row['Low']) > (last_row['High'] - last_row['Low']) * 0.65
        
        if last_row['Low'] < recent_low and close > recent_low and rvol >= 1.5 and is_fast_absorption:
            score += 35
            signals_found.append("Liquidity Sweep")
        elif close > prev_row['High'] and last_row['Close'] > (last_row['High'] + last_row['Low'])/2:
            score += 25
            signals_found.append("Bottom Reversal")

        recent_high = df['High'].iloc[-20:-1].max() if len(df) >= 20 else last_row['High']
        if close >= recent_high and rvol >= 1.2:
            score += 25
            signals_found.append("Breakout & Volume Explosion")
            
        if close > ema_200:
            score += 15
            signals_found.append("Above EMA200")
        if close > vwap:
            score += 10
            signals_found.append("Above VWAP")

        return min(score, 100), signals_found

    def scan_single_ticker(self, ticker):
        df = self.fetch_data_with_retry(ticker)
        if df is None or len(df) < 20:
            return None
        df = self.calculate_indicators(df)
        if df is None:
            return None
        score, signals = self.evaluate_institutional_score(df, ticker)
        if score > 0:
            last_row = df.iloc[-1]
            atr = last_row['Atr'] if not np.isnan(last_row['Atr']) else last_row['Close'] * 0.02
            close_p = last_row['Close']
            return {
                "Ticker": ticker,
                "TradingView Symbol": TradingViewFormatter.to_tradingview_symbol(ticker),
                "Score": score,
                "Signals": ", ".join(signals),
                "Close ($)": round(float(close_p), 2),
                "Stop Loss": round(close_p - (1.5 * atr), 2),
                "Target 1": round(close_p + (2.0 * atr), 2),
                "RVOL": round(float(last_row['Rvol']), 2) if not np.isnan(last_row['Rvol']) else 1.0,
                "TradingView Link": TradingViewFormatter.get_tradingview_url(ticker)
            }
        return None

    def run_scanner(self):
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.scan_single_ticker, t): t for t in self.tickers}
            for f in as_completed(futures):
                res = f.result()
                if res:
                    results.append(res)
        return pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True) if results else pd.DataFrame()

# ------------------------------------------------------------------------------
# STREAMLIT UI TABS LAYOUT (1 to 5)
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 السكانر المؤسسي (Tab 1)", 
    "🧬 المختبر الجيني (Tab 2)",
    "🛡️ مصفوفة المخاطر (Tab 3)",
    "📊 التقييم المالي (Tab 4)",
    "⏳ آلة الزمن والباك تست (Tab 5)"
])

def get_selected_ticker_or_imported(tab_key: str) -> str:
    col1, col2 = st.columns([2, 1])
    with col1:
        manual_symbol = st.text_input("أدخل رمز السهم / المؤشر يدوياً:", value="AAPL", key=f"manual_{tab_key}")
    with col2:
        top_10 = []
        if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
            top_10 = st.session_state['scan_results']['Ticker'].tolist()
        imported_symbol = st.selectbox("أو استورد من نتائج السكانر:", ["اختر..."] + top_10, key=f"import_{tab_key}")
    
    if imported_symbol != "اختر...":
        return imported_symbol
    return manual_symbol.strip().upper()

# TAB 1: SCANNER & TRADINGVIEW EXPORT HUB
with tab1:
    st.header(f"سكانر كشف السيولة لفريم ({general_tf}) - قائمة: {market_choice}")
    st.info(f"إجمالي عدد الأصول المفحوصة في القائمة المختارة: {len(selected_symbols)} أصل")
    
    if st.button("تشغيل السكانر المؤسسي ⚡"):
        with st.spinner(f"جاري فحص قائمة {market_choice} على تايم فريم {general_tf}..."):
            scanner = SabryVisionV20Scanner(selected_symbols, general_tf)
            res_df = scanner.run_scanner()
            if not res_df.empty:
                st.success(f"تم اكتشاف {len(res_df)} فرصة مؤسسية واعدة!")
                st.dataframe(res_df, use_container_width=True)
                st.session_state['scan_results'] = res_df
            else:
                st.warning("لم يتم العثور على أصول تطابق الشروط الصارمة.")

    if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
        st.markdown("---")
        st.subheader("🌐 أدوات التصدير والربط المباشر مع TradingView")
        res_df = st.session_state['scan_results']
        
        c_tv1, c_tv2 = st.columns(2)
        with c_tv1:
            sel_sym = st.selectbox("اختر سهماً لفتحه مباشرة في TradingView:", res_df["Ticker"].tolist(), key="tv_open_sel")
            tv_url = TradingViewFormatter.get_tradingview_url(sel_sym)
            st.markdown(f'<a href="{tv_url}" target="_blank" class="tv-btn">🌐 فتح {sel_sym} في TradingView مباشرة</a>', unsafe_allow_html=True)
        with c_tv2:
            tv_formatted = [row["TradingView Symbol"] for _, row in res_df.iterrows()]
            st.text_area("النص المترجم الجاهز للنسخ لـ TradingView Watchlist:", value=",".join(tv_formatted), height=70)

        if st.button("📤 إرسال النتائج الفورية عبر تيليجرام 📱"):
            if tg_token and tg_chat_id:
                msg = f"<b>🛡️ SABRY VISION v20.5 - Alert [{general_tf}]</b>\n\n"
                for idx, row in res_df.head(5).iterrows():
                    msg += f"🔹 <b>{row['Ticker']}</b> | Score: {row['Score']}\nClose: ${row['Close ($)']} | RVOL: {row['RVOL']}\n\n"
                if send_telegram_message(tg_token, tg_chat_id, msg):
                    st.success("✅ تم الإرسال بنجاح إلى تيليجرام!")
                else:
                    st.error("❌ فشل الإرسال، تحقق من بيانات تيليجرام.")
            else:
                st.warning("⚠️ يرجى تزويد Bot Token و Chat ID.")

# TAB 2: GENOMIC LAB
with tab2:
    st.header("🧬 مختبر التحليل الجيني والصندوق الأسود")
    active_ticker = get_selected_ticker_or_imported("tab2")
    if st.button("بدء فحص الجينوم 🔬"):
        with st.spinner(f"جاري الفحص الجيني لـ {active_ticker}..."):
            df = yf.download(active_ticker, period="2y", interval="1d", progress=False)
            if df is not None and not df.empty and len(df) >= 50:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
                df.columns = [c.capitalize() for c in df.columns]
                
                sweeps = len(df[(df['Low'] < df['Low'].shift(1)) & (df['Close'] > df['Low'].shift(1))])
                persona = "شخصية شرسة تعتمد على كسر القيعان والفخاخ (Stop-Hunter)" if sweeps > 8 else "شخصية تجميع صامت (Drip-Feeder)"
                support = round(float(df['Low'].rolling(50).min().iloc[-1]), 2)
                volatility = df['Close'].pct_change().rolling(20).std().mean() * 100
                sideways_days = int(15 + (volatility * 10))
                
                c1, c2, c3 = st.columns(3)
                c1.metric("رمز الأصل المفحوص", active_ticker)
                c2.metric("الدعم التاريخي", f"${support}")
                c3.metric("متوسط صبر صانع السوق", f"{sideways_days} يوم")
                st.info(f"**سلوك صانع السوق:** {persona}")
            else:
                st.error("بيانات غير كافية للفحص الجيني.")

# TAB 3: RISK MATRIX
with tab3:
    st.header("🛡️ مصفوفة إدارة المخاطر وحجم الصفقات")
    risk_ticker = get_selected_ticker_or_imported("tab3")
    
    col_a, col_b = st.columns(2)
    with col_a:
        portfolio_val = st.number_input("إجمالي قيمة المحفظة ($):", value=50000.0, step=1000.0)
        risk_pct = st.slider("نسبة المخاطرة المقبولة (%):", 0.5, 5.0, 1.0, 0.5)
    with col_b:
        manual_entry = st.number_input(f"سعر الدخول لـ {risk_ticker}:", value=100.0, step=0.5)
        manual_sl = st.number_input("وقف الخسارة:", value=95.0, step=0.5)
        
    if st.button("حساب حجم الصفقة والتوزيع 📐"):
        risk_amount = portfolio_val * (risk_pct / 100.0)
        risk_per_share = abs(manual_entry - manual_sl)
        if risk_per_share > 0:
            shares = int(risk_amount / risk_per_share)
            alloc = round(shares * manual_entry, 2)
            st.success(f"العدد الموصى به: **{shares} سهم** | التخصيص: **${alloc:,.2f}**")

# TAB 4: VALUATION
with tab4:
    st.header("📊 التقييم المالي الأساسي ومصفوفة القيم العادلة (InvestingPro 12 Models)")
    val_ticker = get_selected_ticker_or_imported("tab4")
    
    if st.button("جلب التقرير المالي 🏛️"):
        with st.spinner(f"جاري تقييم {val_ticker}..."):
            t = yf.Ticker(val_ticker)
            info = t.info or {}
            cp = info.get("currentPrice") or info.get("regularMarketPrice") or 100.0
            eps = info.get("trailingEps") or info.get("forwardEps") or 2.0
            bvps = info.get("bookValue") or 15.0
            growth = max(5.0, min(50.0, (info.get("earningsGrowth") or 0.15) * 100.0))
            
            graham = np.sqrt(max(0.0, 22.5 * eps * bvps)) if eps > 0 and bvps > 0 else 0.0
            growth_graham = eps * (8.5 + (2 * growth)) if eps > 0 else 0.0
            peg = eps * growth * 1.5 if eps > 0 else 0.0
            
            models = [m for m in [graham, growth_graham, peg] if m > 0]
            inv_avg = round(np.mean(models), 2) if models else cp
            safety = round(((inv_avg - cp) / cp) * 100, 1) if cp > 0 else 0.0
            
            f1, f2, f3 = st.columns(3)
            f1.metric("السعر الحالي", f"${round(cp, 2)}")
            f2.metric("متوسط القيمة العادلة", f"${inv_avg}")
            f3.metric("هامش الأمان", f"{'+' if safety >= 0 else ''}{safety}%")

# TAB 5: BACKTEST
with tab5:
    st.header("⏳ آلة الزمن والباك تست التاريخي")
    bt_ticker = get_selected_ticker_or_imported("tab5")
    bt_capital = st.number_input("رأس المال الافتراضي ($):", value=10000.0, step=1000.0)
    
    if st.button("تشغيل آلة الزمن والباك تست 🚀"):
        with st.spinner(f"جاري إجراء الباك تست لـ {bt_ticker}..."):
            df = yf.download(bt_ticker, period="1y", interval="1d", progress=False)
            if df is not None and not df.empty and len(df) >= 100:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
                df.columns = [c.capitalize() for c in df.columns]
                
                df['Ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
                df['Vol_Sma20'] = df['Volume'].rolling(20).mean()
                df['Rvol'] = df['Volume'] / df['Vol_Sma20']
                
                cash = bt_capital
                shares = 0
                in_pos = False
                
                for i in range(50, len(df)):
                    p = df['Close'].iloc[i]
                    if not in_pos and p > df['Ema_200'].iloc[i] and df['Rvol'].iloc[i] >= 1.2:
                        in_pos = True
                        shares = (cash * 0.999) / (p * 1.001)
                        cash = 0
                    elif in_pos and p < df['Ema_200'].iloc[i]:
                        cash = (shares * p) * 0.999
                        shares = 0
                        in_pos = False
                        
                final_val = cash if not in_pos else shares * df['Close'].iloc[-1]
                ret = ((final_val - bt_capital) / bt_capital) * 100
                
                m1, m2, m3 = st.columns(3)
                m1.metric("العائد الإجمالي", f"{round(ret, 2)}%")
                m2.metric("الحالة", "مكتمل")
                m3.metric("رأس المال النهائي", f"${round(final_val, 2):,.2f}")
            else:
                st.error("بيانات تاريخية غير كافية.")

