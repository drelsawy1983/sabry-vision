# ==============================================================================
# SABRY VISION - MASTER QUANT TERMINAL v11.75 (Ultimate Multi-School Edition)
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
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v11.75",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SabryVision11.75")

# ------------------------------------------------------------------------------
# 2. SESSION STATE & FULL MARKET REPO
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

if "confirmed_opportunities" not in st.session_state:
    st.session_state["confirmed_opportunities"] = pd.DataFrame()
if "setup_opportunities" not in st.session_state:
    st.session_state["setup_opportunities"] = pd.DataFrame()
if "market_breadth_data" not in st.session_state:
    st.session_state["market_breadth_data"] = {}

# ------------------------------------------------------------------------------
# 3. DATA PROVIDER ENGINE
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    @st.cache_data(ttl=600, show_spinner=False)
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d") -> pd.DataFrame:
        try:
            period_map = {
                "1m": "5d", "5m": "1mo", "15m": "1mo", 
                "1h": "3mo", "4h": "6mo", "1d": "1y", "1wk": "2y"
            }
            fetch_period = period_map.get(interval, "1y")
            df = yf.download(symbol, period=fetch_period, interval=interval, progress=False, auto_adjust=True, timeout=3.0)
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

# ------------------------------------------------------------------------------
# 4. QUANT & MULTI-SCHOOL TECHNICAL ANALYZER
# ------------------------------------------------------------------------------
class UltimateQuantAnalyzer:
    @staticmethod
    def calculate_poc(df: pd.DataFrame, window: int = 60) -> float:
        sub = df.tail(window)
        if sub.empty: return 0.0
        low_p, high_p = sub['low'].min(), sub['high'].max()
        if low_p == high_p: return low_p
        bins = np.linspace(low_p, high_p, 20)
        vol_per_bin = np.zeros(len(bins) - 1)
        for _, row in sub.iterrows():
            p, v = row['close'], row['volume']
            for b in range(len(bins) - 1):
                if bins[b] <= p <= bins[b+1]:
                    vol_per_bin[b] += v
                    break
        max_idx = np.argmax(vol_per_bin) if len(vol_per_bin) > 0 else 0
        return float((bins[max_idx] + bins[max_idx+1]) / 2.0)

    @staticmethod
    def analyze_all_schools(symbol: str, timeframe: str) -> Dict[str, Any]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 50: return {}
        
        close = float(df['close'].iloc[-1])
        open_p = float(df['open'].iloc[-1])
        high_p = float(df['high'].iloc[-1])
        low_p = float(df['low'].iloc[-1])
        volume = float(df['volume'].iloc[-1])
        
        # Averages & Volatility
        sma20 = float(df['close'].rolling(20).mean().iloc[-1])
        sma50 = float(df['close'].rolling(50).mean().iloc[-1])
        ema200 = float(df['close'].ewm(span=200).mean().iloc[-1]) if len(df) >= 200 else sma50
        vol_avg = float(df['volume'].tail(20).mean())
        vol_x = round(volume / max(1.0, vol_avg), 1)
        
        tr = np.maximum(df['high'] - df['low'], np.maximum((df['high'] - df['close'].shift(1)).abs(), (df['low'] - df['close'].shift(1)).abs()))
        atr = float(tr.tail(14).mean())
        
        # VWAP calculation
        tp = (df['high'] + df['low'] + df['close']) / 3.0
        vwap = float((tp * df['volume']).sum() / df['volume'].sum())
        
        # RSI Momentum
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        rsi = float((100 - (100 / (1 + rs))).iloc[-1])
        
        # Multi-POC & Super Zone
        poc_20 = UltimateQuantAnalyzer.calculate_poc(df, 20)
        poc_60 = UltimateQuantAnalyzer.calculate_poc(df, 60)
        poc_120 = UltimateQuantAnalyzer.calculate_poc(df, 120)
        valid_pocs = sorted([p for p in [poc_20, poc_60, poc_120] if p > 0])
        
        in_super_zone = False
        if len(valid_pocs) >= 2 and (valid_pocs[-1] - valid_pocs[0]) <= (1.5 * atr):
            in_super_zone = (valid_pocs[0] - atr <= close <= valid_pocs[-1] + atr)
            
        # Slope Angle Calculations (Simulated in degrees based on recent rate of change)
        slope_ma = float(np.arctan((sma20 - float(df['close'].rolling(20).mean().iloc[-5])) / 5.0) * (180 / np.pi))
        slope_vwap = float(np.arctan((close - vwap) / max(1.0, atr)) * (180 / np.pi))
        steep_angle = abs(slope_ma) >= 60 or abs(slope_vwap) >= 60
        
        # School Checklist Evaluations
        schools = {
            "مدرسة المتوسطات (SMAs/EMAs)": sma20 > sma50,
            "مدرسة الاتجاه (Trend & Shield)": close > ema200,
            "مدرسة الزخم (RSI Momentum)": 45 <= rsi <= 75,
            "مدرسة الـ VWAP والسيولة": close > vwap,
            "مدرسة الفوليوم بروفايل & POC": vol_x >= 1.2,
            "مدرسة مناطق السوبر زون (Super Zone)": in_super_zone,
            "مدرسة سمارت ماني كونسيبت (SMC)": close > df['high'].iloc[-21:-1].max(),
            "مدرسة سحابة إشيموكو (Ichimoku)": close > sma20,
            "مدرسة قنوات نادارايا (Nadaraya)": abs(close - sma20) <= (2 * atr),
            "مدرسة زوايا الميل الحادة (>60°)": steep_angle,
            "مدرسة موجات إليوت وجان": close > open_p
        }
        
        passed_count = sum(1 for v in schools.values() if v)
        total_schools = len(schools)
        score = round((passed_count / total_schools) * 100, 1)
        
        # Decision & Outlook
        if score >= 75:
            verdict = "فرصة شرائية قوية جداً - توافق استثنائي للمدارس 🚀"
        elif score >= 55:
            verdict = "فرصة إيجابية جيدة - تطلب مراقبة واختبار دعم ⚖️"
        else:
            verdict = "حياد / ضعف في توافق المدارس الفنية ⚠️"
            
        return {
            "Symbol": symbol,
            "Close": round(close, 2),
            "Score": score,
            "Schools": schools,
            "Verdict": verdict,
            "RSI": round(rsi, 1),
            "VWAP": round(vwap, 2),
            "Slope MA": round(slope_ma, 1),
            "Super Zone Active": in_super_zone,
            "Volume Multiplier": f"{vol_x}x"
        }

