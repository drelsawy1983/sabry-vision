# ==============================================================================
# SABRY VISION - MASTER QUANT TERMINAL v12.00 (The Ultimate Hybrid Edition)
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
    page_title="SABRY VISION - Master Quant Terminal v12.00",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SabryVision12.00")

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
# 4. HYBRID QUANT & MICRO-AUDIT ENGINE (v12.00)
# ------------------------------------------------------------------------------
class HybridQuantEngine:
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
    def scan_stock(symbol: str, timeframe: str, selected_opps: List[str]) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 30: return None
        
        close = float(df['close'].iloc[-1])
        open_p = float(df['open'].iloc[-1])
        high_p = float(df['high'].iloc[-1])
        low_p = float(df['low'].iloc[-1])
        volume = float(df['volume'].iloc[-1])
        
        vol_avg = float(df['volume'].tail(20).mean())
        vol_x = round(volume / max(1.0, vol_avg), 1)
        
        tr = np.maximum(df['high'] - df['low'], np.maximum((df['high'] - df['close'].shift(1)).abs(), (df['low'] - df['close'].shift(1)).abs()))
        atr = float(tr.tail(14).mean())
        
        sma50 = float(df['close'].tail(50).mean())
        sma20 = float(df['close'].tail(20).mean())
        
        tp = (df['high'] + df['low'] + df['close']) / 3.0
        vwap = float((tp * df['volume']).sum() / df['volume'].sum())
        
        poc_20 = HybridQuantEngine.calculate_poc(df, 20)
        poc_60 = HybridQuantEngine.calculate_poc(df, 60)
        valid_pocs = sorted([p for p in [poc_20, poc_60] if p > 0])
        in_super_zone = len(valid_pocs) >= 2 and abs(valid_pocs[-1] - valid_pocs[0]) <= (1.5 * atr)
        
        recent_high = df['high'].iloc[-21:-1].max()
        recent_low = df['low'].iloc[-21:-1].min()
        
        is_breakout = close > recent_high and vol_x >= 1.2
        is_bottom_reversal = low_p <= recent_low and close > open_p and (close - low_p) > (high_p - close)
        is_retest = any(abs(low_p - p) <= (0.5 * atr) for p in valid_pocs)
        is_liquidity_sweep = low_p < recent_low and close > recent_low
        is_setup = close > sma50 and not (is_breakout or is_bottom_reversal)
        
        detected_opps = []
        if is_breakout: detected_opps.append("Breakout")
        if is_bottom_reversal: detected_opps.append("Bottom Reversal")
        if is_retest: detected_opps.append("Retest")
        if is_liquidity_sweep: detected_opps.append("Liquidity Sweep")
        if is_setup: detected_opps.append("Setup")
        
        if not detected_opps: return None
        if "الكل (جميع الفرص)" not in selected_opps and not any(o in selected_opps for o in detected_opps):
            return None
            
        base_score = 40.0
        if is_breakout: base_score += 25.0
        if is_bottom_reversal: base_score += 20.0
        if is_retest: base_score += 15.0
        if is_liquidity_sweep: base_score += 15.0
        if in_super_zone: base_score += 10.0
        base_score += min(15.0, vol_x * 5.0)
        if close > vwap: base_score += 10.0
        
        score = round(min(99.5, max(30.0, base_score)), 1)
        stop_loss = round(close - (1.5 * atr), 2)
        take_profit = round(close + (2.5 * atr), 2)
        
        return {
            "رمز السهم": symbol.split('.')[0],
            "اسم/رمز الأصل": symbol,
            "الفرصة": " + ".join(detected_opps),
            "السكور": score,
            "السوبر زون": "داخل السوبر زون 🟩" if in_super_zone else "خارج السوبر زون ⬜",
            "حجم الفوليوم": f"{vol_x}x",
            "سعر الإغلاق": round(close, 2),
            "وقف الخسارة (SL)": f"{stop_loss} ({round(((stop_loss-close)/close)*100,2)}%)",
            "الهدف (TP)": f"{take_profit} (+{round(((take_profit-close)/close)*100,2)}%)",
            "Raw Volume $": volume * close,
            "Is Pure Setup": (detected_opps == ["Setup"])
        }

    @staticmethod
    def bulk_scan(symbols: List[str], timeframe: str, selected_opps: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        confirmed_list, setup_list = [], []
        total = len(symbols)
        if total == 0: return pd.DataFrame(), pd.DataFrame(), {}
        
        advancing = 0
        total_volume = 0.0
        bar = st.progress(0)
        status = st.empty()
        completed = 0
        
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {executor.submit(HybridQuantEngine.scan_stock, s, timeframe, selected_opps): s for s in symbols}
            for fut in as_completed(futures):
                completed += 1
                bar.progress(int((completed / total) * 100))
                status.markdown(f"⏳ **جاري فحص السوق الشامل ({total} أصل)... المكتمل: {completed}/{total}**")
                res = fut.result()
                if res:
                    total_volume += res["Raw Volume $"]
                    if res["السكور"] >= 55.0: advancing += 1
                    if res["Is Pure Setup"]: setup_list.append(res)
                    else: confirmed_list.append(res)
                        
        bar.empty(); status.empty()
        breadth_ratio = round((advancing / max(1, total)) * 100, 1)
        
        breadth = {
            "Total": total,
            "Advancing": advancing,
            "Breadth Ratio": f"{breadth_ratio}%",
            "Liquidity Eval": "قوية 🟢" if total_volume > 500_000_000 else ("متوسطة 🟡" if total_volume > 100_000_000 else "ضعيفة 🔴"),
            "Market Strength": "سوق صاعد قوي 🚀" if breadth_ratio >= 60 else ("سوق متزن ⚖️" if breadth_ratio >= 40 else "سوق هابط ⚠️"),
            "Total Liquidity": round(total_volume, 0)
        }
        
        df_conf = pd.DataFrame(confirmed_list).sort_values(by="السكور", ascending=False).reset_index(drop=True) if confirmed_list else pd.DataFrame()
        df_set = pd.DataFrame(setup_list).sort_values(by="السكور", ascending=False).reset_index(drop=True) if setup_list else pd.DataFrame()
        return df_conf, df_set, breadth

    @staticmethod
    def hybrid_full_audit(symbol: str, timeframe: str) -> Dict[str, Any]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 50: return {}
        
        c_cur = df.iloc[-1]
        c_prev = df.iloc[-2]
        
        close = float(c_cur['close'])
        open_p = float(c_cur['open'])
        low_p = float(c_cur['low'])
        volume = float(c_cur['volume'])
        prev_close = float(c_prev['close'])
        
        # --- 1. تقييم المدارس الكبرى للسهم ككل (التقرير الشامل الكلاسيكي) ---
        sma20 = float(df['close'].rolling(20).mean().iloc[-1])
        sma50 = float(df['close'].rolling(50).mean().iloc[-1])
        ema200 = float(df['close'].ewm(span=200).mean().iloc[-1]) if len(df) >= 200 else sma50
        
        ma_ordered = sma20 > sma50 and sma50 > ema200
        trend_shield = close > ema200
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = float((100 - (100 / (1 + (gain / (loss + 1e-9))))).iloc[-1])
        rsi_momentum = 40 <= rsi <= 75
        
        tp = (df['high'] + df['low'] + df['close']) / 3.0
        vwap = float((tp * df['volume']).sum() / df['volume'].sum())
        vwap_liquidity = close > vwap
        
        vol_avg = float(df['volume'].tail(20).mean())
        vol_x = round(volume / max(1.0, vol_avg), 1)
        vol_profile = vol_x >= 1.2
        
        tr = np.maximum(df['high'] - df['low'], np.maximum((df['high'] - df['close'].shift(1)).abs(), (df['low'] - df['close'].shift(1)).abs()))
        atr = float(tr.tail(14).mean())
        
        poc_20 = HybridQuantEngine.calculate_poc(df, 20)
        poc_60 = HybridQuantEngine.calculate_poc(df, 60)
        valid_pocs = sorted([p for p in [poc_20, poc_60] if p > 0])
        in_super_zone = len(valid_pocs) >= 2 and abs(valid_pocs[-1] - valid_pocs[0]) <= (1.5 * atr)
        
        recent_high_15 = df['high'].iloc[-16:-2].max()
        recent_low_15 = df['low'].iloc[-16:-2].min()
        smc_active = close > recent_high_15 or (low_p < recent_low_15 and close > recent_low_15)
        
        ichimoku_cloud = close > sma20
        nadaraya_ok = close >= sma20 - atr
        
        slope_ma = float(np.arctan((sma20 - float(df['close'].rolling(20).mean().iloc[-5])) / 5.0) * (180 / np.pi))
        steep_angle = abs(slope_ma) >= 60
        elliott_wave = close > open_p
        
        macro_schools = {
            "مدرسة المتوسطات (SMAs/EMAs)": {"Status": ma_ordered, "Rating": "ممتاز" if ma_ordered else "تحت المراقبة", "Desc": "ترتيب تصاعدي للمتوسطات المتحركة"},
            "مدرسة الاتجاه والدرع (Trend & Shield)": {"Status": trend_shield, "Rating": "ممتاز" if trend_shield else "تحت المراقبة", "Desc": "السعر أعلى متوسط 200 (الدرع المؤسسي)"},
            "مدرسة الزخم ومؤشر RSI": {"Status": rsi_momentum, "Rating": "ممتاز" if rsi_momentum else "تحت المراقبة", "Desc": f"قيمة RSI ({round(rsi,1)}) في النطاق الإيجابي"},
            "مدرسة السيولة وخط الـ VWAP": {"Status": vwap_liquidity, "Rating": "ممتاز" if vwap_liquidity else "تحت المراقبة", "Desc": f"السعر أعلى خط الـ VWAP ({round(vwap,2)})"},
            "مدرسة الفوليوم بروفايل & POC": {"Status": vol_profile, "Rating": "ممتاز" if vol_profile else "تحت المراقبة", "Desc": f"حجم تداول يدعم الاستمرار ({vol_x}x)"},
            "مدرسة مناطق السوبر زون (Super Zone)": {"Status": in_super_zone, "Rating": "ممتاز" if in_super_zone else "تحت المراقبة", "Desc": "تمركز السعر داخل نطاق الـ POCs المتداخلة"},
            "مدرسة سمارت ماني كونسيبت (SMC)": {"Status": smc_active, "Rating": "ممتاز" if smc_active else "تحت المراقبة", "Desc": "هيكل سعري مدعوم بكسر أو ارتداد سيولة"},
            "مدرسة سحابة إشيموكو (Ichimoku)": {"Status": ichimoku_cloud, "Rating": "ممتاز" if ichimoku_cloud else "تحت المراقبة", "Desc": "السعر أعلى الخط الأساسي للإشيموكو"},
            "مدرسة قنوات نادارايا": {"Status": nadaraya_ok, "Rating": "ممتاز" if nadaraya_ok else "تحت المراقبة", "Desc": "تمركز السعر داخل النطاق الآمن للقناة"},
            "مدرسة زوايا الميل الحادة (>60°)": {"Status": steep_angle, "Rating": "ممتاز" if steep_angle else "تحت المراقبة", "Desc": f"زاوية ميل المتوسطات ({round(slope_ma,1)}°)"},
            "مدرسة موجات إليوت وزوايا جان": {"Status": elliott_wave, "Rating": "ممتاز" if elliott_wave else "تحت المراقبة", "Desc": "مسار الشمعة دافع وإيجابي"}
        }
        
        macro_passed = sum(1 for v in macro_schools.values() if v["Status"])
        macro_score = round((macro_passed / len(macro_schools)) * 100, 1)
        
        # --- 2. التدقيق اللحظي المجهري للشمعة الحالية ---
        realtime_bos = close > recent_high_15 and prev_close <= recent_high_15
        realtime_choch = low_p < recent_low_15 and close > recent_low_15
        fvg_active_now = (float(df['high'].iloc[-3]) < float(df['low'].iloc[-1]))
        bullish_ob_bounce = (c_prev['close'] < c_prev['open']) and (close > open_p) and (low_p <= c_prev['low'])
        
        high_9, low_9 = df['high'].tail(9).max(), df['low'].tail(9).min()
        tenkan_cur = (high_9 + low_9) / 2.0
        high_prev_9, low_prev_9 = df['high'].iloc[-10:-1].max(), df['low'].iloc[-10:-1].min()
        tenkan_prev = (high_prev_9 + low_prev_9) / 2.0
        
        high_26, low_26 = df['high'].tail(26).max(), df['low'].tail(26).min()
        kijun_cur = (high_26 + low_26) / 2.0
        high_prev_26, low_prev_26 = df['high'].iloc[-27:-1].max(), df['low'].iloc[-27:-1].min()
        kijun_prev = (high_prev_26 + low_prev_26) / 2.0
        
        tenkan_kijun_crossed = (tenkan_cur > kijun_cur) and (tenkan_prev <= kijun_prev)
        slope_tenkan = float(np.arctan((tenkan_cur - tenkan_prev) / max(1.0, close * 0.001)) * (180 / np.pi))
        slope_kijun = float(np.arctan((kijun_cur - kijun_prev) / max(1.0, close * 0.001)) * (180 / np.pi))
        steep_ichimoku = abs(slope_tenkan) >= 60 or abs(slope_kijun) >= 60
        vwap_cross_now = close > vwap and prev_close <= vwap
        
        micro_schools = {
            "1. شمعة الحالية: كسر هيكل لحظي (BOS)": {"Status": realtime_bos, "Detail": f"اختراق قمة الـ 15 شمعة بإغلاق {round(close,2)}" if realtime_bos else "لم يحدث BOS في الشمعة الأخيرة"},
            "2. شمعة الحالية: سحب سيولة وتغيير شخصية (CHoCH)": {"Status": realtime_choch, "Detail": "حدث سحب سيولة تحت القاع وارتداد فوري" if realtime_choch else "لا يوجد CHoCH لحظي"},
            "3. شمعة الحالية: الارتداد من الفجوة (FVG & OB)": {"Status": fvg_active_now or bullish_ob_bounce, "Detail": "ارتداد صعودي من منطقة طلب أو فجوة سعرية نشطة" if (fvg_active_now or bullish_ob_bounce) else "السعر بعيد عن مناطق FVG الحالية"},
            "4. إشيموكو اللحظي: تقاطع خطي التحول والأساس": {"Status": tenkan_kijun_crossed, "Detail": f"تقاطع خط التحول مع الأساس في الشمعة الحالية" if tenkan_kijun_crossed else "لا يوجد تقاطع جديد لإشيموكو"},
            "5. إشيموكو اللحظي: زوايا الميل الحادة (>60° عمودي)": {"Status": steep_ichimoku, "Detail": f"زاوية ميل خط التحول ({round(slope_tenkan,1)}°) والأساس ({round(slope_kijun,1)}°)"},
            "6. التقاطع اللحظي النشط مع خط الـ VWAP": {"Status": vwap_cross_now, "Detail": f"اختراق مباشر للـ VWAP ({round(vwap,2)}) في الشمعة الأخيرة" if vwap_cross_now else "السعر مستمر فوق الـ VWAP"},
            "7. الفوليوم المؤسسي الانفجاري للشمعة الحالية": {"Status": vol_x >= 1.5, "Detail": f"مضاعف فوليوم الشمعة ({vol_x}x) يؤكد ضغطاً حاداً" if vol_x >= 1.5 else f"فوليوم الشمعة هادئ ({vol_x}x)"}
        }
        
        micro_passed = sum(1 for v in micro_schools.values() if v["Status"])
        micro_score = round((micro_passed / len(micro_schools)) * 100, 1)
        
        return {
            "Symbol": symbol,
            "Close": round(close, 2),
            "Macro Score": macro_score,
            "Macro Schools": macro_schools,
            "Micro Score": micro_score,
            "Micro Schools": micro_schools,
            "RSI": round(rsi, 1),
            "VWAP": round(vwap, 2),
            "Slope MA": round(slope_ma, 1),
            "Volume Multiplier": f"{vol_x}x",
            "Verdict": "توافق مؤسسي استثنائي للسهم والشمعة الحالية معاً 🚀" if macro_score >= 70 and micro_score >= 40 else ("وضع إيجابي عام للسهم - مراقبة تفاعل الشمعة الحالية ⚖️" if macro_score >= 50 else "حياد أو ضعف هيكلي حالياً ⚠️")
        }

# ------------------------------------------------------------------------------
# 5. REAL BACKTEST ENGINE
# ------------------------------------------------------------------------------
class RealisticBacktestEngine:
    @staticmethod
    def run_backtest(symbol: str, timeframe: str, opp_type: str, use_chandler: bool) -> Dict[str, Any]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe)
        if df.empty or len(df) < 50: return {"Error": "بيانات غير كافية لإجراء باك تيست حقيقي."}
        
        trades = []
        in_trade = False
        entry_price, sl_price, tp_price = 0.0, 0.0, 0.0
        tr = np.maximum(df['high'] - df['low'], np.maximum((df['high'] - df['close'].shift(1)).abs(), (df['low'] - df['close'].shift(1)).abs()))
        atr = tr.rolling(14).mean()
        
        for i in range(30, len(df) - 1):
            sub = df.iloc[:i]
            c_close, c_low, c_high = float(sub['close'].iloc[-1]), float(sub['low'].iloc[-1]), float(sub['high'].iloc[-1])
            c_atr = float(atr.iloc[i]) if not np.isnan(atr.iloc[i]) else c_close * 0.02
            
            if not in_trade:
                signal = False
                if opp_type == "Breakout": signal = c_close > sub['high'].iloc[-21:-1].max()
                elif opp_type == "Bottom Reversal": signal = c_low <= sub['low'].iloc[-21:-1].min() and c_close > float(sub['open'].iloc[-1])
                elif opp_type == "Retest": signal = abs(c_low - float(sub['close'].tail(20).mean())) <= c_atr
                elif opp_type == "Liquidity Sweep": signal = c_low < sub['low'].iloc[-21:-1].min() and c_close > sub['low'].iloc[-21:-1].min()
                else: signal = c_close > float(sub['close'].tail(50).mean())
                
                if signal:
                    in_trade = True
                    entry_price = c_close
                    mult = 1.2 if use_chandler else 1.5
                    sl_price = entry_price - (mult * c_atr)
                    tp_price = entry_price + (2.0 * mult * c_atr)
            else:
                if c_low <= sl_price:
                    trades.append({"result": "Loss", "pnl_pct": ((sl_price - entry_price) / entry_price) * 100})
                    in_trade = False
                elif c_high >= tp_price:
                    trades.append({"result": "Win", "pnl_pct": ((tp_price - entry_price) / entry_price) * 100})
                    in_trade = False
                    
        if not trades: return {"Total Trades": 0, "Message": "لم تظهر إشارات مطابقة للمعايير في الفترات التاريخية."}
        
        wins = [t for t in trades if t['result'] == 'Win']
        losses = [t for t in trades if t['result'] == 'Loss']
        win_rate = round((len(wins) / len(trades)) * 100, 1)
        gross_gain = sum(t['pnl_pct'] for t in wins)
        gross_loss = abs(sum(t['pnl_pct'] for t in losses))
        
        return {
            "Total Trades": len(trades),
            "Wins": len(wins),
            "Losses": len(losses),
            "Win Rate": f"{win_rate}%",
            "Profit Factor": round(gross_gain / max(0.01, gross_loss), 2),
            "Expectancy (%)": round((win_rate / 100.0 * (gross_gain / max(1, len(wins)))) - ((1 - win_rate / 100.0) * (gross_loss / max(1, len(losses)))), 2),
            "Avg PnL per Trade (%)": f"{round(sum(t['pnl_pct'] for t in trades) / len(trades), 2)}%"
        }

