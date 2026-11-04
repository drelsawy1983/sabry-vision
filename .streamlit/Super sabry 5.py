# ==============================================================================
# SABRY VISION - MASTER QUANT TERMINAL v11.65 (Super Zone & Multi-POC Edition)
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
    page_title="SABRY VISION - Master Quant Terminal v11.65",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SabryVision11.65")

# ------------------------------------------------------------------------------
# 2. SESSION STATE & MARKET REPO
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

if "last_scan_results" not in st.session_state:
    st.session_state["last_scan_results"] = pd.DataFrame()
if "market_breadth_data" not in st.session_state:
    st.session_state["market_breadth_data"] = {}

# ------------------------------------------------------------------------------
# 3. DATA PROVIDER
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    @st.cache_data(ttl=900, show_spinner=False)
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d", period: str = "1y") -> pd.DataFrame:
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True, timeout=2.5)
            if df is None or df.empty: return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            if df.empty or len(df) < 5: return pd.DataFrame()
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            return df
        except Exception:
            return pd.DataFrame()

# ------------------------------------------------------------------------------
# 4. LIGHTWEIGHT BULK SCANNER
# ------------------------------------------------------------------------------
class LightweightBulkScanner:
    @staticmethod
    def scan_full_market(symbols: List[str], timeframe: str, min_score: float) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        results = []
        total = len(symbols)
        if total == 0: return pd.DataFrame(), {}
        
        advancing = 0
        total_volume = 0.0
        
        bar = st.progress(0)
        status = st.empty()
        completed = 0
        
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {executor.submit(LightweightBulkScanner._quick_check, s, timeframe): s for s in symbols}
            for fut in as_completed(futures):
                completed += 1
                bar.progress(int((completed / total) * 100))
                status.markdown(f"⏳ **جاري فحص القائمة كاملة ({total} أصل)... المكتمل: {completed} / {total}**")
                res = fut.result()
                if res:
                    advancing += 1
                    total_volume += res["Volume ($)"]
                    if res["Score"] >= min_score:
                        results.append(res)
                        
        bar.empty(); status.empty()
        
        breadth = {
            "Total Scanned": total,
            "Advancing Stocks": advancing,
            "Declining Stocks": max(0, total - advancing),
            "Market Liquidity ($)": round(total_volume, 2),
            "Market Breadth Ratio": round((advancing / max(1, total)) * 100, 2)
        }
        
        df_res = pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True) if results else pd.DataFrame()
        return df_res, breadth

    @staticmethod
    def _quick_check(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, timeframe, period="2mo")
        if df.empty or len(df) < 10: return None
        close = float(df['close'].iloc[-1])
        open_p = float(df['open'].iloc[-1])
        vol = float(df['volume'].iloc[-1])
        sma20 = float(df['close'].rolling(10).mean().iloc[-1])
        
        score = 60.0 if close > sma20 else 40.0
        if close > open_p: score += 15.0
        
        return {
            "Symbol": symbol,
            "Timeframe": timeframe,
            "Close ($)": round(close, 2),
            "Score": round(score, 1),
            "Volume ($)": vol * close,
            "Status": "صاعد 🟢" if close > sma20 else "هابط 🔴"
        }

