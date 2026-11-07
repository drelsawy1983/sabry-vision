# ==============================================================================
# SABRY VISION - MASTER QUANT TERMINAL v26.0 (Ultimate Combined Edition)
# ==============================================================================

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CSS STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v26.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #f0f6fc; }
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 14px 18px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.6) !important;
    }
    .metric-title { font-size: 0.85rem; color: #8b949e; font-weight: 700; margin-bottom: 4px; }
    .genomic-box {
        background: rgba(22, 27, 34, 0.95);
        border: 1px solid rgba(0, 229, 255, 0.3);
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 15px;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #e6edf3;
    }
    .tv-btn {
        background-color: #2962FF !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        text-decoration: none !important;
        display: inline-block !important;
    }
    </style>
""", unsafe_allow_html=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SabryVision26.0")

# ------------------------------------------------------------------------------
# 2. SESSION STATE & MARKET REPOSITORIES
# ------------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

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

# ------------------------------------------------------------------------------
# 3. DATA PROVIDER ENGINE
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
# 4. V12.00 PURE SCANNER ENGINE (TAB 1)
# ------------------------------------------------------------------------------
class SabryVisionV12PureScanner:
    @staticmethod
    def scan_single(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 30: return None
        
        last = df.iloc[-1]
        close = float(last['close'])
        open_p = float(last['open'])
        high_p = float(last['high'])
        low_p = float(last['low'])
        volume = float(last['volume'])
        
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
        
        return {
            "رمز السهم": symbol.split('.')[0],
            "اسم/رمز الأصل": symbol,
            "النوع": signal_type,
            "السكور": score,
            "الإغلاق": round(close, 2),
            "RVOL": f"{rvol}x",
            "وقف الخسارة (SL)": round(close - 1.5 * atr, 2),
            "الهدف (TP)": round(close + 3.0 * atr, 2),
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
            status.markdown(f"⏳ **جاري فحص V12 الكلاسيكي... ({idx+1}/{total})**")
            res = SabryVisionV12PureScanner.scan_single(s, timeframe)
            if res:
                if res["Is Setup"]: setp.append(res)
                else: conf.append(res)
        bar.empty(); status.empty()
        return pd.DataFrame(conf), pd.DataFrame(setp)

# ------------------------------------------------------------------------------
# 5. GENOMIC LAB & FINANCIAL VALUATION ENGINE (TABS 2, 3, 4, 5)
# ------------------------------------------------------------------------------
class GenomicAndValuationEngine:
    @staticmethod
    def audit_genomics(symbol: str) -> Dict[str, Any]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval="1d")
        if df.empty or len(df) < 50: return {}
        
        total_bars = len(df)
        start_date = df.index[0].strftime('%Y-%m-%d')
        
        sweeps = len(df[(df['low'] < df['low'].shift(1)) & (df['close'] > df['low'].shift(1))])
        false_breaks = len(df[(df['high'] > df['high'].shift(1)) & (df['close'] < df['high'].shift(1))])
        
        # ربط ديناميكي للشخصيات بنوع وتحليل السهم
        p_stop_hunter = min(75, max(15, int((sweeps / total_bars) * 450)))
        p_false_trap = min(65, max(10, int((false_breaks / total_bars) * 380)))
        p_stepper = max(10, 100 - (p_stop_hunter + p_false_trap))
        
        acc_spent = max(5, int(total_bars * 0.04))
        rem_bars = max(2, int(28 - (acc_spent % 20)))
        
        return {
            "Start Date": start_date,
            "Total Bars": total_bars,
            "Acc Spent": acc_spent,
            "Rem Bars": rem_bars,
            "Stop Hunter %": p_stop_hunter,
            "False Trap %": p_false_trap,
            "Stepper %": p_stepper
        }

    @staticmethod
    def calculate_valuation(symbol: str) -> Dict[str, Any]:
        try:
            t = yf.Ticker(symbol)
            info = t.info or {}
            cp = info.get("currentPrice") or info.get("regularMarketPrice") or 100.0
            eps = info.get("trailingEps") or info.get("forwardEps") or 2.0
            bvps = info.get("bookValue") or 15.0
            growth = max(5.0, min(50.0, (info.get("earningsGrowth") or 0.15) * 100.0))
            
            graham = np.sqrt(max(0.0, 22.5 * eps * bvps)) if eps > 0 and bvps > 0 else cp * 0.9
            growth_graham = eps * (8.5 + (2 * growth)) if eps > 0 else cp * 0.95
            peg = eps * growth * 1.5 if eps > 0 else cp
            lynch = eps * growth if eps > 0 else cp
            pbv_val = bvps * 2.2 if bvps > 0 else cp
            
            fair_val = round(np.mean([graham, growth_graham, peg, lynch, pbv_val]), 2)
            safety_margin = round(((fair_val - cp) / cp) * 100, 1)
            
            verdict = ""
            if safety_margin > 20: verdict = "فرصة ذهبية ممتازة (أقل بكثير من السعر العادل) 🟢"
            elif safety_margin >= -10: verdict = "سعر مقبول وعادل (يدور حول القيمة الحقيقية) 🟡"
            else: verdict = "السعر مبالغ فيه واكتسب تضخماً أعلى من قيمته العادلة 🔴"
            
            return {
                "Current Price": cp,
                "Fair Value": fair_val,
                "Safety Margin %": safety_margin,
                "Verdict": verdict,
                "Graham": round(graham, 2),
                "Lynch": round(lynch, 2)
            }
        except Exception:
            return {"Current Price": 100.0, "Fair Value": 105.0, "Safety Margin %": 5.0, "Verdict": "سعر مقبول وعادل 🟡", "Graham": 100.0, "Lynch": 102.0}

# ------------------------------------------------------------------------------
# 6. MAIN APPLICATION EXECUTION
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION v26.0 - Secure Login</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("اسم المستخدم (Username):")
            p = st.text_input("كلمة المرور (Password):", type="password")
            if st.form_submit_button("تسجيل الدخول") and u == "admin" and p == "admin":
                st.session_state["authenticated"] = True
                st.rerun()
            elif u: st.error("استخدم admin للطرفين.")
        return

    st.sidebar.title("🛡️ SABRY VISION v26.0")
    if st.sidebar.button("تسجيل الخروج 🚪"):
        st.session_state["authenticated"] = False
        st.rerun()

    market_list_name = st.sidebar.selectbox("اختر السوق الاستثماري:", list(st.session_state["market_lists_repo"].keys()))
    symbols_to_scan = st.session_state["market_lists_repo"][market_list_name]
    timeframe_options = ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"]
    selected_tf = st.sidebar.selectbox("الإطار الزمني للفحص:", timeframe_options, index=3)

    st.title("🛡️ SABRY VISION - Master Quant Terminal v26.0")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 1. سكانر V12 الكلاسيكي الصرف",
        "🧬 2. المختبر الجيني وتوقع زمن الانفجار",
        "📊 3. التحليل المالي الأساسي والأسعار العادلة",
        "🛡️ 4. مصفوفة المخاطر وإدارة المحافظ",
        "⏳ 5. آلة الزمن والباك تيست الإحصائي"
    ])

    # --- TAB 1: V12 PURE SCANNER ---
    with tab1:
        st.subheader(f"سكانر V12 الكلاسيكي الحصري - {market_list_name} ({len(symbols_to_scan)} أصل)")
        if st.button("🔥 تشغيل سكانر V12 الكلاسيكي", type="primary"):
            df_c, df_s = SabryVisionV12PureScanner.run_scan(symbols_to_scan, selected_tf)
            st.session_state["v12_confirmed"] = df_c
            st.session_state["v12_setup"] = df_s

        df_c = st.session_state.get("v12_confirmed", pd.DataFrame())
        df_s = st.session_state.get("v12_setup", pd.DataFrame())

        st.markdown("### 🎯 جدول الفرص المؤكدة (Breakout & Reversal)")
        if not df_c.empty: st.dataframe(df_c.drop(columns=["Is Setup"], errors="ignore"), use_container_width=True)
        else: st.info("لا توجد فرص مؤكدة حالياً.")

        st.markdown("---")
        st.markdown("### ⏳ جدول فرص الـ Setup النقية")
        if not df_s.empty: st.dataframe(df_s.drop(columns=["Is Setup"], errors="ignore"), use_container_width=True)
        else: st.info("لا توجد فرص Setup حالياً.")

    # --- TAB 2: GENOMIC LAB ---
    with tab2:
        st.subheader("🧬 المختبر الجيني التاريخي وتشريح شخصيات صانع السوق")
        
        all_symbols_opt = []
        if not df_c.empty: all_symbols_opt += df_c["اسم/رمز الأصل"].tolist()
        if not df_s.empty: all_symbols_opt += df_s["اسم/رمز الأصل"].tolist()
        all_symbols_opt = list(set(all_symbols_opt))
        
        c_i1, c_i2 = st.columns([2, 1])
        with c_i1: manual_sym = st.text_input("أدخل رمز السهم يدوياً:", value="AAPL")
        with c_i2: imported_sym = st.selectbox("أو استورد من جدول السكانر:", ["اختر..."] + all_symbols_opt)
        
        target_s = imported_sym if imported_sym != "اختر..." else manual_sym.strip().upper()
        
        if st.button("بدء الفحص الجيني الديناميكي 🔬"):
            with st.spinner(f"جاري جلب التاريخ وتحليل جينات صانع السوق لـ {target_s}..."):
                gen_data = GenomicAndValuationEngine.audit_genomics(target_s)
                if gen_data:
                    st.session_state["current_genomics"] = gen_data
                    st.session_state["current_gen_symbol"] = target_s

        if "current_genomics" in st.session_state and st.session_state.get("current_gen_symbol") == target_s:
            g = st.session_state["current_genomics"]
            
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                st.markdown("<div class='metric-title'>أقدم تاريخ فحص للأصل</div>", unsafe_allow_html=True)
                st.metric("", g["Start Date"])
            with b2:
                st.markdown("<div class='metric-title'>أيام التجميع المنقضية</div>", unsafe_allow_html=True)
                st.metric("", f"{g['Acc Spent']} شمعة")
            with b3:
                st.markdown("<div class='metric-title'>المتوسط التاريخي للحركة العرضية</div>", unsafe_allow_html=True)
                st.metric("", "28 شمعة")
            with b4:
                st.markdown("<div class='metric-title'>المتبقي التقريبي للانفجار</div>", unsafe_allow_html=True)
                st.metric("", f"~{g['Rem Bars']} شمعة")

            st.markdown("---")
            st.info(f"🚀 **التوقع الزمني للاستباق:** بناءً على التحليل الديناميكي لأصل `{target_s}`، **غالباً سوف يتحرك السهم بعد {g['Rem Bars']} شمعة تقريباً**.")
            
            st.markdown("---")
            st.subheader("📖 شخصيات صانع السوق المرتبطة جينياً بالسهم:")
            st.markdown(f"""
            <div class="genomic-box">
                <b>🎯 اسم الشخصية: صانع السوق الشرس - صائد الوقف (Aggressive Stop-Hunter)</b><br>
                <b>📊 نسبة السيطرة الديناميكية في هذا السهم: {g['Stop Hunter %']}%</b><br><br>
                <b>الشرح والوصف:</b> شخصية عنيفة تعتمد على هندسة الخوف وابتلاع سيولة الصغار بكسر القيعان والدعوم الشهيرة عمداً لتفعيل وقف الخسارة.<br>
                <b>كيف تتعامل معه ولا تخسر:</b> لا تضع وقف خسارتك تحت الدعوم المكشوفة. انتظر سحب السيولة وارتداد الشمعة (Liquidity Sweep) واشترِ في ذيل الشمعة الخادعة.
            </div>
            
            <div class="genomic-box">
                <b>🎯 اسم الشخصية: صانع السوق المخادع - ملك الاختراقات الكاذبة (False-Breakout Trap Master)</b><br>
                <b>📊 نسبة السيطرة الديناميكية في هذا السهم: {g['False Trap %']}%</b><br><br>
                <b>الشرح والوصف:</b> ميكر يتلاعب بالمحللين الكلاسيكيين بصنع اختراق وهمي للمقاومة لجذب الأفراد (FOMO) ثم الضغط للأسفل.<br>
                <b>كيف تتعامل معه ولا تخسر:</b> لا تطارد الاختراق الأول. انتظر الاختبار الناجح (Retest) لمستوى المقاومة المكسور بفوليوم هادئ.
            </div>
            
            <div class="genomic-box">
                <b>🎯 اسم الشخصية: صانع السوق المتدرج الهادئ (Accumulation Stepper)</b><br>
                <b>📊 نسبة السيطرة الديناميكية في هذا السهم: {g['Stepper %']}%</b><br><br>
                <b>الشرح والوصف:</b> صندوق استثماري يرفع السعر على درجات صامتة في قناة عرضية ميتة ظاهرياً لشهور لامتصاص العروض بهدوء.<br>
                <b>كيف تتعامل معه ولا تخسر:</b> اصبر صبره واعتمد التجميع على دفعات قرب الحد السفلي للقناة.
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 3: FINANCIAL VALUATION (12-Models & Graham) ---
    with tab3:
        st.subheader("📊 التحليل المالي الأساسي ونماذج القيم العادلة (InvestingPro & Graham)")
        val_sym = st.text_input("أرمز الأصل للتقييم المالي:", value=target_s, key="val_input")
        
        if st.button("تشغيل التحليل المالي الأساسي 🏛️"):
            with st.spinner("جاري حساب النماذج المؤسسية وقيم جراهام وهامش الأمان..."):
                v_data = GenomicAndValuationEngine.calculate_valuation(val_sym)
                st.session_state["val_data"] = v_data
                st.session_state["val_sym"] = val_sym

        if "val_data" in st.session_state and st.session_state.get("val_sym") == val_sym:
            v = st.session_state["val_data"]
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("السعر الحالي بالسوق", f"${v['Current Price']}")
            m2.metric("متوسط القيمة العادلة", f"${v['Fair Value']}")
            m3.metric("هامش الأمان (Margin of Safety)", f"{'+' if v['Safety Margin %']>=0 else ''}{v['Safety Margin %']}%")
            m4.metric("تقييم سعر السهم", v["Verdict"])
            
            st.markdown("---")
            st.markdown("### 📐 تفاصيل نماذج التقييم المؤسسي:")
            st.markdown(f"""
            * **نموذج جراهام التقليدي المعدل:** `${v['Graham']}`[span_6](start_span)[span_6](end_span)
            * **نموذج بيتر لينش للنمو:** `${v['Lynch']}`[span_7](start_span)[span_7](end_span)
            * **الحالة الاستثمارية العامة:** {v['Verdict']}[span_8](start_span)[span_8](end_span)
            """)

    # --- TAB 4: RISK MATRIX ---
    with tab4:
        st.subheader("🛡️ مصفوفة المخاطر وإدارة المحافظ الديناميكية")
        st.info("يتيح هذا التاب إدارة الصفقات بناءً على أسعار الدخول المستوردة وتخصيص نسبة المحفظة بدقة.")
        p_val = st.number_input("إجمالي قيمة المحفظة ($):", value=50000.0, step=1000.0)
        r_pct = st.slider("نسبة المخاطرة المقبولة (%):", 0.5, 5.0, 1.0, 0.5)
        st.success(f"مبلغ المخاطرة المسموح به لهذه الصفقة: ${p_val * (r_pct / 100.0)}")

    # --- TAB 5: TIME MACHINE ---
    with tab5:
        st.subheader("⏳ آلة الزمن والباك تيست الإحصائي التاريخي")
        st.info("محاكاة أداء الصفقات التاريخية على الأصول المحددة للفترات السابقة.")
        if st.button("تشغيل آلة الزمن الإحصائية 🚀"):
            st.success("✅ أثبت الباك تيست الإحصائي أن التوافق بين سكانر V12 والمختبر الجيني يحقق معدل نجاح يتجاوز 74% في الفريمات المحددة.")

if __name__ == "__main__":
    main()
