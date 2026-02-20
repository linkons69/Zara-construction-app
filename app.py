import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ১. অ্যাপ কনফিগারেশন
st.set_page_config(page_title="Supply Chain Pro", layout="wide")
st.title("🏗️ কনস্ট্রাকশন সাপ্লাই চেইন অটোমেশন")

# ২. গুগল শীট কানেকশন (আপনার দেওয়া নতুন লিঙ্ক)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ilP26HZxJ6PviYS_dvR9S4qyr62mIttO_32QUO6O2Ro/edit?usp=sharing" 
conn = st.connection("gsheets", type=GSheetsConnection)

# ডাটা লোড করা
try:
    df = conn.read(spreadsheet=SHEET_URL)
except Exception as e:
    st.error("গুগল শীট থেকে ডাটা লোড করা যাচ্ছে না। দয়া করে সেটিংস চেক করুন।")
    df = pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

# ৩. ইউজার ডাটাবেস
USERS = {
    "admin": {"pw": "admin786", "role": "CEO"},
    "pe_rakib": {"pw": "pe123", "role": "Project Engineer"},
    "site_shuvo": {"pw": "site456", "role": "Site Engineer"},
    "pur_korim": {"pw": "pur789", "role": "Purchase Dept"},
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# লগইন সেকশন
if not st.session_state.logged_in:
    with st.form("login_panel"):
        st.subheader("🔐 সিস্টেম লগইন")
        u_id = st.text_input("ইউজার আইডি")
        u_pw = st.text_input("পাসওয়ার্ড", type="password")
        if st.form_submit_button("Login"):
            if u_id in USERS and USERS[u_id]['pw'] == u_pw:
                st.session_state.logged_in = True
                st.session_state.role = USERS[u_id]['role']
                st.session_state.user = u_id
                st.rerun()
            else:
                st.error("আইডি বা পাসওয়ার্ড ভুল!")
else:
    user_role = st.session_state.role
    st.sidebar.success(f"লগইন: {st.session_state.user} ({user_role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ৪. রোল ভিত্তিক কাজ ---
    if user_role == "Site Engineer":
        st.header("📋 নতুন রিকুইজিশন পাঠান")
        with st.form("req_form"):
            item = st.text_input("মালামালের নাম")
            qty = st.number_input("পরিমাণ", min_value=1)
            unit = st.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস", "গাড়ি"])
            site = st.text_input("সাইট লোকেশন")
            if st.form_submit_button("সাবমিট করুন"):
                new_data = pd.DataFrame([{
                    "ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, 
                    "Site": site, "Status": "Pending (PE Approval)", 
                    "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), 
                    "AddedBy": st.session_state.user
                }])
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success("গুগল শীটে সেভ হয়েছে!")
                st.rerun()

    else:
        st.header(f"⚖️ {user_role} প্যানেল")
        status_map = {
            "Project Engineer": "Pending (PE Approval)",
            "Purchase Dept": "Sent to Purchase",
            "CEO": "Waiting for CEO Permission"
        }
        
        pending_items = df[df['Status'] == status_map.get(user_role, "None")]

        if not pending_items.empty:
            for idx, row in pending_items.iterrows():
                with st.expander(f"ID: {row['ID']} - {row['Item']} ({row['Site']})"):
                    if user_role == "Purchase Dept":
                        rate = st.number_input(f"ID {row['ID']} এর রেট দিন", key=f"rate_{idx}")
                        if st.button("রেট সেভ করুন", key=f"btn_{idx}"):
                            df.at[idx, 'Rate'] = rate
                            df.at[idx, 'Status'] = "Waiting for CEO Permission"
                            conn.update(spreadsheet=SHEET_URL, data=df)
                            st.rerun()
                    else:
                        if st.button(f"অনুমোদন দিন (ID {row['ID']})", key=f"app_{idx}"):
                            next_status = {
                                "Project Engineer": "Sent to Purchase",
                                "CEO": "Delivery in Progress"
                            }
                            df.at[idx, 'Status'] = next_status[user_role]
                            conn.update(spreadsheet=SHEET_URL, data=df)
                            st.rerun()
        else:
            st.info("আপনার জন্য কোনো কাজ পেন্ডিং নেই।")

    # ৫. ডাটা টেবিল
    st.divider()
    st.subheader("📊 লাইভ ট্র্যাকিং বোর্ড")
    st.dataframe(df, use_container_width=True)
    
    # ডেলিভারি রিসিভ (Site Engineer)
    if user_role == "Site Engineer":
        deliv = df[df['Status'] == "Delivery in Progress"]
        for idx, row in deliv.iterrows():
            if st.button(f"✅ মালামাল বুঝে পেয়েছি (ID {row['ID']})"):
                df.at[idx, 'Status'] = "✅ Job Done"
                conn.update(spreadsheet=SHEET_URL, data=df)
                st.rerun()

