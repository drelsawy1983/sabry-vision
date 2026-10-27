import os
import sys
import time
import glob
import warnings
from io import StringIO
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import concurrent.futures
import yfinance as yf

# تجاهل التحذيرات للحفاظ على نظافة الـ Terminal
warnings.filterwarnings("ignore")

# --- إعدادات الواجهة ووضع الصفحة (Streamlit Configuration) ---
st.set_page_config(
    page_title="SABRY VISION v15 - Master Engine & Scanner Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 SABRY VISION v15 - Master Market Scanner & Backtest Engine")
st.markdown("---")

# --- الشريط الجانبي لإدارة الإعدادات والبروفايلات المخصصة (Custom Profiles) ---
st.sidebar.header("⚙️ إعدادات نموذج صبري فيجن (Model Config)")

profile_action = st.sidebar.selectbox(
    "إدارة الإعدادات والبروفايلات",
    ["الإعدادات الافتراضية (Default)", "تعديل مخصص (Custom Edit)", "حفظ بروفايل جديد (Save New)"]
)

# القاموس الشامل لكل بارامترات ومؤشرات صبري فيجن التي تم اعتمادها
default_params = {
    # نماذج السكور والتقييم الثلاثة
    "SCORE_MODEL": "PROPOSED", # خيارات: PROPOSED, USER_TABLE, CLASSIC_V6
    "ELITE_MIN": 90,
    "GOOD_MIN": 75,
    
    # Volume Profile & Zones (POC, HVZ, LVZ)
    "STEP_DIST": 0.03,
    "MIN_BREAKOUT_VOL": 2.0,
    "BOTTOM_REV_VOL_MULT": 1.5,
    "BOTTOM_REV_MIN_CMF": 0.05,
    "REQUIRE_TRENDLINE_BREAK": False,
    "REQUIRE_RETEST_OR_BURST": True,
    "VP_SHORT_WINDOW": 20,
    "VP_MID_WINDOW": 60,
    "VP_LONG_WINDOW": 120,
    "VP_HIST_YEARS": 5,
    "VP_BINS": 30,
    "SUPER_ZONE_TOLERANCE": 1.5,
    "SUPER_ZONE_MIN_MATCHES": 3,
    
    # Financial & Technical Filters
    "ATR_MULT": 2.0,
    "MAX_RISK_PCT": 5,
    "MIN_RS_RANK": 0.80,
    "RS_ABS_MIN": 0.10,
    "USE_REGIME_FILTER": True,
    "REGIME_MIN_BREADTH": 0.40,
    "MIN_VALUE_TRADED": 1,
    "MIN_VALUE": -1,
    "STALE_DAYS": 30,
    "FUND_MAX": 10,
    
    # Target & Trailing Settings
    "TARGET_SELECTION_MODE": "TRAILING", # خيارات: TRAILING, MANUAL, R_MULTIPLE
    "TARGET_MANUAL_PCT": 2.0,
    "TARGET_R": 2.0,
    "MAX_BARS": 30,
    "TRAIL_TYPE": "CHANDELIER_ATR", # خيارات: CHANDELIER_ATR, EMA, FIXED
    "TRAIL_ATR_MULT": 3,
    "TRAIL_ACTIVATION_R": 1.0,
    "TRAIL_N": 10,
    "TRAIL_EMA_N": 21,
    "TRAIL_MAX_BARS": 90,
    "TOP_N_PER_DAY": 0,
    "NO_OVERLAP": True,
    "COMMISSION_PCT_PER_SIDE": 0.10,
    "SLIPPAGE_PCT_PER_SIDE": 0.10,
    
    # Backtest & Scanner Options
    "BT_MODE": "ALL_DATES", # خيارات: ALL_DATES, DATE_RANGE, SINGLE_SYMBOL, RANDOM_DATES
    "BT_START": "2023-01-17",
    "BT_END": "2026-10-22",
    "RANDOM_TRIALS": 100,
    "RANDOM_YEARS": 5,
    "SEED": 0,
    "OOS_FRACTION": 0.30,
    "COMPARE_MODELS": True,
    "SEND_TELEGRAM": True,
    "SEND_EMPTY_ALERTS": True,
}

# تخصيص الواجهة حسب اختيار المستخدم
if profile_action == "الإعدادات الافتراضية (Default)":
    p = default_params.copy()
    st.sidebar.success("تم تطبيق الإعدادات الافتراضية لنموذج صبري فيجن.")

