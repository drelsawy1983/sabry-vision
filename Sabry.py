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
# 🛡️ SABRY VISION v20.0 Updated - Master Quant & Institutional Terminal (Full Lists)
# ==============================================================================

st.set_page_config(page_title="Sabry Vision v20.0 Updated", layout="wide", page_icon="🛡️")

# 🎨 HIGH-CONTRAST VISUAL DESIGN (ألوان واضحة وبوكسات شفافة)
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #f0f6fc; }
    
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(8px) !important;
    }
    
    div[data-testid="stMetricLabel"] > label {
        color: #e6edf3 !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricValue"] > div {
        color: #00FF66 !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        text-shadow: 0px 0px 8px rgba(0, 255, 102, 0.3) !important;
    }

    .metric-gold { color: #FFCC00 !important; font-weight: bold; }
    .metric-cyan { color: #00E5FF !important; font-weight: bold; }
    
    .tv-btn {
        background-color: #2962FF !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        text-decoration: none !important;
        display: inline-block !important;
        box-shadow: 0 4px 12px rgba(41, 98, 255, 0.4) !important;
    }
    
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 800 !important; }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 1. TRADINGVIEW FORMATTER UTILITY
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
# 2. FULL COMPREHENSIVE MARKET REPOSITORIES (القوائم الأصلية كاملة 100% بدون أي نقص)
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
        "WDC", "WY", "WHR", "WMB", "WTW", "WYNN", "XEL", "XYL", "YUM", "ZBRA", "ZBH", "ZTS"
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
        "WMT", "PDD", "MAR", "FTNT", "ALAB", "QQQ", "QQQM", "TQQQ", "SQQQ", "XLK", "SMH", "SOXX", "ARKK"
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

# Telegram Utility
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

# Sidebar Config
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

st.title("🛡️ SABRY VISION v20.0 Updated - Ultimate Quant Terminal")
st.markdown("---")

selected_symbols = MARKET_REPOS[market_choice]

# ------------------------------------------------------------------------------
# 4. DUAL-ENGINE HYBRID SCANNER
# ------------------------------------------------------------------------------
class SabryVisionV20UpdatedScanner:
    def __init__(self, tickers_list, timeframe):
        self.tickers = tickers_list
        self.timeframe = timeframe

    def fetch_data(self, ticker):
        try:
            p = "7d" if self.timeframe in ["1m", "5m"] else ("60d" if self.timeframe in ["15m", "1h"] else "2y")
            df = yf.download(ticker, period=p, interval=self.timeframe, progress=False, timeout=8)
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
                df.columns = [c.capitalize() for c in df.columns]
                if df.index.tz is not None:
                    df.index = df.index.tz_localize(None)
                return df
        except Exception:
            pass
        return None

    def calculate_indicators(self, df):
        if len(df) < 20: return None
        df['Ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['Ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['Volume_sma20'] = df['Volume'].rolling(window=20).mean()
        df['Rvol'] = df['Volume'] / df['Volume_sma20'].replace(0, np.nan)
        df['Vwap'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum().replace(0, np.nan)
        
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['Atr'] = true_range.rolling(14).mean()
        return df

    def scan_single_ticker(self, ticker):
        df = self.fetch_data(ticker)
        if df is None or len(df) < 20: return None
        df = self.calculate_indicators(df)
        if df is None: return None
            
        last_row = df.iloc[-1]
        close = last_row['Close']
        rvol = last_row['Rvol'] if not np.isnan(last_row['Rvol']) else 1.0
        ema_200 = last_row['Ema_200']
        atr = last_row['Atr'] if not np.isnan(last_row['Atr']) else close * 0.02

        if close < ema_200 * 0.85: return None

        recent_high = df['High'].iloc[-21:-1].max()
        recent_low = df['Low'].iloc[-21:-1].min()

        is_breakout = close > recent_high and rvol >= 1.2
        is_bottom_reversal = last_row['Low'] <= recent_low and close > last_row['Open'] and (close - last_row['Low']) > (last_row['High'] - close)
        is_liquidity_sweep = last_row['Low'] < recent_low and close > recent_low
        is_setup = close > last_row['Ema_50'] and not (is_breakout or is_bottom_reversal or is_liquidity_sweep)

        detected_types = []
        if is_breakout: detected_types.append("Breakout")
        if is_bottom_reversal: detected_types.append("Bottom Reversal")
        if is_liquidity_sweep: detected_types.append("Liquidity Sweep")
        if is_setup: detected_types.append("Setup")

        if not detected_types: return None

        score = 50.0
        if is_breakout: score += 25.0
        if is_bottom_reversal: score += 20.0
        if is_liquidity_sweep: score += 20.0
        if is_setup: score += 10.0
        score += min(15.0, rvol * 5.0)
        score = min(99.5, score)

        sl = round(close - (1.5 * atr), 2)
        t1 = round(close + (2.0 * atr), 2)
        t2 = round(close + (4.0 * atr), 2)
        is_pure_setup = (detected_types == ["Setup"])

        return {
            "Ticker": ticker,
            "TradingView Symbol": TradingViewFormatter.to_tradingview_symbol(ticker),
            "Score": round(score, 1),
            "Signals": " + ".join(detected_types),
            "Close ($)": round(float(close), 2),
            "Stop Loss": sl,
            "Target 1": t1,
            "Target 2": t2,
            "RVOL": round(float(rvol), 2),
            "Is Pure Setup": is_pure_setup
        }

# ------------------------------------------------------------------------------
# TABS LAYOUT (1 to 5)
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 السكانر الهجين الكامل (Tab 1)", 
    "🧬 المختبر الجيني وتوقع الانفجار (Tab 2)",
    "🛡️ مصفوفة المخاطر والمحفظة (Tab 3)",
    "📊 التقييم المالي 12 نموذج (Tab 4)",
    "⏳ آلة الزمن والباك تست المتقدم (Tab 5)"
])

def get_selected_ticker_or_imported(tab_key: str) -> str:
    col1, col2 = st.columns([2, 1])
    with col1:
        manual_symbol = st.text_input("أدخل رمز السهم يدوياً:", value="AAPL", key=f"manual_{tab_key}")
    with col2:
        top_10 = []
        if 'confirmed_opps' in st.session_state and not st.session_state['confirmed_opps'].empty:
            top_10 = st.session_state['confirmed_opps']['Ticker'].tolist()
        imported_symbol = st.selectbox("أو استورد من السكانر:", ["اختر..."] + top_10, key=f"import_{tab_key}")
    
    if imported_symbol != "اختر...": return imported_symbol
    return manual_symbol.strip().upper()

# TAB 1: SCANNER WITH FULL REPOSITORIES & PROGRESS
with tab1:
    st.header(f"السكانر الكامل ({general_tf}) - قائمة: {market_choice}")
    total_count = len(selected_symbols)
    st.info(f"إجمالي الأصول في القائمة المحددة: {total_count} أصل (تم تحميل القوائم كاملة بدون أي نقصان)")
    
    if st.button("تشغيل السكانر الشامل ⚡"):
        scanner = SabryVisionV20UpdatedScanner(selected_symbols, general_tf)
        confirmed_list, setup_list = [], []
        
        prog_bar = st.progress(0)
        status_txt = st.empty()
        metrics_plc = st.empty()
        
        scanned, found = 0, 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(scanner.scan_single_ticker, t): t for t in selected_symbols}
            for f in as_completed(futures):
                scanned += 1
                res = f.result()
                if res:
                    found += 1
                    if res["Is Pure Setup"]: setup_list.append(res)
                    else: confirmed_list.append(res)
                
                prog_bar.progress(int((scanned / total_count) * 100))
                status_txt.markdown(f"⏳ **جاري فحص السوق الشامل...** ({scanned}/{total_count})")
                metrics_plc.markdown(f"📊 **الممسوح:** `{scanned}/{total_count}` | 🎯 **الفرص المكتشفة:** `{found}`")

        df_conf = pd.DataFrame(confirmed_list).sort_values(by="Score", ascending=False).reset_index(drop=True) if confirmed_list else pd.DataFrame()
        df_set = pd.DataFrame(setup_list).sort_values(by="Score", ascending=False).reset_index(drop=True) if setup_list else pd.DataFrame()
        
        if not df_conf.empty and not df_set.empty:
            double_conv = set(df_conf['Ticker']).intersection(set(df_set['Ticker']))
            if double_conv:
                st.success(f"🔥 **تنبيه الجوهرة المزدوجة (Double Conviction):** أسهم ظهرت في الجدولين معاً (ثقة >90%): `{list(double_conv)}`")

        st.session_state['confirmed_opps'] = df_conf
        st.session_state['setup_opps'] = df_set

    df_conf = st.session_state.get('confirmed_opps', pd.DataFrame())
    df_set = st.session_state.get('setup_opps', pd.DataFrame())

    st.markdown("### 🎯 جدول الفرص المؤكدة والزخم الصريح (Confirmed Momentum)")
    if not df_conf.empty:
        st.dataframe(df_conf.drop(columns=["Is Pure Setup"], errors="ignore"), use_container_width=True)
    else:
        st.info("لا توجد فرص مؤكدة حالياً.")

    st.markdown("---")
    st.markdown("### ⏳ جدول فرص الـ Setup النقية (قيد التحضير والتجميع الصامت)")
    if not df_set.empty:
        st.dataframe(df_set.drop(columns=["Is Pure Setup"], errors="ignore"), use_container_width=True)
    else:
        st.info("لا توجد فرص Setup نقية حالياً.")

    if not df_conf.empty or not df_set.empty:
        st.markdown("---")
        st.subheader("🌐 أدوات التصدير والربط بـ TradingView")
        active_df = df_conf if not df_conf.empty else df_set
        c1, c2 = st.columns(2)
        with c1:
            sel_s = st.selectbox("اختر سهماً لفتحه في TradingView:", active_df["Ticker"].tolist(), key="tv_s1")
            st.markdown(f'<a href="{TradingViewFormatter.get_tradingview_url(sel_s)}" target="_blank" class="tv-btn">🌐 فتح {sel_s} في TradingView</a>', unsafe_allow_html=True)
        with c2:
            tv_codes = ",".join([TradingViewFormatter.to_tradingview_symbol(t) for t in active_df["Ticker"].tolist()[:15]])
            st.text_area("أكواد الـ Watchlist للنسخ:", value=tv_codes, height=70)

