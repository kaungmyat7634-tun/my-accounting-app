import streamlit as st
import pandas as pd
import os

# Files for data storage
USERS_FILE = "users.csv"
TRANSACTIONS_FILE = "transactions.csv"

# Initialize files if they don't exist
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["username", "password", "role"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(TRANSACTIONS_FILE):
    pd.DataFrame(columns=["date", "item", "price", "type", "username"]).to_csv(TRANSACTIONS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_transactions():
    return pd.read_csv(TRANSACTIONS_FILE)

def save_transactions(df):
    df.to_csv(TRANSACTIONS_FILE, index=False)

# Main Application
st.title("💰 စာရင်းကိုင် Application")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    menu = ["ဝင်ရောက်မည်", "အကောင့်သစ်ဖွင့်မည်"]
    choice = st.sidebar.selectbox("မီနူး", menu)
    
    if choice == "ဝင်ရောက်မည်":
        st.subheader("🔑 အကောင့်ဝင်ရန်")
        username = st.text_input("အသုံးပြုသူအမည် (Username)")
        password = st.text_input("စကားဝှက် (Password)", type="password")
        if st.button("ဝင်မည်"):
            users = load_users()
            user = users[(users["username"] == username) & (users["password"] == password)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user.iloc[0]["role"]
                st.success(f"{username} အဖြစ် အောင်မြင်စွာ ဝင်ရောက်ပြီးပါပြီ။")
                st.rerun()
            else:
                st.error("အသုံးပြုသူအမည် သို့မဟုတ် စကားဝှက် မှားယွင်းနေပါသည်။")
                
    elif choice == "အကောင့်သစ်ဖွင့်မည်":
        st.subheader("📝 အကောင့်အသစ်ဆောက်ရန်")
        new_user = st.text_input("အသုံးပြုသူအမည်အသစ်")
        new_password = st.text_input("စကားဝှက်အသစ်", type="password")
        role = st.selectbox("ရာထူး/အဆင့်", ["ဝန်ထမ်း (User)", "စာရင်းကိုင် (Admin)"])
        
        if st.button("အကောင့်ဖွင့်မည်"):
            users = load_users()
            if new_user in users["username"].values:
                st.error("ဤအသုံးပြုသူအမည် ရှိနှင့်ပြီးသားဖြစ်ပါသည်။")
            elif new_user == "" or new_password == "":
                st.error("ကျေးဇူးပြု၍ အချက်အလက်များ ပြည့်စုံစွာဖြည့်ပါ။")
            else:
                new_row = pd.DataFrame([{"username": new_user, "password": new_password, "role": role}])
                users = pd.concat([users, new_row], ignore_index=True)
                save_users(users)
                st.success("အကောင့်အသစ် အောင်မြင်စွာ ဆောက်လုပ်ပြီးပါပြီ။ ဘေးဘောင်မှ 'ဝင်ရောက်မည်' ကိုရွေးချယ်ပါ။")

else:
    st.sidebar.write(f"👤 လူကြီးမင်း: {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("အကောင့်ထွက်မည်"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # Admin View
    if st.session_state.role in ["စာရင်းကိုင် (Admin)", "Admin"]:
        st.subheader("📊 စာရင်းချုပ်ကြည့်ရန် (Admin Only)")
        tx_df = load_transactions()
        if tx_df.empty:
            st.info("လက်ရှိတွင် မည်သည့်စာရင်းမှ မရှိသေးပါ။")
        else:
            st.dataframe(tx_df)
            total_income = tx_df[tx_df["type"] == "ရရန်"]["price"].sum()
            total_expense = tx_df[tx_df["type"] == "ပေးရန်"]["price"].sum()
            st.write(f"📈 **စုစုပေါင်း ရရန်:** {total_income} ကျပ်")
            st.write(f"📉 **စုစုပေါင်း ပေးရန်:** {total_expense} ကျပ်")
            st.write(f"⚖️ **လက်ကျန်ငွေ:** {total_income - total_expense} ကျပ်")
            
            if st.button("📝 စာရင်းအားလုံးကို ဖျက်ပစ်မည်"):
                pd.DataFrame(columns=["date", "item", "price", "type", "username"]).to_csv(TRANSACTIONS_FILE, index=False)
                st.success("စာရင်းအားလုံးကို ဖျက်သိမ်းပြီးပါပြီ။")
                st.rerun()

    # User View (Add Transactions)
    st.subheader("📥 စာရင်းအသစ်သွင်းရန်")
    date = st.date_input("နေ့စွဲ")
    item = st.text_input("ပစ္စည်း/အကြောင်းအရာ")
    price = st.number_input("ဈေးနှုန်း (ကျပ်)", min_value=0, step=1)
    tx_type = st.selectbox("အမျိုးအစား", ["ရရန်", "ပေးရန်"])
    
    if st.button("➕ ထည့်မည်"):
        if item == "" or price == 0:
            st.error("ကျေးဇူးပြု၍ အကြောင်းအရာနှင့် ဈေးနှုန်းကို သေချာစွာဖြည့်စွက်ပါ။")
        else:
            tx_df = load_transactions()
            new_row = pd.DataFrame([{"date": str(date), "item": item, "price": price, "type": tx_type, "username": st.session_state.username}])
            tx_df = pd.concat([tx_df, new_row], ignore_index=True)
            save_transactions(tx_df)
            st.success("စာရင်းသွင်းခြင်း အောင်မြင်ပါသည်။")
            st.rerun()
