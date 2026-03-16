import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pil import Image # ছবি প্রসেসিং এর জন্য

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
    with open(file_path, "wb