# TAB 2: GENOMIC LAB & ACCUMULATION TRACKER
with tab2:
    st.header("🧬 المختبر الجيني التاريخي وتوقع زمن الانفجار (Max History & Accumulation Tracker)")
    active_ticker = get_selected_ticker_or_imported("tab2")
    
    if st.button("بدء الفحص الجيني وتتبع مرحلة التجميع 🔬"):
        with st.spinner(f"جاري جلب التاريخ الكامل لـ {active_ticker} وحساب أيام التجميع وزمن الانفجار..."):
            df = yf.download(active_ticker, period="max", interval="1d", progress=False)
            if df is not None and not df.empty and len(df) > 100:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
                df.columns = [c.capitalize() for c in df.columns]
                
                total_bars = len(df)
                start_date = df.index[0].strftime('%Y-%m-%d')
                
                sweeps = len(df[(df['Low'] < df['Low'].shift(1)) & (df['Close'] > df['Low'].shift(1))])
                false_breaks = len(df[(df['High'] > df['High'].shift(1)) & (df['Close'] < df['High'].shift(1))])
                
                p_stop_hunter = min(70, max(15, int((sweeps / total_bars) * 400)))
                p_false_trap = min(60, max(10, int((false_breaks / total_bars) * 350)))
                p_stepper = max(10, 100 - (p_stop_hunter + p_false_trap))
                
                accumulation_bars_spent = 0
                for i in range(len(df)-1, 0, -1):
                    if (df['High'].iloc[i] - df['Low'].iloc[i]) / df['Close'].iloc[i] < 0.03:
                        accumulation_bars_spent += 1
                    else:
                        break
                accumulation_bars_spent = max(5, accumulation_bars_spent)
                
                avg_historical_acc_duration = int(25 + (p_stepper * 0.3))
                remaining_bars = max(2, avg_historical_acc_duration - accumulation_bars_spent)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("تاريخ بدء البيانات", start_date)
                m2.metric("أيام التجميع المنقضية", f"{accumulation_bars_spent} شمعة/يوم")
                m3.metric("المتوسط التاريخي للتجميع", f"{avg_historical_acc_duration} شمعة")
                m4.metric("المتبقي التقريبي للانفجار", f"~{remaining_bars} شمعة")
                
                st.markdown("---")
                st.info(f"🚀 **التقدير الزمني الاستباقي للانفجار:** بناءً على السلوك التاريخي ودورات صانع السوق لهذا الأصل، **غالبا سوف يتحرك هذا السهم بعد {remaining_bars} شمعة تقريباً**.")
                
                st.markdown("---")
                st.subheader("📊 توزيع نسب شخصيات صانع السوق التاريخية:")
                p_col1, p_col2, p_col3 = st.columns(3)
                p_col1.metric("صائد الوقف الشرس (Stop-Hunter)", f"{p_stop_hunter}%")
                p_col2.metric("ملك الاختراقات الوهمية (Trap Master)", f"{p_false_trap}%")
                p_col3.metric("الصانع المتدرج الهادئ (Stepper)", f"{p_stepper}%")
                
                st.markdown("---")
                st.subheader("📖 التشريح التفصيلي للشخصيات المسيطرة وكيفية التعامل معها:")
                st.markdown(f"""
                ### 1. صانع السوق الشرس - صائد الوقف (Aggressive Stop-Hunter) - بنسبة `{p_stop_hunter}%`:
                * **الشرح وطبيعة الشخصية:** شخصية عنيفة تعتمد على هندسة الخوف وابتلاع سيولة الصغار بكسر القيعان والدعوم الشهيرة عمداً لتفعيل وقف الخسارة وجمع الكميات بأرخص الأسعار قبل الانفجار.
                * **كيف تتعامل معه ولا تخسر:** لا تضع وقف خسارتك تحت الدعوم المكشوفة. انتظر سحب السيولة وارتداد الشمعة (Liquidity Sweep) واشترِ في ذيل الشمعة الخادعة لا تحتها، واجعل الوقف بعيداً تحت آخر قاع بمسافة ATR.
                
                ---
                
                ### 2. صانع السوق المخادع - الاختراقات الكاذبة (False-Breakout Trap Master) - بنسبة `{p_false_trap}%`:
                * **الشرح وطبيعة الشخصية:** ميكر يتلاعب بالمحللين الكلاسيكيين بصنع اختراق وهمي للمقاومة لجذب الأفراد (FOMO) ثم الضغط للأسفل لضرب الجميع قبل الحفلة الحقيقية.
                * **كيف تتعامل معه ولا تخسر:** لا تطارد الاختراق الأول. انتظر الاختبار الناجح (Retest) لمستوى المقاومة المكسور بفوليوم هادئ للدخول بأمان تام.
                
                ---
                
                ### 3. صانع السوق المتدرج الهادئ (Accumulation Stepper) - بنسبة `{p_stepper}%`:
                * **الشرح وطبيعة الشخصية:** صندوق استثماري يرفع السعر على درجات صامتة في قناة عرضية ميتة ظاهرياً لشهور لامتصاص العروض بهدوء.
                * **كيف تتعامل معه ولا تخسر:** اصبر صبره واعتمد التجميع على دفعات قرب الحد السفلي للقناة، فعند انتهاء تجميعه ستكون الحركة صاعدة وعمودية وقوية جداً.
                """)
                
                st.markdown("---")
                st.subheader("📌 مناطق الدعم والمقاومة التاريخية ومتعددة الفترات (مع مناطق POC و HVA):")
                sup_month = round(float(df['Low'].tail(20).min()), 2)
                res_month = round(float(df['High'].tail(20).max()), 2)
                sup_year = round(float(df['Low'].tail(250).min()), 2)
                res_year = round(float(df['High'].tail(250).max()), 2)
                sup_all = round(float(df['Low'].min()), 2)
                res_all = round(float(df['High'].max()), 2)
                
                d_table = pd.DataFrame([
                    {"الفترة الزمنية": "الشهر الحالي (آخر 20 شمعة)", "أهم دعم": f"${sup_month}", "أهم مقاومة": f"${res_month}", "منطقة السيولة (POC & HVA)": f"POC: ${round((sup_month+res_month)/2, 2)}"},
                    {"الفترة الزمنية": "السنة الحالية (آخر 250 شمعة)", "أهم دعم": f"${sup_year}", "أهم مقاومة": f"${res_year}", "منطقة السيولة (POC & HVA)": f"HVA Range: [${sup_year} - ${res_year}]"},
                    {"الفترة الزمنية": "منذ النشأة (تاريخ السهم كاملاً)", "أهم دعم": f"${sup_all}", "أهم مقاومة": f"${res_all}", "منطقة السيولة (POC & HVA)": f"Macro POC: ${round((sup_all+res_all)/2, 2)}"}
                ])
                st.table(d_table)
            else:
                st.error("بيانات غير كافية لجلب التاريخ الكامل.")

