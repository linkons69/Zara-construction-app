import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# ১. পেজ সেটিংস এবং ডিজাইন
st.set_page_config(page_title="ZARA Supply Chain", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007bff; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #0056b3; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { border-radius: 10px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    img { border-radius: 10px; border: 2px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# ২. ডাটা এবং ইমেজ ম্যানেজমেন্ট
DB_FILE = "requisition_data.csv"
IMAGE_DIR = "uploaded_images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy", "RequestImage", "ReceivedImage"])

def save_data(data_df):
    data_df.to_csv(DB_FILE, index=False)

def save_image(uploaded_file, prefix="req"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{prefix}_{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(IMAGE_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

st.title("🏗️ জারা কনস্ট্রাকশন সাপ্লাই চেইন অটোমেশন")

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
        with st.form("login"):
            st.markdown("<h2 style='text-align: center;'>🔐 মেম্বার লগইন</h2>", unsafe_allow_html=True)
            u_id = st.text_input("ইউজার আইডি")
            u_pw = st.text_input("পাসওয়ার্ড", type="password")
            if st.form_submit_button("লগইন করুন"):
                if u_id in USERS and USERS[u_id]['pw'] == u_pw:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.session_state.role = USERS[u_id]['role']
                    st.rerun()
                else: st.error("ভুল ইউজার আইডি বা পাসওয়ার্ড!")
else:
    user_role = st.session_state.role
    st.sidebar.markdown(f"### 👤 {st.session_state.user} ({user_role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ৫. সামারি মেট্রিক্স ---
    m1, m2, m3 = st.columns(3)
    m1.metric("মোট রিকুইজিশন", len(df))
    pending_count = len(df[~df['Status'].str.contains('✅', na=False)])
    m2.metric("পেন্ডিং কাজ", pending_count)
    total_budget = (pd.to_numeric(df['Rate'], errors='coerce') * pd.to_numeric(df['Qty'], errors='coerce')).sum()
    m3.metric("মোট বাজেট (TK)", f"{int(total_budget):,}")

    st.divider()

    # --- ৬. রোল ভিত্তিক ইন্টারফেস ---

    if user_role == "Site Engineer":
        st.subheader("📋 নতুন রিকুইজিশন তৈরি")
        with st.form("req_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            item = c1.text_input("মালামালের নাম")
            qty = c1.number_input("পরিমাণ", min_value=1)
            unit = c2.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস", "গাড়ি"])
            site = c2.text_input("সাইট লোকেশন")
            uploaded_image = c1.file_uploader("সাইটের ছবি (অবশ্যই দিন)", type=["jpg", "jpeg", "png"])
            
            if st.form_submit_button("সাবমিট"):
                if not uploaded_image:
                    st.error("ছবি ছাড়া রিকুইজিশন নেওয়া সম্ভব নয়।")
                else:
                    image_path = save_image(uploaded_image, prefix="req")
                    new_row = {
                        "ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, 
                        "Site": site, "Status": "Pending (PE Approval)", 
                        "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), 
                        "AddedBy": st.session_state.user, "RequestImage": image_path, "ReceivedImage": None
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success("সফলভাবে পাঠানো হয়েছে!")
                    st.balloons()
                    st.rerun()

    elif user_role == "Project Engineer":
        st.subheader("⚖️ PE অনুমোদন")
        pending_pe = df[df['Status'] == "Pending (PE Approval)"]
        for idx, row in pending_pe.iterrows():
            with st.expander(f"📦 ID: {row['ID']} - {row['Item']}"):
                if pd.notna(row['RequestImage']): st.image(row['RequestImage'], width=300)
                if st.button(f"Approve ID {row['ID']}", key=f"pe_{idx}"):
                    df.at[idx, 'Status'] = "Sent to Purchase"
                    save_data(df); st.rerun()

    elif user_role == "Purchase Dept":
        st.subheader("💰 রেট এন্ট্রি")
        pending_pur = df[df['Status'] == "Sent to Purchase"]
        for idx, row in pending_pur.iterrows():
            with st.expander(f"🛒 ID: {row['ID']} - {row['Item']}"):
                rate = st.number_input(f"রেট (ID {row['ID']})", min_value=1.0, key=f"r_{idx}")
                if st.button("Confirm", key=f"btn_{idx}"):
                    df.at[idx, 'Rate'] = rate
                    df.at[idx, 'Status'] = "Waiting for CEO Permission"
                    save_data(df); st.rerun()

    elif user_role == "CEO":
        st.subheader("💎 চূড়ান্ত অনুমোদন")
        pending_ceo = df[df['Status'] == "Waiting for CEO Permission"]
        for idx, row in pending_ceo.iterrows():
            st.warning(f"ID {row['ID']}: {row['Item']} | মোট: {row['Qty']*row['Rate']:,} TK")
            if pd.notna(row['RequestImage']): st.image(row['RequestImage'], width=300)
            if st.button(f"Approve ID {row['ID']}", key=f"ceo_{idx}"):
                df.at[idx, 'Status'] = "Approved & Ready for Delivery"
                save_data(df); st.balloons(); st.rerun()

    # মালামাল বুঝে পাওয়ার সেকশন (সাইট ইঞ্জিনিয়ারের জন্য)
    if user_role == "Site Engineer":
        st.divider()
        st.subheader("🚚 মালামাল গ্রহণ (Delivery Received)")
        deliv = df[df['Status'] == "Approved & Ready for Delivery"]
        for idx, row in deliv.iterrows():
            with st.expander(f"মালামাল বুঝে নিন: {row['Item']}"):
                recv_img = st.file_uploader(f"রিসিভ করার ছবি (ID {row['ID']})", type=["jpg", "png"], key=f"recv_{idx}")
                if st.button(f"Confirm Delivery ID {row['ID']}", key=f"conf_{idx}"):
                    if recv_img:
                        df.at[idx, 'ReceivedImage'] = save_image(recv_img, prefix="recv")
                        df.at[idx, 'Status'] = "✅ Job Done"
                        save_data(df); st.balloons(); st.rerun()
                    else: st.error("ছবি আপলোড করুন।")

    # --- ৭. অল রিকুইজিশন বোর্ড (KeyError Fix) ---
    st.divider()
    st.subheader("📊 অল ট্র্যাকিং বোর্ড")
    
    # এরর এড়াতে কলাম চেক করে ড্রপ করা
    cols_to_show = df.columns.tolist()
    for img_col in ['RequestImage', 'ReceivedImage']:
        if img_col in cols_to_show:
            cols_to_show.remove(img_col)
    
    st.dataframe(df[cols_to_show], use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 ডাউনলোড রিপোর্ট", data=csv, file_name="ZARA_Report.csv", mime="text/csv")