# ------------------------------------------------------------------------------
# 6. MAIN APPLICATION LAYOUT
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION v12.00 - Secure Login</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("اسم المستخدم (Username):")
            p = st.text_input("كلمة المرور (Password):", type="password")
            if st.form_submit_button("تسجيل الدخول") and u == "admin" and p == "admin":
                st.session_state["authenticated"] = True
                st.rerun()
            elif u: st.error("استخدم admin للطرفين.")
        return

    st.sidebar.title("🛡️ SABRY VISION v12.00")
    if st.sidebar.button("تسجيل الخروج 🚪"):
        st.session_state["authenticated"] = False
        st.rerun()

    market_list_name = st.sidebar.selectbox("اختر السوق الاستثماري:", list(st.session_state["market_lists_repo"].keys()))
    symbols_to_scan = st.session_state["market_lists_repo"][market_list_name]
    timeframe_options = ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"]
    selected_tf = st.sidebar.selectbox("الإطار الزمني للفحص والتداول:", timeframe_options, index=2)
    
    selected_opportunities = st.sidebar.multiselect(
        "🎯 نوع الفرص المراد اقتناصها:",
        ["الكل (جميع الفرص)", "Breakout", "Bottom Reversal", "Retest", "Liquidity Sweep", "Setup"],
        default=["الكل (جميع الفرص)"]
    )

    st.title("🛡️ SABRY VISION - Master Quant Terminal v12.00")
    st.markdown("---")

    tab1, tab2 = st.tabs([
        "🚀 1. سكانر السوق الشامل وتصدير الفرص (TradingView)",
        "🧠 2. التقارير الهجينة: تقييم السهم العام + التدقيق اللحظي للشمعة والباك تيست"
    ])

    with tab1:
        st.subheader(f"🚀 مسح السوق الشامل - {market_list_name} ({len(symbols_to_scan)} أصل)")
        if st.button("🔥 تشغيل سكانر السيولة والفرص الكمية", type="primary"):
            df_conf, df_set, breadth = HybridQuantEngine.bulk_scan(symbols_to_scan, selected_tf, selected_opportunities)
            st.session_state["confirmed_opportunities"] = df_conf
            st.session_state["setup_opportunities"] = df_set
            st.session_state["market_breadth_data"] = breadth

        breadth_data = st.session_state.get("market_breadth_data", {})
        if breadth_data:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("قوة الاتجاه العام", breadth_data.get("Market Strength"))
            m2.metric("تقييم السيولة التراكمية", breadth_data.get("Liquidity Eval"))
            m3.metric("نسبة اتساع السوق", breadth_data.get("Breadth Ratio"))
            m4.metric("الأسهم المكتشفة", f"{breadth_data.get('Advancing')}/{breadth_data.get('Total')}")
            st.markdown("---")

        df_confirmed = st.session_state.get("confirmed_opportunities", pd.DataFrame())
        df_setup = st.session_state.get("setup_opportunities", pd.DataFrame())

        st.markdown("### 🎯 1. جدول الفرص المؤكدة (المنفردة والمزدوجة والتركيبية)")
        if not df_confirmed.empty:
            st.dataframe(df_confirmed.drop(columns=["Raw Volume $", "Is Pure Setup"], errors="ignore"), use_container_width=True)
        else:
            st.info("لا توجد فرص مؤكدة حالياً، اضغط على زر المسح بالأعلى.")

        st.markdown("---")
        st.markdown("### ⏳ 2. جدول فرص الـ Setup النقية (قيد التكون)")
        if not df_setup.empty:
            st.dataframe(df_setup.drop(columns=["Raw Volume $", "Is Pure Setup"], errors="ignore"), use_container_width=True)
        else:
            st.info("لا توجد فرص Setup منفردة حالياً.")

        st.markdown("---")
        st.markdown("### 📋 بوكس نسخ الأسهم المباشر لتشارتات TradingView")
        col_e1, col_e2 = st.columns([1, 2])
        with col_e1:
            target_table = st.selectbox("اختر الجدول للنسخ:", ["جدول الفرص المؤكدة", "جدول فرص الـ Setup"])
            copy_count = st.selectbox("عدد الأسهم:", ["أول 10 أسهم", "أول 20 سهم", "جميع الأسهم المتاحة"])
        target_df = df_confirmed if target_table == "جدول الفرص المؤكدة" else df_setup
        with col_e2:
            if not target_df.empty and "رمز السهم" in target_df.columns:
                codes = target_df["رمز السهم"].tolist()
                if copy_count == "أول 10 أسهم": codes = codes[:10]
                elif copy_count == "أول 20 سهم": codes = codes[:20]
                formatted = ", ".join([f"TADAWUL:{c}" if "السعودي" in market_list_name else c for c in codes])
                st.text_area("انسخ الأكواد للصقها مباشرة في TradingView:", value=formatted, height=120)
            else:
                st.write("قم بتشغيل السكانر لتوليد الأكواد.")

    with tab2:
        st.subheader("🧠 التقرير الهجيني الشامل: تقييم السهم العام + التدقيق اللحظي للشمعة الحالية")
        
        select_mode = st.radio("طريقة اختيار الأصل للتحليل:", ["إدخال رمز السهم يدويًا", "من جدول الفرص المؤكدة (رقم 1)", "من جدول فرص الـ Setup (رقم 2)"], horizontal=True)
        
        selected_stock_code = ""
        if select_mode == "إدخال رمز السهم يدويًا":
            selected_stock_code = st.text_input("أدخل رمز السهم (مثال: 1120.SR أو AAPL):", value="2222.SR")
        elif select_mode == "من جدول الفرص المؤكدة (رقم 1)":
            if not df_confirmed.empty: selected_stock_code = st.selectbox("اختر السهم:", df_confirmed["اسم/رمز الأصل"].tolist())
            else: st.warning("جدول الفرص المؤكدة فارغ.")
        else:
            if not df_setup.empty: selected_stock_code = st.selectbox("اختر السهم:", df_setup["اسم/رمز الأصل"].tolist())
            else: st.warning("جدول الـ Setup فارغ.")

        if st.button("📊 توليد التقرير الهجيني الشامل (الملخص + المدارس + التدقيق اللحظي)"):
            if selected_stock_code:
                with st.spinner(f"جاري إعداد التقرير الهجيني المدمج لـ {selected_stock_code}..."):
                    audit = HybridQuantEngine.hybrid_full_audit(selected_stock_code, selected_tf)
                    if audit:
                        st.markdown(f"### 📋 التقارير الفنية الهجينة للأصل: **{selected_stock_code}** (الفريم: {selected_tf})")
                        st.info(f"💡 **الملخص البصري السريع للقرار:** {audit.get('Verdict')} | **السكور العام للسهم:** {audit.get('Macro Score')}% | **سكور الشمعة اللحظي:** {audit.get('Micro Score')}%")
                        
                        # --- القسم الأول: جدول التقييم الشامل للمدارس الكبرى ---
                        st.markdown("#### 🎯 أ. جدول الفحص البصري الشامل للمدارس الكبرى والمؤشرات للسهم ككل:")
                        macro_data = audit.get("Macro Schools", {})
                        macro_df = pd.DataFrame([
                            {"المدرسة / المؤشر الفني": k, "الحالة الفنية": "✅ إيجابي / متوافق" if v["Status"] else "❌ غير متوافق", "التقييم المؤسسي": v["Rating"], "التفاصيل": v["Desc"]}
                            for k, v in macro_data.items()
                        ])
                        st.table(macro_df)
                        
                        # --- القسم الثاني: التدقيق اللحظي المجهري للشمعة الحالية ---
                        st.markdown("#### ⚡ ب. التدقيق اللحظي المجهري للشمعة الحالية (BOS, CHoCH وإشيموكو اللحظي):")
                        micro_data = audit.get("Micro Schools", {})
                        micro_df = pd.DataFrame([
                            {"مدرسة التحليل / المؤشر اللحظي": k, "حالة الشمعة الحالية": "✅ تحقق الآن" if v["Status"] else "⬜ لم يتحقق في الشمعة", "التفاصيل التدقيقية": v["Detail"]}
                            for k, v in micro_data.items()
                        ])
                        st.table(micro_df)
                        
                        # --- القسم الثالث: المؤشرات الرقمية وزوايا الميل ---
                        st.markdown("#### 📈 ج. المؤشرات الرقمية وزوايا الانفجار السعري:")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("قيمة الـ RSI", audit.get("RSI"))
                        c2.metric("مستوى الـ VWAP", audit.get("VWAP"))
                        c3.metric("زاوية ميل المتوسطات", f"{audit.get('Slope MA')}°")
                        c4.metric("مضاعف الفوليوم", audit.get("Volume Multiplier"))

        st.markdown("---")
        st.markdown("### 🔬 د. إعدادات محرك الباك تيست الواقعي التاريخي")
        cb1, cb2, cb3 = st.columns(3)
        with cb1: bt_strat = st.selectbox("استراتيجية الاختبار:", ["Breakout", "Bottom Reversal", "Retest", "Liquidity Sweep", "Setup"])
        with cb2: chandler_opt = st.selectbox("Chandler ATR Stop:", ["ON", "OFF"])
        with cb3: bt_timeframe = st.selectbox("إطار الباك تيست الزمني:", timeframe_options, index=3)
        
        if st.button("🚀 تشغيل الباك تيست التاريخي الفعلي", type="primary"):
            if selected_stock_code:
                with st.spinner("جاري تنفيذ الباك تيست التاريخي..."):
                    res_bt = RealisticBacktestEngine.run_backtest(selected_stock_code, bt_timeframe, bt_strat, chandler_opt == "ON")
                    if "Error" in res_bt: st.error(res_bt["Error"])
                    elif "Message" in res_bt: st.warning(res_bt["Message"])
                    else:
                        st.success(f"✅ تم اجتياز الباك تيست بنجاح للسهم {selected_stock_code}")
                        b1, b2, b3, b4 = st.columns(4)
                        b1.metric("إجمالي الصفقات", res_bt.get("Total Trades"))
                        b2.metric("نسبة النجاح (Win Rate)", res_bt.get("Win Rate"))
                        b3.metric("معامل الربحية", res_bt.get("Profit Factor"))
                        b4.metric("التوقع المالي", res_bt.get("Expectancy (%)"))
                        
                        b5, b6, b7 = st.columns(3)
                        b5.metric("الصفقات الرابحة 🟢", res_bt.get("Wins"))
                        b6.metric("الصفقات الخاسرة 🔴", res_bt.get("Losses"))
                        b7.metric("متوسط ربح/خسارة الصفقة", res_bt.get("Avg PnL per Trade (%)"))

if __name__ == "__main__":
    main()
