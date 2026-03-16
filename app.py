import streamlit as st
import pandas as pd
import os
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# CEO প্যানেলে অনুমোদন দিলে নিচের এই লাইনটি যোগ করুন
if st.button(f"অনুমোদন দিন (ID {row['ID']})"):
    df.at[idx, 'Status'] = "Approved"
    save_data(df)
    st.balloons() # এই এনিমেশনটি যোগ করুন
    st.success("কাজটি অনুমোদিত হয়েছে! 🎊")
    st.rerun()
from datetime import datetime

# ১. ফাইল পাথ ও ডাটা ম্যানেজমেন্ট
DB_FILE = "requisition_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

def save_data(data_df):
    data_df.to_csv(DB_FILE, index=False)

# ২. পেজ সেটআপ
st.set_page_config(page_title="Supply Chain Automation", layout="wide")
st.title("🏗️ জারা কনস্ট্রাকশন সাপ্লাই চেইন অটোমেশন")

df = load_data()

# ৩. ইউজার রোল ও পাসওয়ার্ড সেটআপ
USERS = {
    "admin": {"pw": "admin786", "role": "CEO"},
    "pe_rakib": {"pw": "pe123", "role": "Project Engineer"},
    "site_shuvo": {"pw": "site456", "role": "Site Engineer"},
    "enam": {"pw": "enam123", "role": "Site Engineer"},
    "pur_korim": {"pw": "pur789", "role": "Purchase Dept"},
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৪. লগইন লজিক
if not st.session_state.logged_in:
    with st.form("login_panel"):
        st.subheader("🔐 লগইন করুন")
        u_id = st.text_input("ইউজার আইডি")
        u_pw = st.text_input("পাসওয়ার্ড", type="password")
        if st.form_submit_button("Login"):
            if u_id in USERS and USERS[u_id]['pw'] == u_pw:
                st.session_state.logged_in = True
                st.session_state.user = u_id
                st.session_state.role = USERS[u_id]['role']
                st.rerun()
            else:
                st.error("ভুল ইউজার আইডি বা পাসওয়ার্ড!")
else:
    user_role = st.session_state.role
    st.sidebar.success(f"লগইন: {st.session_state.user} ({user_role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ৫. রোল ভিত্তিক ইন্টারফেস লজিক ---

    # ক. সাইট ইঞ্জিনিয়ার প্যানেল
    if user_role == "Site Engineer":
        st.header("📋 নতুন রিকুইজিশন তৈরি")
        with st.form("req_form"):
            item = st.text_input("মালামালের নাম")
            qty = st.number_input("পরিমাণ", min_value=1)
            unit = st.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস"])
            site = st.text_input("সাইট লোকেশন")
            if st.form_submit_button("সাবমিট"):
                new_row = {
                    "ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, 
                    "Site": site, "Status": "Pending (PE Approval)", 
                    "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), 
                    "AddedBy": st.session_state.user
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success("রিকুইজিশন পাঠানো হয়েছে!"); st.rerun()

    # খ. প্রজেক্ট ইঞ্জিনিয়ার (PE) প্যানেল
    elif user_role == "Project Engineer":
        st.header("⚖️ PE অনুমোদন প্যানেল")
        pending_pe = df[df['Status'] == "Pending (PE Approval)"]
        if not pending_pe.empty:
            for idx, row in pending_pe.iterrows():
                with st.expander(f"ID: {row['ID']} - {row['Item']} ({row['Site']})"):
                    if st.button(f"Approve ID {row['ID']}", key=f"pe_{idx}"):
                        df.at[idx, 'Status'] = "Sent to Purchase"
                        save_data(df); st.rerun()
        else: st.info("কোনো পেন্ডিং রিকুইজিশন নেই।")

    # গ. পারচেজ ডিপার্টমেন্ট প্যানেল
    elif user_role == "Purchase Dept":
        st.header("💰 বাজার দর (Rate) এন্ট্রি")
        pending_pur = df[df['Status'] == "Sent to Purchase"]
        if not pending_pur.empty:
            for idx, row in pending_pur.iterrows():
                with st.expander(f"ID: {row['ID']} - {row['Item']}"):
                    rate = st.number_input(f"Rate for ID {row['ID']}", min_value=1.0, key=f"r_{idx}")
                    if st.button("Confirm Rate", key=f"btn_{idx}"):
                        df.at[idx, 'Rate'] = rate
                        df.at[idx, 'Status'] = "Waiting for CEO Permission"
                        save_data(df); st.rerun()
        else: st.info("কোনো কাজ পেন্ডিং নেই।")

    # ঘ. CEO প্যানেল
    elif user_role == "CEO":
        st.header("💎 চূড়ান্ত অনুমোদন (CEO)")
        pending_ceo = df[df['Status'] == "Waiting for CEO Permission"]
        if not pending_ceo.empty:
            for idx, row in pending_ceo.iterrows():
                total = row['Qty'] * row['Rate']
                st.warning(f"ID {row['ID']}: {row['Item']} - {row['Qty']} {row['Unit']} | মোট খরচ: {total} TK")
                if st.button(f"চূড়ান্ত অনুমোদন দিন (ID {row['ID']})"):
                    df.at[idx, 'Status'] = "✅ Approved & Delivery in Progress"
                    save_data(df); st.rerun()
        else: st.info("অনুমোদনের জন্য কোনো ফাইল নেই।")

    # --- ৬. রিপোর্ট ও ড্যাশবোর্ড ---
    st.divider()
    st.subheader("📊 অল রিকুইজিশন বোর্ড")
    st.dataframe(df, use_container_width=True)
    
    # রিপোর্ট ডাউনলোড বাটন
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 ডাউনলোড রিপোর্ট (Excel)", data=csv, file_name="supply_chain_report.csv", mime="text/csv")