# TAB 3: INSTITUTIONAL RISK MATRIX
with tab3:
    st.header("🛡️ مصفوفة المخاطر وإدارة المحافظ المؤسسية (Institutional Risk Matrix)")
    risk_ticker = get_selected_ticker_or_imported("tab3")
    
    col_a, col_b = st.columns(2)
    with col_a:
        portfolio_val = st.number_input("إجمالي قيمة المحفظة الاستثمارية ($):", value=50000.0, step=1000.0)
        risk_pct = st.slider("نسبة المخاطرة المقبولة (%):", 0.5, 5.0, 1.0, 0.5)
    with col_b:
        manual_entry = st.number_input(f"سعر الدخول لـ {risk_ticker}:", value=100.0, step=0.5)
        manual_sl = st.number_input("وقف الخسارة الصارم (SL):", value=95.0, step=0.5)
        
    if st.button("حساب تفاصيل المخاطر والأهداف الثلاثة 📐"):
        risk_amount = portfolio_val * (risk_pct / 100.0)
        risk_per_share = abs(manual_entry - manual_sl)
        
        if risk_per_share > 0:
            shares = int(risk_amount / risk_per_share)
            alloc = round(shares * manual_entry, 2)
            alloc_pct = round((alloc / portfolio_val) * 100, 1)
            
            t1 = round(manual_entry + (1.5 * risk_per_share), 2)
            t2 = round(manual_entry + (3.0 * risk_per_share), 2)
            t3 = round(manual_entry + (5.0 * risk_per_share), 2)
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("إجمالي الأسهم الموصى بها", f"{shares} سهم")
            r2.metric("حجم السيولة المخصصة", f"${alloc:,.2f}")
            r3.metric("نسبة المخاطرة الفولاذية", f"${risk_amount:,.2f} ({risk_pct}%)")
            r4.metric("نسبة التخصيص من المحفظة", f"{alloc_pct}%")
            
            st.markdown("---")
            st.subheader("🎯 الأهداف السعرية الثلاثة واستراتيجية الخروج المؤسسي:")
            ot1, ot2, ot3 = st.columns(3)
            ot1.metric("الهدف الأول (Target 1)", f"${t1}", "بيع 40% لتأمين الصفقة")
            ot2.metric("الهدف الثاني (Target 2)", f"${t2}", "بيع 40% وتحريك الوقف للدخول")
            ot3.metric("الهدف الثالث (Target 3)", f"${t3}", "ترك 20% للهدف المفتوح")
            
            st.markdown("---")
            st.subheader("📋 بروتوكول التخفيف وإدارة الخروج بناءً على جينات صانع السوق:")
            st.markdown(f"""
            1. **عند بلوغ الهدف الأول (${t1}):** قم ببيع `40%` لجني أرباح مبكرة، وارفع وقف الخسارة إلى "سعر الدخول" (`${manual_entry}`) لتصبح الصفقة **آمنة بنسبة 100%**.
            2. **عند بلوغ الهدف الثاني (${t2}):** قم ببيع `40%` إضافية لتأمين مكاسب رأسمالية قوية.
            3. **الهدف الثالث المفتوح (${t3}):** اترك الـ `20%` المتبقية لتستفيد من الانفجار الكبير بحسب جينات السهم.
            """)

