import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
from datetime import datetime

# ১. পেজ সেটিংস
st.set_page_config(page_title="Supply Chain Pro", layout="wide")
st.title("🏗️ কনস্ট্রাকশন সাপ্লাই চেইন অটোমেশন")

# ২. গুগল শীট কানেকশন (সঠিক পদ্ধতি)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ilP26HZxJ6PviYS_dvR9S4qyr62mIttO_32QUO6O2Ro/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# ৩. ডাটা লোড করা
try:
    df = conn.read(spreadsheet=SHEET_URL)
except Exception as e:
    st.error("গুগল শীট থেকে ডাটা লোড করা যাচ্ছে না।")
    df = pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

# ৪. ইউজার লিস্ট
USERS = {"admin": "admin786", "site_shuvo": "site456"}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    u_id = st.text_input("User ID")
    u_pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_id in USERS and USERS[u_id] == u_pw:
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("ভুল পাসওয়ার্ড!")
else:
    st.header("📋 নতুন রিকুইজিশন")
    with st.form("req"):
        item = st.text_input("মালামাল")
        qty = st.number_input("পরিমাণ", min_value=1)
        if st.form_submit_button("সাবমিট"):
            new_row = pd.DataFrame([{"ID": len(df)+1, "Item": item, "Qty": qty, "Status": "Pending", "Date": datetime.now().strftime("%d/%m/%Y")}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success("সেভ হয়েছে!")
            st.rerun()
    
    st.divider()
    st.dataframe(df)
