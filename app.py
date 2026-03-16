import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ১. ফাইল পাথ ও ডাটা লোড
DB_FILE = "requisition_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

def save_data(data_df):
    data_df.to_csv(DB_FILE, index=False)

# ২. পেজ সেটআপ
st.set_page_config(page_title="Supply Chain Pro", layout="wide")
st.title("🏗️ কনস্ট্রাকশন সাপ্লাই চেইন অটোমেশন")

df = load_data()

# ৩. ইউজার ডাটাবেস
USERS = {
    "admin": {"pw": "admin786", "role": "CEO"},
    "pe_rakib": {"pw": "pe123", "role": "Project Engineer"},
    "site_shuvo": {"pw": "site456", "role": "Site Engineer"},
    "pur_korim": {"pw": "pur789", "role": "Purchase Dept"},
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৪. লগইন লজিক
if not st.session_state.logged_in:
    with st.form("login"):
        u = st.text_input("User ID")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u in USERS and USERS[u]['pw'] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.session_state.role = USERS[u]['role']
                st.rerun()
            else: st.error("ভুল আইডি বা পাসওয়ার্ড!")
else:
    role = st.session_state.role
    st.sidebar.success(f"ইউজার: {st.session_state.user} ({role})")
    
    # --- ৫. রোল ভিত্তিক ইন্টারফেস ---
    
    # ক. সাইট ইঞ্জিনিয়ার: মালামাল এন্ট্রি করবে
    if role == "Site Engineer":
        st.header("📋 নতুন রিকুইজিশন পাঠান")
        with st.form("req"):
            item = st.text_input("মালামালের নাম")
            qty = st.number_input("পরিমাণ", min_value=1)
            unit = st.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস"])
            site = st.text_input("সাইট")
            if st.form_submit_button("সাবমিট"):
                new_row = {"ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, "Site": site, "Status": "Pending", "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), "AddedBy": st.session_state.user}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success("সেভ হয়েছে!"); st.rerun()

    # খ. পারচেজ ডিপার্টমেন্ট: রেট বসাবে
    elif role == "Purchase Dept":
        st.header("💰 মালামালের রেট আপডেট করুন")
        pending = df[df['Status'] == "Pending"]
        for idx, row in pending.iterrows():
            with st.expander(f"ID: {row['ID']} - {row['Item']}"):
                rate = st.number_input("রেট (টাকা)", key=f"r_{idx}")
                if st.button("রেট কনফার্ম করুন", key=f"b_{idx}"):
                    df.at[idx, 'Rate'] = rate
                    df.at[idx, 'Status'] = "Rate Added (Waiting for CEO)"
                    save_data(df)
                    st.rerun()

    # গ. CEO: চূড়ান্ত অনুমোদন দেবেন
    elif role == "CEO":
        st.header("⚖️ চূড়ান্ত অনুমোদন (Approval)")
        to_approve = df[df['Status'] == "Rate Added (Waiting for CEO)"]
        for idx, row in to_approve.iterrows():
            st.info(f"মালামাল: {row['Item']} | পরিমাণ: {row['Qty']} | মোট দাম: {row['Qty']*row['Rate']} টাকা")
            if st.button(f"Approve ID: {row['ID']}"):
                df.at[idx, 'Status'] = "Approved & Ready for Delivery"
                save_data(df)
                st.rerun()

    # ৬. ডাটা টেবিল (সবার জন্য)
    st.divider()
    st.subheader("📊 সাপ্লাই চেইন ট্র্যাকিং বোর্ড")
    st.dataframe(df, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
# ডাটা টেবিলের ঠিক উপরে এই অংশটুকু যোগ করুন
st.divider()
st.subheader("📊 সামারি রিপোর্ট")

col1, col2, col3 = st.columns(3)
col1.metric("মোট রিকুইজিশন", len(df))
col2.metric("পেন্ডিং", len(df[df['Status'] == 'Pending']))
col3.metric("মোট খরচ", f"{df['Rate'].sum() * df['Qty'].sum()} TK") # এটি একটি সাধারণ হিসাব

# এক্সেল ডাউনলোড বাটন
st.download_button(
    label="📥 ডাউনলোড এক্সেল রিপোর্ট",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name=f'requisition_report_{datetime.now().strftime("%d-%m-%y")}.csv',
    mime='text/csv',
)