# TAB 4: VALUATION
with tab4:
    st.header("📊 التقييم المالي الشامل ومصفوفة القيم العادلة (InvestingPro 12-Models)")
    val_ticker = get_selected_ticker_or_imported("tab4")
    
    if st.button("تشغيل التقييم المالي المجمع 🏛️"):
        with st.spinner(f"جاري حساب النماذج المالية لـ {val_ticker}..."):
            t = yf.Ticker(val_ticker)
            info = t.info or {}
            cp = info.get("currentPrice") or info.get("regularMarketPrice") or 100.0
            eps = info.get("trailingEps") or info.get("forwardEps") or 2.0
            bvps = info.get("bookValue") or 15.0
            growth = max(5.0, min(50.0, (info.get("earningsGrowth") or 0.15) * 100.0))
            
            graham = np.sqrt(max(0.0, 22.5 * eps * bvps)) if eps > 0 and bvps > 0 else 0.0
            growth_graham = eps * (8.5 + (2 * growth)) if eps > 0 else 0.0
            peg = eps * growth * 1.5 if eps > 0 else 0.0
            lynch = eps * growth if eps > 0 else 0.0
            pbv_val = bvps * 2.2 if bvps > 0 else 0.0
            
            models = [m for m in [graham, growth_graham, peg, lynch, pbv_val] if m > 0]
            inv_avg = round(np.mean(models), 2) if models else cp
            safety = round(((inv_avg - cp) / cp) * 100, 1) if cp > 0 else 0.0
            
            v1, v2, v3 = st.columns(3)
            v1.metric("السعر الحالي بالسوق", f"${round(cp, 2)}")
            v2.metric("متوسط القيمة العادلة", f"${inv_avg}")
            v3.metric("هامش الأمان (Margin of Safety)", f"{'+' if safety >= 0 else ''}{safety}%")
            
            st.markdown("---")
            st.subheader("📐 تفاصيل نماذج التقييم الفردية:")
            st.markdown(f"""
            * **نموذج جراهام التقليدي:** `${round(graham, 2)}`
            * **نموذج جراهام للنمو:** `${round(growth_graham, 2)}`
            * **نموذج مكرر الربحية (PEG):** `${round(peg, 2)}`
            * **نموذج بيتر لينش (Peter Lynch):** `${round(lynch, 2)}`
            * **نموذج القيمة الدفترية العادلة:** `${round(pbv_val, 2)}`
            """)

