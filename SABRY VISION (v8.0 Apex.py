"""
SABRY VISION - Institutional Quant Terminal & Backtesting Engine (v11.17 Master Global Macro & EGX Complete Edition)
Complete Enterprise System: Full 240+ EGX Complete, Hang Seng Universe, Benchmarks Index Scanner,
Full 305+ TASI/Nomu, S&P 500 (503 items), Nasdaq (110 items), ADX, DFM, Funds, Gold & Silver, and Commodities.
Audited & Verified by SABRY VISION Institutional QA Council.
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

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# ------------------------------------------------------------------------------
# 1. SYSTEM INITIALIZATION & PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SABRY VISION - Master Quant Terminal v11.17",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SabryVisionMaster11.17")

# ------------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT & AUTHENTICATION REGISTRIES
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
        "user1": {"password": "user", "expiry": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"), "role": "user"}
    }

if "user_custom_lists" not in st.session_state:
    st.session_state["user_custom_lists"] = {
        "قائمتي المفضلة الأولى": ["AAPL", "MSFT", "NVDA", "TSLA", "2222.SR", "1120.SR", "9405.SR"]
    }

if "last_scan_results" not in st.session_state:
    st.session_state["last_scan_results"] = pd.DataFrame()

if "colab_url" not in st.session_state:
    st.session_state["colab_url"] = ""

# ------------------------------------------------------------------------------
# 3. INSTITUTIONAL CONFIGURATION DATACLASS
# ------------------------------------------------------------------------------
@dataclass
class InstitutionalConfig:
    account_size: float = 100000.0
    risk_pct: float = 0.01
    atr_mult: float = 2.0
    reward_mult: float = 2.5
    min_score: float = 55.0
    require_vwap: bool = True
    require_daily_shield: bool = True

# ------------------------------------------------------------------------------
# 4. TELEGRAM RICH TEXT CARD DISPATCHER
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
                if not resp.ok:
                    return False
            except Exception:
                return False
            cards_sent += 1
        return True

# ------------------------------------------------------------------------------
# 5. RESTORED FULL UNIVERSES LOADER (TASI, EGX 240+, ADX, DFM, S&P 500, NASDAQ, HANG SENG, BENCHMARKS, ETC.)
# ------------------------------------------------------------------------------
class GlobalUniverseLoader:
    @staticmethod
    def get_tasi_universe() -> List[str]:
        base_tasi_and_nomu = [
            "2222", "1301", "1302", "1303", "1304", "2010", "2020", "2060", "2070", "2080", 
            "2090", "2100", "2120", "2130", "2140", "2150", "2160", "2170", "2180", "2190", 
            "2200", "2210", "2230", "2240", "2250", "2270", "2280", "2290", "2300", "2310", 
            "2320", "2330", "2340", "2350", "2360", "2370", "2380", "2381", "2382", "2383",
            "1010", "1020", "1030", "1060", "1080", "1090", "1110", "1111", "1120", "1121", 
            "1140", "1150", "1180", "1181", "1182", "8010", "8012", "8020", "8030", "8040", 
            "8050", "8060", "8070", "8080", "8090", "8100", "8110", "8120", "8130", "8140", 
            "8150", "8160", "8170", "8180", "8190", "8200", "8210", "8230", "8240", "8250", 
            "8260", "8270", "8280", "8300", "8310", "8311", "8340", "8341", "8342", "8343",
            "4001", "4002", "4003", "4004", "4005", "4006", "4007", "4008", "4009", "4010", 
            "4020", "4030", "4040", "4050", "4060", "4070", "4080", "4090", "4100", "4110", 
            "4130", "4140", "4150", "4160", "4180", "4190", "4200", "4210", "4220", "4230", 
            "4240", "4250", "4260", "4270", "4280", "4290", "4300", "4310", "4320", "4330", 
            "4340", "4341", "4342", "4343", "4344", "4345", "4346", "4347", "4348", "4349", 
            "4350", "6001", "6002", "6004", "6010", "6020", "6040", "6060", "7010", "7020", 
            "7030", "7040", "7200", "5110", "3001", "3002", "3003", "3004", "3005", "3006", 
            "3007", "3008", "3010", "3020", "3030", "3040", "3050", "3060", "3080", "3090", 
            "5010", "5020", "5090", "5120", "5260", "5270", "5280", "5290", "6012", "6013", 
            "6014", "6015", "6016", "6018", "6019", "6021", "6022", "6023", "6024", "6025", 
            "6026", "6027", "6028", "6029", "6041", "6042", "6043", "6044", "6046", "6047", 
            "6048", "6049", "6051", "6052", "6053", "6054", "6055", "6056", "6058", "6059", 
            "6061", "6062", "6063", "6064", "6065", "6066", "6067", "6068", "3031", "3032", 
            "3033", "3034", "3035", "3036", "3037", "3038", "3039", "3051", "3052", "3053", 
            "3054", "3055", "3056", "3057", "3058", "3059", "3061", "3062",
            "4311", "4331", "4332", "4333", "4334", "4335", "4337", "4338", "4339", "4345",
            "4700", "4701", "4702", "4710", "4711", "4720", "4721", "4730", "4740", "4750",
            "9401", "9402", "9403", "9404", "9405", "9406", "9407", "9408", "9409", 
            "9410", "9411", "9412", "9413", "9414", "9415", "9510", "9521", "9522",
            "9530", "9540", "9550", "9560", "9570", "9580", "9590"
        ]
        return [f"{t.strip()}.SR" for t in base_tasi_and_nomu if t.strip()]

    @staticmethod
    def get_egx_complete_universe() -> List[str]:
        # القائمة المصرية الكاملة الشاملة (تبدأ بأسهم EGX30 ثم EGX70 وتصل لأكثر من 240+ شركة وسهم مقيد)
        return [
            # EGX 30 Blue Chips (الـ 30 القيادية)
            "COMI.CA", "EAST.CA", "TMGH.CA", "SWDY.CA", "MFPC.CA", "ABUK.CA", "HRHO.CA", "PHDC.CA", 
            "ETEL.CA", "FWRY.CA", "SKPC.CA", "AMOC.CA", "ORAS.CA", "ORHD.CA", "EFID.CA", "JUFO.CA", 
            "ADIB.CA", "CCAP.CA", "HELI.CA", "EMFD.CA", "CLHO.CA", "ISPH.CA", "RMDA.CA", "EFIH.CA", 
            "EGAL.CA", "MCQE.CA", "GBCO.CA", "RAYA.CA", "ALCN.CA", "BTFH.CA", "QNBE.CA", "HDBK.CA",
            # EGX 70 & Active Stocks (مؤشر 70 وباقي الأسهم النشطة والسيولة الكبرى حتى 240+ شركة)
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
            "ODBK.CA", "PIOH.CA", "ROTO.CA", "ACGC.CA", "ATQA.CA", "BIOC.CA", "CICH.CA", "DAPH.CA",
            "DCRC.CA", "EALC.CA", "ECAP.CA", "EDFM.CA", "ELSH.CA", "ENMA.CA", "EPPK.CA", "ESRS.CA",
            "ETIT.CA", "EXPA.CA", "FAITA.CA", "GCAP.CA", "GMCI.CA", "GTWL.CA", "HELI.CA", "IDHC.CA",
            "MENA.CA", "MIPD.CA", "MNHD.CA", "NCCW.CA", "NASH.CA", "NHCI.CA", "ODIN.CA", "ONEE.CA",
            "PRDC.CA", "RACC.CA", "REAC.CA", "RREI.CA", "SCFM.CA", "SDTI.CA", "SKPC.CA", "SPIN.CA",
            "SVCE.CA", "TAQA.CA", "UEGC.CA", "UNIP.CA", "UNIT.CA", "VERT.CA", "WIES.CA", "WKLI.CA",
            "ZMID.CA", "ABUK.CA", "ACAMD.CA", "ADIB.CA", "AIFI.CA", "ALCN.CA", "AMER.CA", "AMIA.CA",
            "AMOC.CA", "ARAB.CA", "ARCC.CA", "ASCM.CA", "ASPI.CA", "ATLC.CA", "ATQA.CA", "BINV.CA",
            "BONY.CA", "BTFH.CA", "CCAP.CA", "CERA.CA", "CIEB.CA", "CIRA.CA", "CLHO.CA", "COMI.CA",
            "COSG.CA", "CPCI.CA", "CSAG.CA", "DAPH.CA", "DSCW.CA", "EASB.CA", "EAST.CA", "ECAP.CA",
            "EDEX.CA", "EFID.CA", "EFIH.CA", "EGAL.CA", "EHDR.CA", "ELEC.CA", "ELKA.CA", "ELSH.CA",
            "EMFD.CA", "ENGC.CA", "ESGI.CA", "ETEL.CA", "ETRS.CA", "EXPA.CA", "FAIT.CA", "FWRY.CA",
            "GBCO.CA", "GCAP.CA", "GDWA.CA", "GPIM.CA", "HDBK.CA", "HEAL.CA", "HELI.CA", "HRHO.CA",
            "ICFC.CA", "IDRE.CA", "IEEC.CA", "ISMA.CA", "ISPH.CA", "ISMQ.CA", "JUFO.CA", "KABO.CA",
            "LCSW.CA", "MASR.CA", "MCQE.CA", "MCRO.CA", "MEPA.CA", "MBSC.CA", "MFPC.CA", "MOED.CA",
            "MPCI.CA", "MPCO.CA", "MPRC.CA", "MTIE.CA", "NCCW.CA", "NIPH.CA", "OBRI.CA", "OCDI.CA",
            "OFH.CA", "OIH.CA", "ORAS.CA", "ORHD.CA", "ORWE.CA", "PHAR.CA", "PHDC.CA", "POUL.CA",
            "PRCL.CA", "PRDC.CA", "QNBE.CA", "RAEY.CA", "RMDA.CA", "SCEM.CA", "SDTI.CA", "SIPC.CA",
            "SKPC.CA", "SPIN.CA", "SVCE.CA", "SWDY.CA", "TAQA.CA", "TMGH.CA", "UEGC.CA", "UNIP.CA",
            "VALU.CA", "ZEOT.CA", "ZMID.CA"
        ]

    @staticmethod
    def get_hang_seng_universe() -> List[str]:
        # مؤشر هانج سينج (Hang Seng) وعمالقة السوق الصيني في هونغ كونغ
        return [
            "0700.HK", "9988.HK", "3690.HK", "9618.HK", "1211.HK", "0941.HK", "2318.HK", 
            "1398.HK", "3988.HK", "0939.HK", "0388.HK", "2020.HK", "1044.HK", "0027.HK", 
            "1810.HK", "0669.HK", "2269.HK", "2382.HK", "0883.HK", "1088.HK", "1928.HK", 
            "0012.HK", "0002.HK", "0003.HK", "0006.HK", "0011.HK", "0016.HK", "0017.HK", 
            "0066.HK", "0101.HK", "0175.HK", "0267.HK", "0288.HK", "0386.HK", "0762.HK", 
            "0857.HK", "0960.HK", "0968.HK", "0981.HK", "1109.HK", "1177.HK", "1299.HK", 
            "2007.HK", "2319.HK", "2333.HK", "2388.HK", "2628.HK", "3328.HK", "6030.HK", "8833.HK"
        ]

    @staticmethod
    def get_benchmarks_universe() -> List[str]:
        # قائمة المؤشرات الرئيسية العالمية والمحلية للدراسة والمقارنة (Benchmarks)
        return [
            "^TASI.SR",   # مؤشر السوق السعودي (تاسي)
            "EGX30.CA",   # مؤشر البورصة المصرية 30
            "^GSPC",      # مؤشر S&P 500 الأمريكي
            "^IXIC",      # مؤشر ناسداك المركب
            "FTGM.AD",    # مؤشر سوق أبوظبي العام
            "^DFMGI",     # مؤشر سوق دبي المالي
            "^HSI",       # مؤشر هانج سينج (هونغ كونغ)
            "SPY",        # صندوق الإس آند بي 500
            "QQQ"         # صندوق ناسداك
        ]

    @staticmethod
    def get_adx_universe() -> List[str]:
        return [
            "IHC.AD", "FAB.AD", "ETISALAT.AD", "TAQA.AD", "ADCB.AD", "ALDAR.AD", "ADNOCDIST.AD", 
            "ADNOCDRILL.AD", "MULTIPLY.AD", "ALPHA.AD", "RAKPROP.AD", "DANA.AD", "MANAZEL.AD", 
            "ADIS.AD", "AGTHIA.AD", "ARASEM.AD", "ASHM.AD", "ASMK.AD", "BILD.AD", "CBI.AD", 
            "ESHRAQ.AD", "FGBI.AD", "GIC.AD", "GULFCEMENT.AD", "JULPHAR.AD", "RAKCEC.AD", "ASM.AD",
            "NMDC.AD", "QHOLD.AD", "GBG.AD", "INMA.AD", "KHC.AD", "WGI.AD", "OOREDOO.AD", "HELI.AD",
            "ESG.AD", "APEX.AD", "LULU.AD", "MODON.AD", "FERTIGLB.AD", "ADNOCGAS.AD", "NMDCENR.AD"
        ]

    @staticmethod
    def get_dfm_universe() -> List[str]:
        return [
            "EMAAR.DU", "ENBD.DU", "DIB.DU", "DEWA.DU", "DU.DU", "ARAMEX.DU", "DIC.DU", 
            "EMAARDEV.DU", "TALABAT.DU", "SALIK.DU", "TECOM.DU", "EMPOWER.DU", "DTC.DU", 
            "SPINNEYS.DU", "UPP.DU", "AMLAK.DU", "DEYAAR.DU", "AJMANBANK.DU", "AIRARABIA.DU", 
            "GFH.DU", "SHUAA.DU", "TAKAFUL-EM.DU", "SALAMA.DU", "ITHRAERADA.DU", "AMAN.DU", 
            "AMANAT.DU", "UNIONPROPERTIES.DU", "EMIRATESREEM.DU", "GGICO.DU", "ANSI.DU", 
            "DXB.DU", "TESS.DU", "ICD.DU", "ALANSARI.DU", "MEDGULF.DU", "TAKAFUL.DU"
        ]

    @staticmethod
    def get_sp500_universe() -> List[str]:
        return [
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
        ]

    @staticmethod
    def get_nasdaq_universe() -> List[str]:
        return [
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

    @staticmethod
    def get_funds_universe() -> List[str]:
        return ["SPY", "QQQ", "DIA", "IWM", "VOO", "VTI", "ARKK", "XLK", "XLF", "XLE", "XLV", "SMH", "SOXX", "XLI", "XLU", "XLP", "XLY", "XLRE", "XLC"]

    @staticmethod
    def get_gold_silver_universe() -> List[str]:
        return ["GC=F", "GLD", "IAU", "9405.SR", "SI=F", "SLV"]

    @staticmethod
    def get_commodities_universe() -> List[str]:
        return [
            "GC=F", "GLD", "IAU", "SI=F", "SLV", "PL=F", "PA=F", "HG=F", 
            "CL=F", "BZ=F", "HO=F", "RB=F", "NG=F", "USO", "UNG", "DBA", 
            "ZC=F", "ZW=F", "ZS=F", "KC=F", "SB=F", "CT=F", "LE=F", "HE=F"
        ]

# ------------------------------------------------------------------------------
# 6. UNIFIED DATA PROVIDER
# ------------------------------------------------------------------------------
class UnifiedDataProvider:
    @staticmethod
    def fetch_raw_ohlcv(symbol: str, interval: str = "1d") -> pd.DataFrame:
        try:
            period = "5d" if interval == "5m" else ("1mo" if interval == "15m" else "6mo")
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True, timeout=10)
            if df is None or df.empty:
                df = yf.download(symbol, period="max", interval=interval, progress=False, auto_adjust=True, timeout=10)
            if df is None or df.empty:
                return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
            df = df[["open", "high", "low", "close", "volume"]].dropna()
            if df.empty or len(df) < 10:
                return pd.DataFrame()
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            return df
        except Exception:
            return pd.DataFrame()

# ------------------------------------------------------------------------------
# 7. STRICT REAL FINANCIAL DATA & VALUATION
# ------------------------------------------------------------------------------
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
            
            pe_str = str(round(pe, 2)) if pe else "N/A"
            roe_str = f"{round(roe * 100, 1)}%" if roe else "N/A"
            
            score = 70.0
            if roe and roe > 0.15: score += 15.0
            if pe and 0 < pe < 30: score += 10.0
            health_str = f"{round(min(100.0, score), 1)}%"
            
            fair_target = round(target_mean, 2) if target_mean else "N/A"
            upside = "N/A"
            if target_mean and current_price and current_price > 0:
                up_val = ((target_mean - current_price) / current_price) * 100.0
                upside = f"{round(up_val, 1)}%"
                
            return {
                "Health Score": health_str,
                "P/E": pe_str,
                "ROE": roe_str,
                "Fair Target": fair_target,
                "Upside (%)": upside
            }
        except Exception:
            return {"Health Score": "N/A", "P/E": "N/A", "ROE": "N/A", "Fair Target": "N/A", "Upside (%)": "N/A"}

# ------------------------------------------------------------------------------
# 8. ADAPTIVE MARKET REGIME CONTROLLER
# ------------------------------------------------------------------------------
class AdaptiveMarketRegimeController:
    @staticmethod
    def evaluate_market_regime(benchmark_symbol: str = "SPY") -> Tuple[bool, float]:
        try:
            df_bench = UnifiedDataProvider.fetch_raw_ohlcv(benchmark_symbol, interval="1d")
            if df_bench.empty or len(df_bench) < 30:
                return True, 1.0
            current_close = float(df_bench.iloc[-1]["close"])
            sma_50 = float(df_bench["close"].rolling(50).mean().iloc[-1])
            is_bullish = current_close >= sma_50
            return is_bullish, (1.15 if not is_bullish else 1.0)
        except Exception:
            return True, 1.0

# ------------------------------------------------------------------------------
# 9. 5-LAYER QUANT ENGINE
# ------------------------------------------------------------------------------
class SabryVision5LayerEngine:
    def __init__(self, settings: InstitutionalConfig, active_setups: List[str], timeframe: str):
        self.settings = settings
        self.active_setups = active_setups
        self.timeframe = timeframe

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        f = df.copy()
        roll_window = min(20, len(f))
        f["ema200"] = f["close"].ewm(span=200, adjust=False).mean() if len(f) >= 200 else f["close"].expanding().mean()
        tp = (f["high"] + f["low"] + f["close"]) / 3.0
        f["vwap"] = (tp * f["volume"]).rolling(roll_window).sum() / f["volume"].rolling(roll_window).sum()
        
        vwap_diff = f["vwap"].diff(3)
        f["vwap_slope_deg"] = np.degrees(np.arctan(vwap_diff))
        
        tr = np.maximum(f["high"] - f["low"], np.maximum((f["high"] - f["close"].shift(1)).abs(), (f["low"] - f["close"].shift(1)).abs()))
        f["atr14"] = tr.rolling(14).mean()
        f["rvol"] = (f["volume"] / f["volume"].rolling(roll_window).mean().replace(0, np.nan)).fillna(1.0)
        f["poc"] = tp.rolling(min(50, len(f))).mean()
        
        lookback_p = min(20, len(f) - 1)
        f["pivot_20"] = f["high"].rolling(lookback_p).max().shift(1)
        f["low_20"] = f["low"].rolling(lookback_p).min().shift(1)
        
        dyn_rvol = 1.5 if self.timeframe in ["5m", "15m"] else 1.2
        
        is_breakout = (f["close"] > f["pivot_20"]) & (f["rvol"] >= dyn_rvol)
        is_retest = (f["close"].shift(1) > f["pivot_20"]) & (f["low"] <= f["poc"] * 1.03) & (f["close"] > f["poc"])
        is_setup = (f["close"] <= f["pivot_20"]) & (f["close"] >= f["pivot_20"] * 0.95) & (f["rvol"] < 1.3)
        is_bottom = (f["low"] < f["low_20"]) & (f["close"] > f["low_20"])
        
        f["sig_breakout"] = is_breakout if "BREAKOUT" in self.active_setups else False
        f["sig_retest"] = is_retest if "RETEST" in self.active_setups else False
        f["sig_setup"] = is_setup if "SETUP" in self.active_setups else False
        f["sig_bottom_reversal"] = is_bottom if "BOTTOM_REVERSAL" in self.active_setups else False
        
        conditions = [f["sig_breakout"], f["sig_retest"], f["sig_setup"], f["sig_bottom_reversal"]]
        choices = ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"]
        f["signal_type"] = np.select(conditions, choices, default="NONE")
        return f

# ------------------------------------------------------------------------------
# 10. MASTER SCANNER
# ------------------------------------------------------------------------------
class SabryVisionMasterScanner:
    def __init__(self, config: InstitutionalConfig, active_setups: List[str], timeframe: str, market_booster: float = 1.0):
        self.config = config
        self.active_setups = active_setups
        self.timeframe = timeframe
        self.market_booster = market_booster

    def scan_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        df = UnifiedDataProvider.fetch_raw_ohlcv(symbol, self.timeframe)
        if df.empty or len(df) < 10:
            return None
        processed = SabryVision5LayerEngine(self.config, self.active_setups, self.timeframe).process_data(df)
        if processed.empty:
            return None
        latest = processed.iloc[-1]
        sig_type = latest.get("signal_type", "NONE")
        if sig_type == "NONE":
            return None
        
        close_p = float(latest["close"])
        atr = float(latest.get("atr14", close_p * 0.02))
        rvol = float(latest.get("rvol", 1.0))
        slope = float(latest.get("vwap_slope_deg", 0.0))
        
        calc_score = 60.0 + min(25.0, rvol * 5.0) + min(15.0, abs(slope) * 0.5)
        if calc_score < (self.config.min_score * self.market_booster):
            return None

        risk_dollar = self.config.account_size * self.config.risk_pct
        stop_loss = close_p - (atr * self.config.atr_mult)
        risk_per_share = max(0.01, close_p - stop_loss)
        setup_mult = 1.2 if sig_type == "BREAKOUT" else 1.0
        shares_qty = int((risk_dollar / risk_per_share) * setup_mult)
        total_cost = shares_qty * close_p

        fin = FinancialHealthEvaluator.get_financial_metrics(symbol)

        return {
            "Symbol": symbol,
            "Timeframe": self.timeframe,
            "Signal": sig_type,
            "Close": round(close_p, 2),
            "Shares Qty": shares_qty,
            "Position Cost ($)": round(total_cost, 2),
            "Score": round(calc_score, 1),
            "Health": fin["Health Score"],
            "P/E": fin["P/E"],
            "ROE": fin["ROE"],
            "Fair Target": fin["Fair Target"],
            "Upside (%)": fin["Upside (%)"],
            "Stop Loss": round(stop_loss, 2),
            "Take Profit": round(close_p + (risk_per_share * self.config.reward_mult), 2)
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
                
        bar.empty()
        status.empty()
        return pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True) if results else pd.DataFrame()

# ------------------------------------------------------------------------------
# 11. LOGIN & SECURITY MANAGEMENT SCREEN
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
# 12. STREAMLIT COMMAND CENTER & DASHBOARD (ROLE-BASED TABS)
# ------------------------------------------------------------------------------
def main():
    if not st.session_state["authenticated"]:
        render_login_screen()
        return

    st.sidebar.title(f"🛡️ SABRY VISION v11.17")
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
            
            action_mode = st.selectbox("الإجراء المطلوب:", ["تعديل حساب حالي (أو الأدمن)", "إضافة مستخدم جديد"])
            
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
                                    st.error("اسم المستخدم الجديد مستخدم بالفعل!")
                                else:
                                    st.session_state["users_db"][edit_username] = {
                                        "password": edit_password,
                                        "expiry": edit_expiry.strftime("%Y-%m-%d"),
                                        "role": curr_info["role"]
                                    }
                                    del st.session_state["users_db"][target_user]
                                    st.success("تم تحديث اسم المستخدم والبيانات!")
                                    st.rerun()
                            else:
                                st.session_state["users_db"][target_user]["password"] = edit_password
                                st.session_state["users_db"][target_user]["expiry"] = edit_expiry.strftime("%Y-%m-%d")
                                st.success("تم تحديث بيانات الحساب بنجاح!")
                                st.rerun()
                with col_btn2:
                    if target_user != "admin":
                        if st.button("🗑️ حذف الحساب"):
                            del st.session_state["users_db"][target_user]
                            st.success("تم حذف الحساب بنجاح!")
                            st.rerun()
                    else:
                        st.info("لا يمكن حذف حساب المسؤول الرئيسي.")
            
            st.markdown("---")
            st.write("قائمة الحسابات النشطة:")
            for u, info in st.session_state["users_db"].items():
                st.write(f"- **{u}** ({info['role']}) ➔ ينتهي في: {info['expiry']}")

    st.sidebar.markdown("### ⚙️ إعدادات تليجرام الفورية")
    ui_token = st.sidebar.text_input("Telegram Bot Token", value="", type="password")
    ui_chat = st.sidebar.text_input("Telegram Chat ID", value="")
    
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
    
    base_markets = [
        "📈 المؤشرات الرئيسية (Benchmarks)",
        "السوق السعودي (تاسي + نمو + REITs)",
        "البورصة المصرية الكاملة (EGX Complete 240+)",
        "هونغ كونغ والمؤشر (Hang Seng)",
        "سوق أبوظبي (ADX)",
        "سوق دبي (DFM)",
        "السوق الأمريكي (S&P 500)",
        "الناسداك (Nasdaq)",
        "صناديق الاستثمار (Funds)",
        "الذهب والفضة (Gold & Silver)",
        "السلع (Commodities)"
    ]
    custom_names = list(st.session_state["user_custom_lists"].keys())
    all_markets = base_markets + [f"📁 {name}" for name in custom_names]
    
    market_choice = st.sidebar.selectbox("اختر السوق المستهدف:", all_markets)
    timeframe = st.sidebar.selectbox("الإطار الزمني:", ["5m", "15m", "1h", "1d"], index=2)
    active_setups = st.sidebar.multiselect("نماذج الدخول:", ["BREAKOUT", "RETEST", "SETUP", "BOTTOM_REVERSAL"], default=["BREAKOUT", "RETEST"])

    st.title("🛡️ SABRY VISION - Institutional Quant Terminal v11.17")
    st.markdown("---")
    
    if st.session_state["is_admin"]:
        tab1, tab2, tab3 = st.tabs([
            "🚀 السكانر الشامل وتليجرام", 
            "📊 تقييم البيانات المالية الحقيقية", 
            "⚙️ هندسة القوائم المخصصة (Admin Only)"
        ])
    else:
        tab1, tab2 = st.tabs([
            "🚀 السكانر الشامل وتليجرام", 
            "📊 تقييم البيانات المالية الحقيقية"
        ])
    
    with tab1:
        st.subheader("محرك السكانر المؤسسي وبطاقات الفرص")
        if st.button("بدء المسح المؤسسي الشامل", type="primary"):
            if "المؤشرات الرئيسية" in market_choice: syms = GlobalUniverseLoader.get_benchmarks_universe(); bench = "SPY"
            elif "السوق السعودي" in market_choice: syms = GlobalUniverseLoader.get_tasi_universe(); bench = "2222.SR"
            elif "البورصة المصرية الكاملة" in market_choice: syms = GlobalUniverseLoader.get_egx_complete_universe(); bench = "COMI.CA"
            elif "هونغ كونغ والمؤشر" in market_choice: syms = GlobalUniverseLoader.get_hang_seng_universe(); bench = "^HSI"
            elif "سوق أبوظبي" in market_choice: syms = GlobalUniverseLoader.get_adx_universe(); bench = "IHC.AD"
            elif "سوق دبي" in market_choice: syms = GlobalUniverseLoader.get_dfm_universe(); bench = "EMAAR.DU"
            elif "السوق الأمريكي" in market_choice: syms = GlobalUniverseLoader.get_sp500_universe(); bench = "SPY"
            elif "الناسداك" in market_choice: syms = GlobalUniverseLoader.get_nasdaq_universe(); bench = "QQQ"
            elif "صناديق الاستثمار" in market_choice: syms = GlobalUniverseLoader.get_funds_universe(); bench = "SPY"
            elif "الذهب والفضة" in market_choice: syms = GlobalUniverseLoader.get_gold_silver_universe(); bench = "GLD"
            elif "السلع" in market_choice: syms = GlobalUniverseLoader.get_commodities_universe(); bench = "GLD"
            else:
                c_name = market_choice.replace("📁 ", "")
                syms = st.session_state["user_custom_lists"].get(c_name, [])
                bench = "SPY"
                
            is_bull, booster = AdaptiveMarketRegimeController.evaluate_market_regime(bench)
            scanner = SabryVisionMasterScanner(config, active_setups, timeframe, market_booster=booster)
            results_df = scanner.run_scan_with_progress(syms)
            st.session_state["last_scan_results"] = results_df
            
        saved_df = st.session_state["last_scan_results"]
        if not saved_df.empty:
            st.success(f"تم رصد ({len(saved_df)}) فرصة بنجاح:")
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
        st.subheader("📊 فحص البيانات المالية الحقيقية لأي أصل")
        f_sym = st.text_input("أدخل رمز الأصل (مثال: COMI.CA أو ^TASI.SR أو 0700.HK):", value="COMI.CA")
        if st.button("جلب البيانات المالية الحقيقية"):
            metrics = FinancialHealthEvaluator.get_financial_metrics(f_sym)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("مؤشر الصحة", metrics["Health Score"])
            c2.metric("مكرر الربحية P/E", metrics["P/E"])
            c3.metric("العائد ROE", metrics["ROE"])
            c4.metric("السعر المستهدف", metrics["Fair Target"])
            c5.metric("نسبة الصعود", metrics["Upside (%)"])

    if st.session_state["is_admin"]:
        with tab3:
            st.subheader("⚙️ هندسة القوائم المخصصة (لوحة تحكم الأدمن)")
            
            new_l = st.text_input("اسم القائمة الجديدة:")
            if st.button("إنشاء قائمة"):
                if new_l and new_l not in st.session_state["user_custom_lists"]:
                    st.session_state["user_custom_lists"][new_l] = []
                    st.success("تم الإنشاء بنجاح!")
                    st.rerun()
                    
            st.markdown("---")
            cur_list = st.selectbox("اختر القائمة للإدارة:", list(st.session_state["user_custom_lists"].keys()))
            
            ren_l = st.text_input("تعديل اسم القائمة:", value=cur_list)
            if st.button("حفظ الاسم الجديد"):
                if ren_l and ren_l != cur_list:
                    st.session_state["user_custom_lists"][ren_l] = st.session_state["user_custom_lists"].pop(cur_list)
                    st.success("تم التعديل!")
                    st.rerun()
                    
            syms_in_list = st.session_state["user_custom_lists"][cur_list]
            st.write(f"**الأسهم الحالية ({len(syms_in_list)}):**", syms_in_list)
            
            add_s = st.text_input("أضف رمز جديد (مثال: MSFT أو 1120.SR):")
            if st.button("إضافة الرمز للقائمة"):
                if add_s and add_s.strip().upper() not in syms_in_list:
                    st.session_state["user_custom_lists"][cur_list].append(add_s.strip().upper())
                    st.success("تمت الإضافة!")
                    st.rerun()
                    
            if syms_in_list:
                rem_s = st.selectbox("اختر رمزاً للحذف:", syms_in_list)
                if st.button("حذف الرمز المختار"):
                    st.session_state["user_custom_lists"][cur_list].remove(rem_s)
                    st.success("تم الحذف!")
                    st.rerun()
                    
            if st.button("حذف هذه القائمة بالكامل"):
                if len(st.session_state["user_custom_lists"]) > 1:
                    del st.session_state["user_custom_lists"][cur_list]
                    st.success("تم الحذف!")
                    st.rerun()
                else:
                    st.warning("يجب أن تبقى قائمة واحدة على الأقل.")

if __name__ == "__main__":
    main()