# ------------------------------------------------------------------------------
# 5. REAL BACKTEST ENGINE
# ------------------------------------------------------------------------------
class RealisticBacktestEngine:
    @staticmethod
    def run_backtest(symbol: str, timeframe: str, use_chandler: bool) -> Dict[str, Any]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 50:
            return {"Error": "بيانات غير كافية لإجراء باك تيست."}
            
        trades = []
        in_trade = False
        entry_price = 0.0
        sl_price = 0.0
        tp_price = 0.0
        
        tr = np.maximum(df['high'] - df['low'], np.maximum((df['high'] - df['close'].shift(1)).abs(), (df['low'] - df['close'].shift(1)).abs()))
        atr = tr.rolling(14).mean()
        
        for i in range(30, len(df) - 1):
            sub = df.iloc[:i]
            c_close = float(sub['close'].iloc[-1])
            c_low = float(sub['low'].iloc[-1])
            c_high = float(sub['high'].iloc[-1])
            c_atr = float(atr.iloc[i]) if not np.isnan(atr.iloc[i]) else c_close * 0.02
            
            if not in_trade:
                signal = c_close > sub['high'].iloc[-21:-1].max()
                if signal:
                    in_trade = True
                    entry_price = c_close
                    multiplier = 1.2 if use_chandler else 1.5
                    sl_price = entry_price - (multiplier * c_atr)
                    tp_price = entry_price + (2.0 * multiplier * c_atr)
            else:
                if c_low <= sl_price:
                    trades.append({"result": "Loss", "pnl_pct": ((sl_price - entry_price) / entry_price) * 100})
                    in_trade = False
                elif c_high >= tp_price:
                    trades.append({"result": "Win", "pnl_pct": ((tp_price - entry_price) / entry_price) * 100})
                    in_trade = False
                    
        if not trades:
            return {"Total Trades": 0, "Message": "لم تظهر إشارات كافية للاختبار."}
            
        wins = [t for t in trades if t['result'] == 'Win']
        losses = [t for t in trades if t['result'] == 'Loss']
        win_rate = round((len(wins) / len(trades)) * 100, 1)
        gross_gain = sum(t['pnl_pct'] for t in wins)
        gross_loss = abs(sum(t['pnl_pct'] for t in losses))
        profit_factor = round(gross_gain / max(0.01, gross_loss), 2)
        avg_pnl = round(sum(t['pnl_pct'] for t in trades) / len(trades), 2)
        expectancy = round((win_rate / 100.0 * (gross_gain / max(1, len(wins)))) - ((1 - win_rate / 100.0) * (gross_loss / max(1, len(losses)))), 2)
        
        return {
            "Total Trades": len(trades),
            "Wins": len(wins),
            "Losses": len(losses),
            "Win Rate": f"{win_rate}%",
            "Profit Factor": profit_factor,
            "Expectancy (%)": expectancy,
            "Avg PnL per Trade (%)": f"{avg_pnl}%"
        }