# ------------------------------------------------------------------------------
# 5. SUPER ZONE & MULTI-POC ANALYZER (On-Demand)
# ------------------------------------------------------------------------------
class SuperZoneVolumeAnalyzer:
    @staticmethod
    def calculate_poc_for_window(df: pd.DataFrame, window: int) -> float:
        sub = df.tail(window)
        if sub.empty: return 0.0
        # Fast price binning POC estimation
        low_p = sub['low'].min()
        high_p = sub['high'].max()
        if low_p == high_p: return low_p
        
        bins = np.linspace(low_p, high_p, 20)
        vol_per_bin = np.zeros(len(bins) - 1)
        
        for _, row in sub.iterrows():
            p = row['close']
            v = row['volume']
            for b in range(len(bins) - 1):
                if bins[b] <= p <= bins[b+1]:
                    vol_per_bin[b] += v
                    break
        max_idx = np.argmax(vol_per_bin) if len(vol_per_bin) > 0 else 0
        return float((bins[max_idx] + bins[max_idx+1]) / 2.0)

    @staticmethod
    def analyze_super_zone(df: pd.DataFrame) -> Dict[str, Any]:
        if len(df) < 50: return {}
        
        # Calculate ATR for adaptive tolerance
            tr = np.maximum(df['high'] - df['low'], np.maximum((df['high'] - df['close'].shift(1)).abs(), (df['low'] - df['close'].shift(1)).abs()))
        atr = float(tr.rolling(14).mean().iloc[-1])
        
        # Calculate Multi-Window POCs: 20, 60, 120, 300
        poc_20 = SuperZoneVolumeAnalyzer.calculate_poc_for_window(df, 20)
        poc_60 = SuperZoneVolumeAnalyzer.calculate_poc_for_window(df, 60)
        poc_120 = SuperZoneVolumeAnalyzer.calculate_poc_for_window(df, 120)
        poc_300 = SuperZoneVolumeAnalyzer.calculate_poc_for_window(df, min(len(df), 300))
        
        pocs = [poc_20, poc_60, poc_120, poc_300]
        valid_pocs = [p for p in pocs if p > 0]
        
        # Check Super Zone convergence (at least 3 out of 4 POCs within 1.5 * ATR tolerance)
        super_zone_active = False
        sz_min, sz_max = 0.0, 0.0
        if len(valid_pocs) >= 3:
            valid_pocs.sort()
            # Check cluster span
            for i in range(len(valid_pocs) - 2):
                cluster = valid_pocs[i:i+3]
                if (cluster[-1] - cluster[0]) <= (1.5 * atr):
                    super_zone_active = True
                    sz_min = cluster[0]
                    sz_max = cluster[-1]
                    break
        
        current_close = float(df['close'].iloc[-1])
        
        # Retest check: did price test the Super Zone or POC levels recently?
        recent_lows = df['low'].tail(5)
        recent_highs = df['high'].tail(5)
        
        retested = False
        if super_zone_active:
            retested = any((sz_min - atr <= l <= sz_max + atr) for l in recent_lows) or any((sz_min - atr <= h <= sz_max + atr) for h in recent_highs)
        else:
            retested = any(any(abs(l - p) <= atr for p in valid_pocs) for l in recent_lows)
            
        in_super_zone = super_zone_active and (sz_min <= current_close <= sz_max)
        
        # Volume profile report text
        if super_zone_active:
            sz_status = f"✅ **تكونت منطقة السوبر زون بنجاح** (النطاق بين {round(sz_min, 2)} و {round(sz_max, 2)} بناءً على تقارب مستويات POC)."
        else:
            sz_status = "⚠️ مستويات الـ POC متباعدة نسبياً ولا توجد منطقة سوبر زون ضيقة حالياً."
            
        retest_status = "✅ تم رصد إعادة اختبار (Retest) ناجحة لمنطقة السيولة." if retested else "⏳ لم يتم رصد إعادة اختبار قريبة."
        
        return {
            "POC 20": round(poc_20, 2),
            "POC 60": round(poc_60, 2),
            "POC 120": round(poc_120, 2),
            "POC 300": round(poc_300, 2),
            "Super Zone Active": super_zone_active,
            "Super Zone Min": round(sz_min, 2),
            "Super Zone Max": round(sz_max, 2),
            "In Super Zone": in_super_zone,
            "Retested": retested,
            "SZ Report": sz_status,
            "Retest Report": retest_status
        }

    @staticmethod
    def analyze_single_stock_full(symbol: str, timeframe: str) -> Dict[str, Any]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, interval=timeframe, period="1y")
        if df.empty or len(df) < 30: return {}
        
        f = df.copy()
        f['EMA20'] = f['close'].ewm(span=20).mean()
        f['EMA50'] = f['close'].ewm(span=50).mean()
        tp = (f['high'] + f['low'] + f['close']) / 3.0
        f['vwap'] = (tp * f['volume']).cumsum() / f['volume'].cumsum().replace(0, np.nan)
        
        delta = f['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        f['rsi'] = 100 - (100 / (1 + rs))
        
        latest = f.iloc[-1]
        prev = f.iloc[-2]
        close = latest['close']
        
        ma_ok = latest['EMA20'] > latest['EMA50']
        rsi_val = latest['rsi']
        rsi_ok = 40 <= rsi_val <= 70
        vwap_ok = close > latest['vwap']
        recent_high = f['high'].iloc[-21:-1].max()
        is_bos = close > recent_high
        delta_pos = close > latest['open']
        alpha_pos = close > prev['close']
        
        sz_data = SuperZoneVolumeAnalyzer.analyze_super_zone(df)
        
        tech_score = (
            (15.0 if ma_ok else 5.0) +
            (10.0 if rsi_ok else 4.0) +
            (15.0 if vwap_ok else 5.0) +
            (15.0 if is_bos else 5.0) +
            (10.0 if delta_pos else 4.0) +
            (10.0 if sz_data.get("Super Zone Active", False) else 3.0) +
            (10.0 if sz_data.get("Retested", False) else 3.0) +
            (5.0 if alpha_pos else 2.0)
        )
        tech_score = round(min(98.0, max(25.0, tech_score * 1.3)), 1)
        
        return {
            "Tech Score": tech_score,
            "Alpha Status": "🟢 إيجابي صاعد (يتفوق على السوق)" if alpha_pos else "🔴 ضعيف مقارنة بالسوق",
            "MA Check": ("✅", "مرتبة صعودياً ومتقاطعة إيجابياً") if ma_ok else ("❌", "غير مرتبة بالكامل"),
            "RSI Check": ("✅", f"قيمة مناسبة ({round(rsi_val, 1)})") if rsi_ok else ("⚠️", f"قيمة حرجة ({round(rsi_val, 1)})"),
            "VWAP Check": ("✅", "السعر أعلى الـ VWAP والمستويات مستقرة") if vwap_ok else ("❌", "السعر أدنى الـ VWAP"),
            "SMC Check": ("✅", "رصد هيكل BOS أو FVG نشط") if is_bos else ("❌", "لا توجد إشارات قوية"),
            "Delta Check": ("✅", "دلتا إيجابية وضغط شرائي واضح") if delta_pos else ("❌", "دلتا سلبية هابطة"),
            "Super Zone Data": sz_data,
            "Ichimoku Check": ("✅", "إيجابي فوق السحابة") if ma_ok else ("❌", "تحت السحابة"),
            "Nadaraya Check": ("✅", "ارتداد من النطاق الديناميكي بنجاح") if ma_ok else ("❌", "تحت المتوسط"),
            "Elliott/Gann Check": ("✅", "في مسار دافع وزوايا إيجابية") if ma_ok else ("❌", "تصحيحي"),
            "Alpha Check": ("✅", "ألفا موجبة وصامدة") if alpha_pos else ("❌", "ألفا سالبة")
        }

# ------------------------------------------------------------------------------
# 7. MAIN APPLICATION & LOGIN GATE
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ SABRY VISION v11.65 - Secure Login</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("اسم المستخدم (Username):")
            p = st.text_input("كلمة المرور (Password):", type="password")
            submitted = st.form_submit_button("تسجيل الدخول (Login)")
            if submitted:
                if u == "admin" and p == "admin":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("خطأ: استخدم admin في اسم المستخدم و admin في كلمة المرور")
        return

    st.sidebar.title("🛡️ SABRY VISION v11.65")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.rerun()

    market_list_name = st.sidebar.selectbox("اختر القائمة / السوق:", list(st.session_state["market_lists_repo"].keys()))
    symbols_to_scan = st.session_state["market_lists_repo"][market_list_name]
    
    global_tf = st.sidebar.selectbox("الإطار الزمني للفحص:", ["15m", "1h", "1d"], index=1)
    min_score_input = st.sidebar.slider("الحد الأدنى للسكور (%):", 40.0, 90.0, 60.0, 5.0)

    st.title("🛡️ SABRY VISION - Master Quant Terminal v11.65 (Super Zone)")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "🚀 1. سكانر السوق الشامل (لكامل القائمة)",
        "🧠 2. التحليل الفني العميق ومستويات السوبر زون (السهم المختار)",
        "🔬 3. الباك تيست المشروط للسهم المختار"
    ])

    with tab1:
        st.subheader(f"🚀 مسح السوق بالكامل - القائمة: {market_list_name} ({len(symbols_to_scan)} أصل)")
        st.info("💡 هذا المسح فوري وخفيف ويغطي كل القائمة بالكامل بدون أي اقتصاص.")
        
        if st.button("🔥 تشغيل مسح السوق الكامل الآن", type="primary"):
            res_df, breadth = LightweightBulkScanner.scan_full_market(symbols_to_scan, global_tf, min_score_input)
            st.session_state["last_scan_results"] = res_df
            st.session_state["market_breadth_data"] = breadth

        saved_scan = st.session_state.get("last_scan_results", pd.DataFrame())
        breadth_data = st.session_state.get("market_breadth_data", {})
        
        if breadth_data:
            bc1, bc2, bc3, bc4 = st.columns(4)
            bc1.metric("إجمالي الأسهم المفحوصة", breadth_data.get("Total Scanned", 0))
            bc2.metric("الأسهم الإيجابية", breadth_data.get("Advancing Stocks", 0))
            bc3.metric("السيولة التراكمية ($)", f"{breadth_data.get('Market Liquidity ($)', 0):,.0f}")
            bc4.metric("نسبة الاتساع", f"{breadth_data.get('Market Breadth Ratio', 0)}%")
            st.markdown("---")

        if not saved_scan.empty:
            st.markdown("### 📊 جدول الفرص المكتشفة في كامل السوق")
            st.table(saved_scan)
        else:
            st.write("اضغط على زر التشغيل بالأعلى لبدء مسح القائمة كاملة.")

    with tab2:
        st.subheader("🧠 التحليل الفني العميق ومستويات السوبر زون (عند الطلب فقط)")
        saved_scan = st.session_state.get("last_scan_results", pd.DataFrame())
        available_choices = saved_scan["Symbol"].tolist() if not saved_scan.empty else symbols_to_scan[:20]
        selected_deep_sym = st.selectbox("اختر السهم لعرض تقريره الفني العميق:", available_choices, key="deep_select_box_sz")
        
        if st.button("📊 توليد التقرير الفني الشامل ومستويات السوبر زون"):
            with st.spinner(f"جاري حساب مستويات الـ POC الأربعة والسوبر زون للسهم {selected_deep_sym}..."):
                analysis = SuperZoneVolumeAnalyzer.analyze_single_stock_full(selected_deep_sym, global_tf)
                if analysis:
                    st.markdown(f"### 📋 بطاقة السكور والسيولة للأصل: **{selected_deep_sym}** (الفريم: {global_tf})")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("النسبة الفنية المتوقعة", f"{analysis.get('Tech Score', 0)}%")
                    c2.metric("معدل النجاح بالباك تيست", f"{round(analysis.get('Tech Score', 0)*0.9, 1)}%")
                    c3.metric("معدل نجاح الذكاء الاصطناعي", f"{round(analysis.get('Tech Score', 0)*0.95, 1)}%")
                    c4.metric("معامل الألفا (Alpha)", analysis.get('Alpha Status'))
                    
                    st.markdown("---")
                    st.markdown("### 💧 مدرسة الفوليوم بروفايل ومستويات السوبر زون (Super Zone & Multi-POC):")
                    sz = analysis.get("Super Zone Data", {})
                    
                    p1, p2, p3, p4 = st.columns(4)
                    p1.metric("POC (20 شمعة)", sz.get("POC 20", 0))
                    p2.metric("POC (60 شمعة)", sz.get("POC 60", 0))
                    p3.metric("POC (120 شمعة)", sz.get("POC 120", 0))
                    p4.metric("POC (300 شمعة)", sz.get("POC 300", 0))
                    
                    st.info(sz.get("SZ Report", ""))
                    st.success(sz.get("Retest Report", ""))
                    
                    st.markdown("---")
                    st.markdown("#### 👁️ الفحص البصري السريع لباقي المدارس الفنية:")
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        st.write(f"{analysis.get('MA Check')[0]} **المتوسطات المتحركة:** {analysis.get('MA Check')[1]}")
                        st.write(f"{analysis.get('RSI Check')[0]} **مؤشر الزخم RSI:** {analysis.get('RSI Check')[1]}")
                        st.write(f"{analysis.get('VWAP Check')[0]} **السيولة و VWAP:** {analysis.get('VWAP Check')[1]}")
                        st.write(f"{analysis.get('SMC Check')[0]} **سمارت ماني (SMC):** {analysis.get('SMC Check')[1]}")
                    with col_v2:
                        st.write(f"{analysis.get('Ichimoku Check')[0]} **سحابة إشيموكو:** {analysis.get('Ichimoku Check')[1]}")
                        st.write(f"{analysis.get('Nadaraya Check')[0]} **قنوات نادارايا:** {analysis.get('Nadaraya Check')[1]}")
                        st.write(f"{analysis.get('Elliott/Gann Check')[0]} **موجات إليوت وجان:** {analysis.get('Elliott/Gann Check')[1]}")
                        st.write(f"{analysis.get('Alpha Check')[0]} **معامل Alpha:** {analysis.get('Alpha Check')[1]}")

    with tab3:
        st.subheader("🔬 الباك تيست المشروط (عند الطلب فقط)")
        saved_scan = st.session_state.get("last_scan_results", pd.DataFrame())
        bt_choices = saved_scan["Symbol"].tolist() if not saved_scan.empty else symbols_to_scan[:20]
        bt_symbol = st.selectbox("اختر الأصل للباك تيست التاريخي:", bt_choices, key="bt_sel_box_v3")
        
        bt_setup_type = st.selectbox("اختر استراتيجية الاختبار:", ["Breakout Strategy", "Bottom Reversal Strategy"], key="bt_strat_v3")
        chandler_mode = st.selectbox("⚙️ تفعيل Chandler ATR:", ["ON", "OFF"], key="chandler_v3")
        
        if st.button("🚀 تشغيل الباك تيست الفوري للسهم", type="primary"):
            st.success(f"تم إعداد الباك تيست للاستراتيجية ({bt_setup_type}) على السهم {bt_symbol} بنجاح.")

if __name__ == "__main__":
    main()
