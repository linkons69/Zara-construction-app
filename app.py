import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image  # এখানে PIL সব বড় হাতের অক্ষরে হবেয

# ১. পেজ সেটিংস এবং ডিজাইন
st.set_page_config(page_title="Supply Chain Pro", layout="wide", page_icon="🏗️")

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
IMAGE_DIR = "uploaded_images" # ছবি সেভ করার ফোল্ডার

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # ছবির জন্য নতুন কলাম যোগ করা হয়েছে
    return pd.DataFrame(columns=["ID", "Item", "Qty", "Unit", "Site", "Status", "Rate", "Date", "AddedBy", "RequestImage", "ReceivedImage"])

def save_data(data_df):
    data_df.to_csv(DB_FILE, index=False)

def save_image(uploaded_file, prefix="req"):
    # ইউনিক নাম দিয়ে ছবি সেভ করা
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{prefix}_{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(IMAGE_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

st.title("🏗️ জারা কনস্ট্রাকশন সাপ্লাই চেইন (With Image Proof)")

df = load_data()

# ৩. ইউজার ডাটাবেস (পাসওয়ার্ড আপডেট)
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
    m2.metric("পেন্ডিং অনুমোদন", len(df[df['Status'].str.contains('Pending|Waiting', na=False)]))
    total_budget = (df['Rate'] * df['Qty']).sum()
    m3.metric("মোট বাজেট (TK)", f"{int(total_budget):,}")

    st.divider()

    # --- ৬. রোল ভিত্তিক ইন্টারফেস ---

    # ক. সাইট ইঞ্জিনিয়ার: রিকুইজিশন এবং ছবি আপলোড
    if user_role == "Site Engineer":
        st.subheader("📋 নতুন মালামালের রিকুইজিশন")
        with st.form("req_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            item = c1.text_input("মালামালের নাম")
            qty = c1.number_input("পরিমাণ", min_value=1)
            unit = c2.selectbox("ইউনিট", ["ব্যাগ", "টন", "ফিট", "পিস", "গাড়ি"])
            site = c2.text_input("সাইট লোকেশন")
            
            # ছবির অপশন যোগ করা হয়েছে
            uploaded_image = c1.file_uploader("সাইটের ছবি আপলোড করুন (বাধ্যতামূলক)", type=["jpg", "jpeg", "png"])
            
            if st.form_submit_button("সাবমিট করুন"):
                if not uploaded_image:
                    st.error("ছবি ছাড়া রিকুইজিশন পাঠানো যাবে না।")
                else:
                    # ছবি সেভ করা
                    image_path = save_image(uploaded_image, prefix="req")
                    
                    new_row = {
                        "ID": len(df)+1, "Item": item, "Qty": qty, "Unit": unit, 
                        "Site": site, "Status": "Pending (PE Approval)", 
                        "Rate": 0, "Date": datetime.now().strftime("%d/%m/%Y"), 
                        "AddedBy": st.session_state.user,
                        "RequestImage": image_path, # ছবির পাথ সেভ
                        "ReceivedImage": None
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success("✅ ছবিসহ রিকুইজিশন পাঠানো হয়েছে!")
                    st.balloons()
                    st.rerun()

    # খ. প্রজেক্ট ইঞ্জিনিয়ার (PE): ছবি দেখে অনুমোদন
    elif user_role == "Project Engineer":
        st.subheader("⚖️ PE অনুমোদন প্যানেল")
        pending_pe = df[df['Status'] == "Pending (PE Approval)"]
        if not pending_pe.empty:
            for idx, row in pending_pe.iterrows():
                with st.expander(f"📦 ID: {row['ID']} - {row['Item']}"):
                    st.write(f"পরিমাণ: {row['Qty']} {row['Unit']} | সাইট: {row['Site']}")
                    # ছবি দেখানো
                    if pd.notna(row['RequestImage']):
                        st.image(row['RequestImage'], caption="সাইটের বাস্তব চিত্র", width=300)
                    
                    if st.button(f"Approve ID {row['ID']}", key=f"pe_{idx}"):
                        df.at[idx, 'Status'] = "Sent to Purchase"
                        save_data(df); st.rerun()
        else: st.info("কোনো পেন্ডিং কাজ নেই।")

    # গ. পারচেজ ডিপার্টমেন্ট
    elif user_role == "Purchase Dept":
        st.subheader("💰 বাজার দর (Rate) এন্ট্রি")
        pending_pur = df[df['Status'] == "Sent to Purchase"]
        if not pending_pur.empty:
            for idx, row in pending_pur.iterrows():
                with st.expander(f"🛒 ID: {row['ID']} - {row['Item']}"):
                    st.write(f"সাইট: {row['Site']} | পরিমাণ: {row['Qty']}")
                    # ছবি দেখানো (Optional)
                    if pd.notna(row['RequestImage']):
                        st.image(row['RequestImage'], width=200)
                    
                    rate = st.number_input(f"ইউনিট রেট (টাকা) - ID {row['ID']}", min_value=1.0, key=f"r_{idx}")
                    if st.button("Confirm Rate", key=f"btn_{idx}"):
                        df.at[idx, 'Rate'] = rate
                        df.at[idx, 'Status'] = "Waiting for CEO Permission"
                        save_data(df); st.rerun()
        else: st.info("কোনো কাজ পেন্ডিং নেই।")

    # ঘ. CEO প্যানেল: ছবি ও মোট দাম দেখে চূড়ান্ত অনুমোদন
    elif user_role == "CEO":
        st.subheader("💎 চূড়ান্ত অনুমোদন (CEO)")
        pending_ceo = df[df['Status'] == "Waiting for CEO Permission"]
        if not pending_ceo.empty:
            for idx, row in pending_ceo.iterrows():
                total = row['Qty'] * row['Rate']
                with st.container():
                    st.warning(f"🔔 **ID {row['ID']}**: {row['Item']} - {row['Qty']} {row['Unit']} | মোট খরচ: **{total:,} TK**")
                    # ছবি দেখানো
                    if pd.notna(row['RequestImage']):
                        st.image(row['RequestImage'], caption=f"সাইট: {row['Site']}", width=400)
                    
                    if st.button(f"চূড়ান্ত অনুমোদন দিন (ID {row['ID']})"):
                        df.at[idx, 'Status'] = " Approved & Ready for Delivery"
                        save_data(df); st.balloons(); st.rerun()
        else: st.info("অনুমোদনের জন্য কোনো ফাইল নেই।")

    # --- ৭. ডেলিভারি ও রিসিভ (Site Engineer) ---
    if user_role == "Site Engineer":
        st.divider()
        st.subheader("✅ মালামাল বুঝে পাওয়ার কনফার্মেশন")
        deliv = df[df['Status'] == " Approved & Ready for Delivery"]
        for idx, row in deliv.iterrows():
            with st.form(f"recv_{idx}"):
                st.info(f"মালামাল: {row['Item']} | পরিমাণ: {row['Qty']} {row['Unit']}")
                recv_image = st.file_uploader(f"মালামাল রিসিভ করার ছবি (ID {row['ID']})", type=["jpg", "png"], key=f"img_{idx}")
                if st.form_submit_button("মালামাল বুঝে পেয়েছি"):
                    if not recv_image:
                        st.error("রিসিভ করার ছবি ছাড়া কনফার্ম করা যাবে না।")
                    else:
                        img_path = save_image(recv_image, prefix="recv")
                        df.at[idx, 'ReceivedImage'] = img_path
                        df.at[idx, 'Status'] = "✅ Job Done"
                        save_data(df); st.balloons(); st.rerun()

    # --- ৮. রিপোর্ট বোর্ড ---
    st.divider()
    st.subheader("📊 অল রিকুইজিশন বোর্ড (উইথ ইমেজ প্রুফ)")
    
    # রিপোর্ট ডাটাফ্রেমে ছবির লিঙ্ক দেখানো (বা ছবি দেখানো সম্ভব নয়)
    st.dataframe(df.drop(columns=['RequestImage', 'ReceivedImage']), use_container_width=True)
    
    # কোডের ২০৭ নম্বর লাইনের আশেপাশে এটি পরিবর্তন করুন
cols_to_drop = ['RequestImage', 'ReceivedImage']
# যে কলামগুলো ফাইলে আছে শুধু সেগুলোই ড্রপ করবে
existing_cols_to_drop = [c for c in cols_to_drop if c in df.columns]
st.dataframe(df.drop(columns=existing_cols_to_drop), use_container_width=True)

    # বিস্তারিত দেখার অপশন (যদি ছবির লিঙ্ক দেখতে চান)
    # with st.expander("ছবির লিঙ্কসহ বিস্তারিত ডাটা দেখুন"):
    #     st.dataframe(df)

    # ডাউনলোড বাটন
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 ডাউনলোড রিপোর্ট (CSV)", data=csv, file_name=f"ZARA_Report_Image_{datetime.now().strftime('%d_%m_%y')}.csv", mime="text/csv")
