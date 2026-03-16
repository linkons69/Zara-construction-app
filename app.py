import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ১. পেজ সেটআপ এবং স্টাইল
st.set_page_config(page_title="ZARA Supply Chain", layout="wide", page_icon="🏗️")

# Custom CSS ফর বেটার লুক
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    div[data-testid="stExpander"] {
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ২. ডাটা ম্যানেজমেন্ট
DB_FILE = "requisition_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

def save_data(data_df):
    data_df.to_csv(DB_FILE, index=False)

st.title("🏗️ জারা কনস্ট্রাকশন সাপ্লাই চেইন")

df = load_data()

# ৩. ইউজার ডাটাবেস
USERS = {
    "admin": {"pw": "admin123", "role": "CEO"},
    "Linkon": {"pw": "linkon123", "role": "Project Engineer"},
    "site_shuvo": {"pw": "site456", "role": "Site Engineer"},
    "enam": {"pw": "enam123", "role": "Site Engineer"},
    "Rovi": {"pw": "rovi123", "role": "Purchase Dept"},
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৪. লগইন লজিক
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_panel"):
            st.markdown("<h2 style='text-align: center;'>🔐 মেম্বার লগইন</h2>", unsafe_allow_html=True)
            u_id = st.text_input("ইউজার আইডি")
            u_pw = st.text_input("পাসওয়ার্ড", type="password")
            if st.form_submit_button("লগইন করুন"):
                if u_id in USERS and USERS[u_id]['pw'] == u_pw:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.session_state.role = USERS[u_id]['role']
                    st.rerun()
                else:
                    st.error("ভুল ইউজার আইডি বা পাসওয়ার্ড!")
else:
    user_role = st.session_state.role
    st.sidebar.markdown(f"### 👤 স্বাগতম, {st.session_state.user}")
    st.sidebar.info(f"পদবী: {user_role}")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ৫. সামারি মেট্রিক্স (সবার জন্য) ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("মোট রিকুইজিশন", len(df))
    m2.metric("পেন্ডিং (PE)", len(df[df['Status'] == "Pending (PE Approval)"]))
    m3.metric("পেন্ডিং (CEO)", len(df[df['Status'] == "Waiting for CEO Permission"]))
    total_cost = (df['Rate'] * df['Qty']).sum()
    m4.metric("মোট বাজেট (TK)", f"{int(total_cost):,}")

    st.divider()

    # --- ৬. রোল ভিত্তিক ইন্টারফেস ---

    # ক. সাইট ইঞ্জিনিয়ার
    if user_role == "Site Engineer":
        st.subheader("📋 নতুন মালামালের রিকুইজিশন")
        with st.form("req_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            item = c1.text_input("মালামালের নাম (যেমন: সিমেন্ট)")
            qty = c1.number_input("পরিমাণ", min_value=1)
            unit = c2.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস", "গাড়ি"])
            site = c2.text_input("সাইট লোকেশন")
            if st.form_submit_button("সাবমিট করুন"):
                new_row = {
                    "ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, 
                    "Site": site, "Status": "Pending (PE Approval)", 
                    "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), 
                    "AddedBy": st.session_state.user
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success("✅ রিকুইজিশন সফলভাবে পাঠানো হয়েছে!")
                st.balloons()
                st.rerun()

    # খ. প্রজেক্ট ইঞ্জিনিয়ার (PE)
    elif user_role == "Project Engineer":
        st.subheader("⚖️ PE অনুমোদন প্যানেল")
        pending_pe = df[df['Status'] == "Pending (PE Approval)"]
        if not pending_pe.empty:
            for idx, row in pending_pe.iterrows():
                with st.expander(f"📦 ID: {row['ID']} - {row['Item']} ({row['Site']})"):
                    st.write(f"পরিমাণ: {row['Qty']} {row['Unit']} | তারিখ: {row['Date']}")
                    if st.button(f"Approve ID {row['ID']}", key=f"pe_{idx}"):
                        df.at[idx, 'Status'] = "Sent to Purchase"
                        save_data(df)
                        st.success("অনুমোদিত এবং পারচেজ ডিপার্টমেন্টে পাঠানো হয়েছে।")
                        st.rerun()
        else: st.info("বর্তমানে কোনো পেন্ডিং রিকুইজিশন নেই।")

    # গ. পারচেজ ডিপার্টমেন্ট
    elif user_role == "Purchase Dept":
        st.subheader("💰 বাজার দর (Rate) এন্ট্রি")
        pending_pur = df[df['Status'] == "Sent to Purchase"]
        if not pending_pur.empty:
            for idx, row in pending_pur.iterrows():
                with st.expander(f"🛒 ID: {row['ID']} - {row['Item']} ({row['Site']})"):
                    rate = st.number_input(f"প্রতি ইউনিটের দাম (ID {row['ID']})", min_value=1.0, key=f"r_{idx}")
                    if st.button("Confirm Rate", key=f"btn_{idx}"):
                        df.at[idx, 'Rate'] = rate
                        df.at[idx, 'Status'] = "Waiting for CEO Permission"
                        save_data(df)
                        st.success("দাম আপডেট হয়েছে!")
                        st.rerun()
        else: st.info("রেট বসানোর জন্য কোনো কাজ পেন্ডিং নেই।")

    # ঘ. CEO প্যানেল
    elif user_role == "CEO":
        st.subheader("💎 চূড়ান্ত অনুমোদন (CEO)")
        pending_ceo = df[df['Status'] == "Waiting for CEO Permission"]
        if not pending_ceo.empty:
            for idx, row in pending_ceo.iterrows():
                total = row['Qty'] * row['Rate']
                with st.container():
                    st.warning(f"🔔 **ID {row['ID']}**: {row['Item']} - {row['Qty']} {row['Unit']} | মোট খরচ: **{total:,} TK**")
                    if st.button(f"চূড়ান্ত অনুমোদন দিন (ID {row['ID']})"):
                        df.at[idx, 'Status'] = "✅ Approved & Delivery in Progress"
                        save_data(df)
                        st.success("অনুমোদিত হয়েছে! ডেলিভারি প্রসেস শুরু হচ্ছে।")
                        st.balloons()
                        st.rerun()
        else: st.info("অনুমোদনের জন্য কোনো ফাইল পেন্ডিং নেই।")

    # --- ৭. লাইভ রিপোর্ট বোর্ড ---
    st.divider()
    st.subheader("📊 অল রিকুইজিশন বোর্ড")
    
    # স্ট্যাটাস অনুযায়ী কালার হাইলাইট (Optional)
    st.dataframe(df.style.highlight_max(axis=0, subset=['Rate'], color='#e1f5fe'), use_container_width=True)
    
    # রিপোর্ট ডাউনলোড সেকশন
    st.markdown("### 📥 রিপোর্ট এক্সপোর্ট")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="ডাউনলোড এক্সেল রিপোর্ট (CSV)",
        data=csv,
        file_name=f"ZARA_Report_{datetime.now().strftime('%d_%m_%y')}.csv",
        mime="text/csv",
        help="ক্লিক করলে সম্পূর্ণ ডাটাবেস ডাউনলোড হবে"
    )
