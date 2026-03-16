import streamlit as st
import pandas as pd
from datetime import datetime

# ১. টাইটেল
st.set_page_config(page_title="Supply Chain Pro", layout="wide")
st.title("🏗️ জারা কনস্ট্রাকশন এর সাপ্লাই চেইন অটোমেশন")

# ২. গুগল শীট লিঙ্ক (সরাসরি CSV হিসেবে পড়া)
SHEET_ID = "1ilP26HZxJ6PviYS_dvR9S4qyr62mIttO_32QUO6O2Ro"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# ৩. ডাটা লোড করার বিকল্প পদ্ধতি
@st.cache_data(ttl=10) # প্রতি ১০ সেকেন্ড পর পর আপডেট হবে
def load_data():
    try:
        return pd.read_csv(SHEET_URL)
    except:
        return pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

df = load_data()

# ৪. ইউজার লিস্ট
USERS = {
    "admin": {"pw": "admin786", "role": "CEO"},
    "pe_rakib": {"pw": "pe123", "role": "Project Engineer"},
    "site_shuvo": {"pw": "site456", "role": "Site Engineer"},
    "pur_korim": {"pw": "pur789", "role": "Purchase Dept"},
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login"):
        st.subheader("🔐 লগইন প্যানেল")
        u_id = st.text_input("User ID")
        u_pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u_id in USERS and USERS[u_id]['pw'] == u_pw:
                st.session_state.logged_in = True
                st.session_state.role = USERS[u_id]['role']
                st.session_state.user = u_id
                st.rerun()
            else:
                st.error("ভুল আইডি বা পাসওয়ার্ড!")
else:
    user_role = st.session_state.role
    st.sidebar.info(f"ইউজার: {st.session_state.user} ({user_role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ৫. রোল ভিত্তিক কাজ ---
    if user_role == "Site Engineer":
        st.header("📋 নতুন রিকুইজিশন পাঠান")
        with st.form("req_form"):
            item = st.text_input("মালামালের নাম")
            qty = st.number_input("পরিমাণ", min_value=1)
            unit = st.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস"])
            site = st.text_input("সাইট লোকেশন")
            if st.form_submit_button("সাবমিট"):
                new_data = pd.DataFrame([{
                    "ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, 
                    "Site": site, "Status": "Pending (PE Approval)", 
                    "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), 
                    "AddedBy": st.session_state.user
                }])
                df = pd.concat([df, new_data], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=df)
                st.success("সেভ হয়েছে!")
                st.rerun()
    else:
        st.header(f"⚖️ {user_role} প্যানেল")
        status_map = {
            "Project Engineer": "Pending (PE Approval)",
            "Purchase Dept": "Sent to Purchase",
            "CEO": "Waiting for CEO Permission"
        }
        pending = df[df['Status'] == status_map.get(user_role, "None")]
        
        if not pending.empty:
            for idx, row in pending.iterrows():
                with st.expander(f"ID: {row['ID']} - {row['Item']}"):
                    if user_role == "Purchase Dept":
                        rate = st.number_input("রেট দিন", key=f"r_{idx}")
                        if st.button("Confirm Rate", key=f"b_{idx}"):
                            df.at[idx, 'Rate'], df.at[idx, 'Status'] = rate, "Waiting for CEO Permission"
                            conn.update(spreadsheet=SHEET_URL, data=df); st.rerun()
                    else:
                        if st.button("Approve", key=f"a_{idx}"):
                            nxt = {"Project Engineer": "Sent to Purchase", "CEO": "Delivery in Progress"}
                            df.at[idx, 'Status'] = nxt[user_role]
                            conn.update(spreadsheet=SHEET_URL, data=df); st.rerun()
        else:
            st.info("আপনার জন্য কোনো পেন্ডিং কাজ নেই।")

    st.divider()
    st.subheader("📊 লাইভ ট্র্যাকিং বোর্ড")
    st.dataframe(df, use_container_width=True)