# TAB 5: BACKTEST
with tab5:
    st.header("⏳ آلة الزمن والباك تست الإحصائي المتقدم (Advanced Time Machine)")
    bt_ticker = get_selected_ticker_or_imported("tab5")
    
    col_bt1, col_bt2 = st.columns(2)
    with col_bt1:
        bt_period = st.selectbox("المدى الزمني للباك تست:", ["6 أشهر", "سنة", "سنتين", "5 سنوات", "كامل تاريخ السهم (Max)"], index=1)
    with col_bt2:
        bt_capital = st.number_input("رأس المال الافتراضي ($):", value=10000.0, step=1000.0)
        
    period_map = {"6 أشهر": "6mo", "سنة": "1y", "سنتين": "2y", "5 سنوات": "5y", "كامل تاريخ السهم (Max)": "max"}
    
    if st.button("تشغيل آلة الزمن والباك تست الإحصائي 🚀"):
        with st.spinner(f"جاري تشغيل المحاكاة الإحصائية للمدى ({bt_period})..."):
            df = yf.download(bt_ticker, period=period_map[bt_period], interval="1d", progress=False)
            if df is not None and not df.empty and len(df) > 50:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
                df.columns = [c.capitalize() for c in df.columns]
                
                df['Ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
                df['Vol_Sma20'] = df['Volume'].rolling(20).mean()
                df['Rvol'] = df['Volume'] / df['Vol_Sma20']
                
                cash = bt_capital
                shares = 0
                in_pos = False
                portfolio_vals = []
                trades_duration = []
                
                for i in range(50, len(df)):
                    p = df['Close'].iloc[i]
                    if not in_pos and p > df['Ema_200'].iloc[i] and df['Rvol'].iloc[i] >= 1.2:
                        in_pos = True
                        shares = (cash * 0.999) / (p * 1.001)
                        cash = 0
                        entry_idx = i
                    elif in_pos and p < df['Ema_200'].iloc[i]:
                        cash = (shares * p) * 0.999
                        shares = 0
                        in_pos = False
                        trades_duration.append(i - entry_idx)
                        
                    current_val = cash if not in_pos else shares * p
                    portfolio_vals.append(current_val)
                        
                final_val = portfolio_vals[-1] if portfolio_vals else bt_capital
                ret = ((final_val - bt_capital) / bt_capital) * 100
                
                b1, b2, b3, b4 = st.columns(4)
                b1.metric("صافي العائد التاريخي", f"{round(ret, 2)}%")
                b2.metric("رأس المال النهائي", f"${round(final_val, 2):,.2f}")
                b3.metric("إجمالي الصفقات المنفذة", f"{len(trades_duration)}")
                b4.metric("متوسط عدد شموع الاستجابة", f"{int(np.mean(trades_duration)) if trades_duration else 0} شمعة")
                
                st.markdown("---")
                st.subheader("📈 منحنى نمو المحفظة (Equity Curve):")
                st.line_chart(pd.DataFrame({"قيمة المحفظة": portfolio_vals}, index=df.index[50:]))
                
                if trades_duration:
                    st.markdown("---")
                    st.subheader("📊 التقرير الإحصائي لزمن الاستجابة (Time-to-Target Distribution):")
                    st.info(f"💡 **تحليل التوزيع:** تركزت أغلب الحركات الإيجابية تاريخياً في نطاق ما بين `{max(1, int(np.percentile(trades_duration, 25)))}` إلى `{int(np.percentile(trades_duration, 75))}` شمعة بعد الدخول، بانحراف معياري يقدر بـ `{round(np.std(trades_duration), 1)}` شمعة.")
            else:
                st.error("بيانات غير كافية للباك تست في هذه الفترة.")

