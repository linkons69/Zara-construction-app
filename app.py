import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ১. অ্যাপ কনফিগারেশন
st.set_page_config(page_title="Supply Chain Pro", layout="wide")
st.title("🏗️ কনস্ট্রাকশন সাপ্লাই চেইন অটোমেশন")

# ২. গুগল শীট কানেকশন (লিঙ্ক আপডেট করা হয়েছে)


try:
    df = conn.read(spreadsheet=SHEET_URL)
except Exception as e:
    st.error(f"শীট লোড করতে সমস্যা হচ্ছে: {e}")
    df = pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy"])

# ৩. ইউজার লিস্ট (পাসওয়ার্ডসহ)
USERS = {
    "admin": {"pw": "admin786", "role": "CEO"},
    "pe_rakib": {"pw": "pe123", "role": "Project Engineer"},
    "site_shuvo": {"pw": "site456", "role": "Site Engineer"},
    "pur_korim": {"pw": "pur789", "role": "Purchase Dept"},
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# লগইন ফর্ম
if not st.session_state.logged_in:
    with st.form("login"):
        u_id = st.text_input("User ID")
        u_pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u_id in USERS and USERS[u_id]['pw'] == u_pw:
                st.session_state.logged_in = True
                st.session_state.role = USERS[u_id]['role']
                st.session_state.user = u_id
                st.rerun()
            else: st.error("ভুল ইউজার আইডি বা পাসওয়ার্ড!")
else:
    user_role = st.session_state.role
    st.sidebar.info(f"লগইন: {st.session_state.user} ({user_role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ৪. ওয়ার্কফ্লো লজিক ---
    if user_role == "Site Engineer":
        st.header("📋 নতুন রিকুইজিশন তৈরি")
        with st.form("req"):
            item = st.text_input("মালামালের নাম")
            qty = st.number_input("পরিমাণ", min_value=1)
            unit = st.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস"])
            site = st.text_input("সাইট লোকেশন")
            if st.form_submit_button("সাবমিট"):
                new_row = pd.DataFrame([{"ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, "Site": site, "Status": "Pending (PE Approval)", "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), "AddedBy": st.session_state.user}])
                df = pd.concat([df, new_row], ignore_index=True)
               
                st.success("সফলভাবে পাঠানো হয়েছে!")
                st.rerun()
    else:
        # অনুমোদন প্যানেল
        status_map = {"Project Engineer": "Pending (PE Approval)", "Purchase Dept": "Sent to Purchase", "CEO": "Waiting for CEO Permission"}
        pending = df[df['Status'] == status_map.get(user_role, "None")]
        if not pending.empty:
            for idx, row in pending.iterrows():
                with st.expander(f"ID: {row['ID']} | {row['Item']}"):
                    if user_role == "Purchase Dept":
                        r = st.number_input(f"ID {row['ID']} এর রেট দিন", key=f"r{idx}")
                        if st.button("Confirm Rate", key=f"b{idx}"):
                            df.at[idx, 'Rate'], df.at[idx, 'Status'] = r, "Waiting for CEO Permission"
                            conn.update(spreadsheet=SHEET_URL, data=df); st.rerun()
                    else:
                        if st.button(f"Approve (ID {row['ID']})", key=f"a{idx}"):
                            next_st = {"Project Engineer": "Sent to Purchase", "CEO": "Delivery in Progress"}
                            df.at[idx, 'Status'] = next_st[user_role]
                            conn.update(spreadsheet=SHEET_URL, data=df); st.rerun()
        else:
            st.info("কোনো পেন্ডিং কাজ নেই।")

    st.divider()
    st.subheader("📊 অল ট্র্যাকিং বোর্ড")
    st.dataframe(df, use_container_width=True)

    # ডেলিভারি কনফার্মেশন
    if user_role == "Site Engineer":
        deliv = df[df['Status'] == "Delivery in Progress"]
        for idx, row in deliv.iterrows():
            if st.button(f"✅ Received (ID {row['ID']})"):
                df.at[idx, 'Status'] = "✅ Job Done"
                conn.update(spreadsheet=SHEET_URL, data=df); st.rerun()



