import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ১. ফাইল পাথ সেটআপ (এখানেই সব ডাটা জমা হবে)
DB_FILE = "requisition_data.csv"

# ২. ডাটা লোড করার ফাংশন
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # ফাইল না থাকলে নতুন কলাম তৈরি করবে
        return pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Date", "AddedBy"])

# ৩. ডাটা সেভ করার ফাংশন
def save_data(data_df):
    data_df.to_csv(DB_FILE, index=False)

# ৪. অ্যাপ ইন্টারফেস
st.set_page_config(page_title="Supply Chain Pro", layout="wide")
st.title("🏗️ কনস্ট্রাকশন সাপ্লাই চেইন (Offline/Local Version)")

df = load_data()

# ৫. সিম্পল লগইন
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    u = st.text_input("User ID")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "Linkon" and p == "1234":
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("ভুল আইডি বা পাসওয়ার্ড!")
else:
    st.sidebar.success(f"ইউজার: {st.session_state.user}")
    
    # ৬. নতুন ডাটা এন্ট্রি
    st.header("📋 নতুন রিকুইজিশন পাঠান")
    with st.form("req_form"):
        item = st.text_input("মালামালের নাম")
        qty = st.number_input("পরিমাণ", min_value=1)
        unit = st.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস"])
        site = st.text_input("সাইট লোকেশন")
        
        if st.form_submit_button("সাবমিট করুন"):
            new_row = {
                "ID": len(df) + 1,
                "Item": item,
                "Qty": qty,
                "Unit": unit,
                "Site": site,
                "Status": "Pending",
                "Date": datetime.now().strftime("%d/%m/%Y"),
                "AddedBy": st.session_state.user
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("ডাটা লোকাল ফাইলে সেভ হয়েছে!")
            st.rerun()

    st.divider()
    st.subheader("📊 অল ট্র্যাকিং বোর্ড")
    st.dataframe(df, use_container_width=True)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