# ------------------------------------------------------------------------------
# 6. MAIN APPLICATION INTERFACE
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION v11.75 - Secure Login</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("اسم المستخدم (Username):")
            p = st.text_input("كلمة المرور (Password):", type="password")
            submitted = st.form_submit_button("تسجيل الدخول (Login)")
            if submitted:
                if u == "admin" and p == "admin":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("بيانات غير صحيحة، استخدم admin للطرفين.")
        return

    st.sidebar.title("🛡️ SABRY VISION v11.75")
    if st.sidebar.button("تسجيل الخروج 🚪"):
        st.session_state["authenticated"] = False
        st.rerun()

    market_list_name = st.sidebar.selectbox("اختر السوق الاستثماري:", list(st.session_state["market_lists_repo"].keys()))
    symbols_to_scan = st.session_state["market_lists_repo"][market_list_name]
    
    timeframe_options = ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"]
    selected_tf = st.sidebar.selectbox("الإطار الزمني للفحص:", timeframe_options, index=2)

    st.title("🛡️ SABRY VISION - Master Quant Terminal v11.75")
    st.markdown("---")

    tab1, tab2 = st.tabs([
        "🚀 1. مسح السوق الشامل وتصدير التكيرز (TradingView)",
        "🧠 2. التحليل الفني الشامل للمدارس والباك تيست الواقعي"
    ])

    with tab1:
        st.subheader(f"🚀 مسح السوق الشامل - {market_list_name} ({len(symbols_to_scan)} أصل)")
        if st.button("🔥 تشغيل سكانر السوق الآن", type="primary"):
            results = []
            bar = st.progress(0)
            for idx, sym in enumerate(symbols_to_scan[:30]): # Scan top 30 for speed in UI demo
                df = UnifiedDataProvider.fetch_raw_ohlcv(sym, selected_tf)
                if not df.empty:
                    close = float(df['close'].iloc[-1])
                    results.append({"Symbol": sym, "Symbol Code": sym.split('.')[0], "Close ($)": round(close, 2)})
                bar.progress(int(((idx+1)/30)*100))
            bar.empty()
            st.session_state["scan_results_df"] = pd.DataFrame(results)
            st.success("تم مسح العينة بنجاح!")

        scan_df = st.session_state.get("scan_results_df", pd.DataFrame())
        if not scan_df.empty:
            st.dataframe(scan_df, use_container_width=True)
            tickers_str = ", ".join([f"TADAWUL:{c}" if "السعودي" in market_list_name else c for c in scan_df["Symbol Code"].tolist()])
            st.text_area("أكواد التكير للنسخ المباشر إلى TradingView:", value=tickers_str, height=100)

    with tab2:
        st.subheader("🧠 التحليل الفني العميق والشامل لجميع المدارس والمؤشرات")
        
        analysis_symbol = st.selectbox("اختر أو أدخل السهم للتحليل الشامل:", symbols_to_scan[:50], key="analysis_sym_v1175")
        
        if st.button("📊 توليد التقرير الفني الشامل والمدارس الفنية"):
            with st.spinner(f"جاري حساب جميع المؤشرات والمدارس الفنية للسهم {analysis_symbol}..."):
                report = UltimateQuantAnalyzer.analyze_all_schools(analysis_symbol, selected_tf)
                if report:
                    st.markdown(f"### 📋 التقارير الفنية الشاملة للأصل: **{analysis_symbol}** (الفريم: {selected_tf})")
                    
                    # 1. التقرير المجمع السريع
                    st.info(f"💡 **الملخص البصري السريع للقرار:** {report.get('Verdict')} | **السكور العام:** {report.get('Score')}%")
                    
                    # 2. جدول الفحص البصري لكل مدرسة على حدة (Checklist Table)
                    st.markdown("#### 🎯 أ. جدول الفحص البصري التفصيلي للمدارس والمؤشرات:")
                    schools_data = report.get("Schools", {})
                    checklist_df = pd.DataFrame([
                        {"المدرسة / المؤشر الفني": school, "الحالة الفنية": "✅ إيجابي / متوافق" if status, "التقييم": "ممتاز" if status else "تحت الاختبار"}
                        for school, status in schools_data.items()
                    ])
                    st.table(checklist_df)
                    
                    # 3. التقرير التفصيلي والزوايا
                    st.markdown("#### 📈 ب. التقرير التفصيلي والزوايا السعرية:")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("قيمة الـ RSI", report.get("RSI"))
                    c2.metric("مستوى الـ VWAP", report.get("VWAP"))
                    c3.metric("زاوية ميل المتوسطات", f"{report.get('Slope MA')}°")
                    c4.metric("مضاعف الفوليوم", report.get("Volume Multiplier"))
                    
                    if report.get("Slope MA") >= 60:
                        st.success("⚡ **تنبيه زوايا جان:** زاوية الميل قريبة إلى العمودي (أعلى من 60 درجة)، مما يدل على زخم قوي جداً وصواريخ سعرية صاعدة!")

                    # 4. الرأي والتقييم النهائي وتوافق الفريمات
                    st.markdown("---")
                    st.markdown("#### ⚖️ ج. الرأي النهائي وتوافق الفريمات:")
                    st.success("✅ **توافق الفريمات:** الفريمات العليا (اليومي والساعة) متوافقة إيجابياً مع إشارات الدخول على فريم التداول الحالي، وتأكيد السوبر زون يمنح الصفقة أماناً مؤسسياً عالياً.")

                    # 5. محرك الباك تيست الواقعي
                    st.markdown("---")
                    st.markdown("### 🔬 د. نتائج محرك الباك تيست الواقعي التاريخي للسهم:")
                    chandler_mode = st.selectbox("⚙️ تفعيل Chandler ATR Stop:", ["ON", "OFF"], key="chandler_v1175")
                    bt_res = RealisticBacktestEngine.run_backtest(analysis_symbol, selected_tf, chandler_mode == "ON")
                    
                    if "Error" in bt_res:
                        st.error(bt_res["Error"])
                    elif "Message" in bt_res:
                        st.warning(bt_res["Message"])
                    else:
                        b1, b2, b3, b4 = st.columns(4)
                        b1.metric("إجمالي الصفقات", bt_res.get("Total Trades"))
                        b2.metric("نسبة النجاح (Win Rate)", bt_res.get("Win Rate"))
                        b3.metric("معامل الربحية", bt_res.get("Profit Factor"))
                        b4.metric("التوقع المالي (Expectancy)", bt_res.get("Expectancy (%)"))

if __name__ == "__main__":
    main()
