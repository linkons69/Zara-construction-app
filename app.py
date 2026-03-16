import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
from datetime import datetime

# ১. পেজ সেটিংস
st.set_page_config(page_title="Supply Chain Pro", layout="wide")
st.title("🏗️ কনস্ট্রাকশন সাপ্লাই চেইন অটোমেশন")

# ২. গুগল শীট কানেকশন স্থাপন (এটি সবার উপরে থাকতে হবে)
# এখানে আমরা conn অবজেক্টটি গ্লোবালি ডিফাইন করছি
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ilP26HZxJ6PviYS_dvR9S4qyr62mIttO_32QUO6O2Ro/edit?usp=sharing"

# ৩. ডাটা লোড করা
try:
    df = conn.read(spreadsheet=SHEET_URL)
except Exception as e:
    st.error(f"ডাটা লোড করা যাচ্ছে না: {e}")
    df = pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

# ৪. লগইন চেক
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login"):
        u = st.text_input("User ID")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == "site_shuvo" and p == "site456":
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("ভুল পাসওয়ার্ড!")
else:
    # ৫. ডাটা এন্ট্রি ফর্ম (এখানেই আপনার আগের এররটি আসছিল)
    st.header("📋 নতুন রিকুইজিশন পাঠান")
    with st.form("req_form"):
        item = st.text_input("মালামালের নাম")
        qty = st.number_input("পরিমাণ", min_value=1)
        if st.form_submit_button("সাবমিট করুন"):
            # নতুন ডাটা তৈরি
            new_row = pd.DataFrame([{
                "ID": len(df)+1, "Item": item, "Qty": qty, 
                "Status": "Pending", "Date": datetime.now().strftime("%d/%m/%Y"),
                "AddedBy": st.session_state.user
            }])
            # ডাটা আপডেট
            updated_df = pd.concat([df, new_row], ignore_index=True)
            # আপডেটটি গুগল শীটে পাঠানো
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success("সফলভাবে সেভ হয়েছে!")
            st.rerun()

    st.divider()
    st.dataframe(df)
