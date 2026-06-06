import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Files for data storage
TRANSACTIONS_FILE = "transactions.csv"

# Initialize transactions file if it doesn't exist
if not os.path.exists(TRANSACTIONS_FILE):
    pd.DataFrame(columns=["date", "item", "price", "type", "username"]).to_csv(TRANSACTIONS_FILE, index=False)

def load_transactions():
    return pd.read_csv(TRANSACTIONS_FILE)

def save_transactions(df):
    df.to_csv(TRANSACTIONS_FILE, index=False)

# Pre-defined Accounts
ACCOUNTS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "user": {"password": "user123", "role": "User"}
}

# App Layout Configuration
st.set_page_config(page_title="စာရင်းကိုင်စနစ်", page_icon="💰", layout="wide")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>💰 စာရင်းကိုင် Application</h2>", unsafe_index=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔑 စနစ်အတွင်းသို့ ဝင်ရောက်ရန်")
        username = st.text_input("အသုံးပြုသူအမည် (Username)", placeholder="ဥပမာ - admin")
        password = st.text_input("စကားဝှက် (Password)", type="password", placeholder="ဥပမာ - admin123")
        
        if st.button("ဝင်ရောက်မည်", use_container_width=True):
            if username in ACCOUNTS and ACCOUNTS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = ACCOUNTS[username]["role"]
                st.success("ဝင်ရောက်မှု အောင်မြင်ပါသည်။")
                st.rerun()
            else:
                st.error("အသုံးပြုသူအမည် သို့မဟုတ် စကားဝှက် မှားယွင်းနေပါသည်။")

# --- MAIN APP (LOGGED IN) ---
else:
    # Sidebar Navigation & Logout
    st.sidebar.title("📌 ထိန်းချုပ်ခန်း")
    st.sidebar.write(f"👤 အသုံးပြုသူ: **{st.session_state.username}**")
    st.sidebar.write(f"🎖️ ရာထူးဆင့်အတန်း: `{st.session_state.role}`")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 အကောင့်ထွက်မည်", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # ==========================================
    # INTERFACE 1: ADMIN VIEW (စာရင်းကိုင်/အရာရှိ မီနူး)
    # ==========================================
    if st.session_state.role == "Admin":
        st.title("📊 စာရင်းကိုင်ချုပ် မျက်နှာပြင် (Admin Interface)")
        
        # Load Data
        tx_df = load_transactions()
        
        # Dashboard Overview Cards
        if not tx_df.empty:
            total_income = tx_df[tx_df["type"] == "ရရန်"]["price"].sum()
            total_expense = tx_df[tx_df["type"] == "ပေးရန်"]["price"].sum()
            net_balance = total_income - total_expense
            
            c1, c2, c3 = st.columns(3)
            c1.metric(label="📈 စုစုပေါင်း ရရန်ငွေ", value=f"{total_income:,} ကျပ်")
            c2.metric(label="📉 စုစုပေါင်း ပေးရန်ငွေ", value=f"{total_expense:,} ကျပ်")
            c3.metric(label="⚖️ အသားတင် လက်ကျန်ငွေ", value=f"{net_balance:,} ကျပ်")
            
            st.markdown("---")
            
            # Data Table View
            st.subheader("📝 ရရှိ/ပေးရန် စာရင်းဇယားချုပ်")
            st.dataframe(tx_df, use_container_width=True)
            
            # Action Controls
            st.markdown("### ⚙️ စနစ်ထိန်းချုပ်မှု")
            col_del1, col_del2 = st.columns([1, 3])
            with col_del1:
                if st.button("❌ စာရင်းအားလုံးကို ဖျက်ပစ်မည်", type="primary"):
                    pd.DataFrame(columns=["date", "item", "price", "type", "username"]).to_csv(TRANSACTIONS_FILE, index=False)
                    st.success("စာရင်းအားလုံးကို အောင်မြင်စွာ ဖျက်သိမ်းပြီးပါပြီ။")
                    st.rerun()
        else:
            st.info("📊 လက်ရှိတွင် မည်သည့်ဝန်ထမ်းမှ စာရင်းသွင်းထားခြင်း မရှိသေးပါ။")

    # ==========================================
    # INTERFACE 2: USER VIEW (ဝန်ထမ်း စာရင်းသွင်း မီနူး)
    # ==========================================
    else:
        st.title("📥 ဝန်ထမ်း စာရင်းသွင်းမျက်နှာပြင် (User Interface)")
        st.write("နေ့စဉ် ရရန်/ပေးရန် စာရင်းများကို အောက်ပါပုံစံတွင် တိကျစွာ ဖြည့်စွက်ပေးပါ။")
        
        st.markdown("---")
        
        # Entry Form
        with st.form(key="transaction_form"):
            date = st.date_input("📆 နေ့စွဲ", value=datetime.today())
            item = st.text_input("📦 ပစ္စည်း / အကြောင်းအရာ", placeholder="ဥပမာ - ရုံးသုံးစက္ကူဝယ်ယူခြင်း")
            price = st.number_input("💵 ဈေးနှုန်း (ကျပ်ငွေဖြင့်)", min_value=0, step=100)
            tx_type = st.selectbox("🔄 အမျိုးအစား ခွဲခြားခြင်း", ["ရရန်", "ပေးရန်"])
            
            submit_button = st.form_submit_with_suppress_with_view_ids("➕ စာရင်းထဲသို့ ထည့်သွင်းမည်")
            
            if submit_button:
                if item.strip() == "" or price == 0:
                    st.error("⚠️ ကျေးဇူးပြု၍ အကြောင်းအရာနှင့် ဈေးနှုန်းကို သေသေချာချာ ဖြည့်စွက်ပေးပါ။")
                else:
                    tx_df = load_transactions()
                    new_row = pd.DataFrame([{
                        "date": str(date),
                        "item": item,
                        "price": price,
                        "type": tx_type,
                        "username": st.session_state.username
                    }])
                    tx_df = pd.concat([tx_df, new_row], ignore_index=True)
                    save_transactions(tx_df)
                    st.success(f"✅ '{item}' အတွက် စာရင်းသွင်းခြင်း အောင်မြင်ပါသည်။")
        
        # User's Own View (Show entries made by this user today)
        st.markdown("---")
        st.subheader("🕒 မိမိသွင်းထားသော စာရင်းများ")
        all_tx = load_transactions()
        user_tx = all_tx[all_tx["username"] == st.session_state.username]
        if not user_tx.empty:
            st.dataframe(user_tx, use_container_width=True)
        else:
            st.caption("ယနေ့အတွက် မည်သည့်စာရင်းမှ မသွင်းရသေးပါ။")