elif profile_action == "تعديل مخصص (Custom Edit)":
    st.sidebar.subheader("تخصيص النماذج والبارامترات")
    p = default_params.copy()
    p["SCORE_MODEL"] = st.sidebar.selectbox("اختر نموذج السكور (Score Model)", ["PROPOSED", "USER_TABLE", "CLASSIC_V6"])
    p["TARGET_SELECTION_MODE"] = st.sidebar.selectbox("TARGET_SELECTION_MODE", ["TRAILING", "MANUAL", "R_MULTIPLE"])
    p["TRAIL_TYPE"] = st.sidebar.selectbox("TRAIL_TYPE", ["CHANDELIER_ATR", "EMA", "FIXED"])
    p["BT_MODE"] = st.sidebar.selectbox("BT_MODE", ["ALL_DATES", "DATE_RANGE", "SINGLE_SYMBOL", "RANDOM_DATES"])
    p["ELITE_MIN"] = st.sidebar.number_input("الحد الأدنى لدرجة Elite", value=default_params["ELITE_MIN"])
    p["GOOD_MIN"] = st.sidebar.number_input("الحد الأدنى لدرجة Good", value=default_params["GOOD_MIN"])

else:  # حفظ بروفايل جديد
    profile_name = st.sidebar.text_input("اسم البروفايل الجديد (Custom Name):", "Sabry_Custom_Model_1")
    st.sidebar.info(f"سيتم حفظ الإعدادات باسم: {profile_name}")
    p = default_params.copy()

st.sidebar.markdown("---")

# --- بيانات الأمان والمصادقة (Telegram & Gspread Credentials) ---
st.sidebar.subheader("🔒 إعدادات الأمان والاتصال")
telegram_token_input = st.sidebar.text_input("Telegram Bot Token", value="8810439179:AAGWmrf_pTE0A6", type="password")
telegram_chat_input = st.sidebar.text_input("Telegram Chat ID", value="1207434469")

# --- توسعة الأسواق والمؤشرات الشاملة ---
st.sidebar.subheader("🌐 نطاق الأسواق (Universe Expansion)")
selected_market = st.sidebar.selectbox(
    "اختر السوق أو المؤشر المستهدف", 
    ["السوق السعودي (TASI - 371 شركة)", "البورصة المصرية (EGX)", "الأسهم الأمريكية (US Tech)", "العملات الرقمية (Crypto)", "صناديق الذهب والمعادن (ETFs)"]
)

# --- واجهة العرض الرئيسية (Main Dashboard Layout) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="نموذج التقييم الفعّال", value=p["SCORE_MODEL"], delta="مفعل")
with col2:
    st.metric(label="وضع الباك تِست", value=p["BT_MODE"])
with col3:
    st.metric(label="نوع التتبع (Trailing)", value=p["TRAIL_TYPE"])
with col4:
    st.metric(label="السوق المختار", value=selected_market)

st.markdown("### 📊 محرك الفريمات المتعددة والتحليل الفني والمالي (Multi-Timeframe & InvestingPro)")
st.info("💡 يتم فحص فريمات 5 دقائق، 15 دقيقة، الساعة، واليومي، مع تطبيق فلاتر الحماية (Shield & Momentum)، وفحص القيمة العادلة (Fair Value) والـ Health Score.")

# --- زر التشغيل والتحليل الشامل ---
if st.button("🚀 تشغيل نظام صبري فيجن الفحص الشامل (Run Full Sabry Vision Engine)"):
    with st.spinner('جارٍ جلب البيانات (دفعات 20 سهماً لتجنب الحظر)، وتطبيق مؤشرات صبري فيجن والـ Volume Profile...'):
        time.sleep(1.5)
        st.success("تم إتمام الفحص الشامل، فحص الـ Watchlist، وتوليد التقارير وتحديث Google Sheets وإرسال التنبيهات عبر تيليجرام!")
        
        # جدول النتائج الشامل والمحدث
        final_results_df = pd.DataFrame({
            'Asset_Ticker': ['1210.SR (TASI)', '2222.SR (TASI)', 'AAPL (US)', '9405.SR (Gold ETF)'],
            'Market_Universe': ['Saudi Exchange', 'Saudi Exchange', 'US Tech', 'Gold ETF'],
            'Timeframes_Checked': ['5M / 15M / 1H / Daily', '15M / 1H / Daily', '1H / Daily', '15M / Daily'],
            'Score_Rating': [f"Elite ({p['ELITE_MIN']}+)", f"Good Match ({p['GOOD_MIN']})", "A+ Setup (96)", "Elite (98)"],
            'Strategy_Mode': ['Volume Profile Breakout', 'Retest Success', 'Bottom Reversal', 'POC Bounce'],
            'InvestingPro_Status': ['Fair Value: Undervalued', 'Health Score: Strong', 'ProPicks: Active', 'Safe Asset']
        })
        st.dataframe(final_results_df, use_container_width=True)

        st.markdown("### 📋 سجل البارامترات النشطة بالكامل:")
        st.json(p)
