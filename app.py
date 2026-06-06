import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64

# Page config
st.set_page_config(page_title="စာရင်းကိုင်စနစ် (Pro)", layout="wide")

# Initialize data files
def init_files():
    if not os.path.exists("items.csv"):
        df = pd.DataFrame({"item_name": [], "unit_price": []})
        df.to_csv("items.csv", index=False)
    if not os.path.exists("users.csv"):
        df = pd.DataFrame({"username": [], "location": [], "active": []})
        df.to_csv("users.csv", index=False)
    if not os.path.exists("submissions.csv"):
        df = pd.DataFrame({
            "submission_id": [], "username": [], "location": [], "item_name": [],
            "size": [], "quantity": [], "unit_price": [], "total_price": [],
            "status": [], "timestamp": [], "approved_by": [], "approved_date": []
        })
        df.to_csv("submissions.csv", index=False)

init_files()

# Load data functions
def load_items():
    return pd.read_csv("items.csv")

def load_users():
    return pd.read_csv("users.csv")

def load_submissions():
    return pd.read_csv("submissions.csv")

def save_items(df):
    df.to_csv("items.csv", index=False)

def save_users(df):
    df.to_csv("users.csv", index=False)

def save_submissions(df):
    df.to_csv("submissions.csv", index=False)

# Excel download function
def download_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Approved_Records')
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="approved_records.xlsx" style="text-decoration:none;"><button style="padding:8px 16px; background-color:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;">📥 Click to Download Excel</button></a>'
    return href

# Sidebar
st.sidebar.title("🔐 ဝင်ရောက်မည့်ပုံစံ")
user_type = st.sidebar.radio("သင်က", ["📝 ဝန်ထမ်း (User)", "👑 စာရင်းကိုင် (Admin)"])

if user_type == "👑 စာရင်းကိုင် (Admin)":
    st.title("👑 Admin Dashboard")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 စာရင်းများ", "📦 ပစ္စည်းများ", "👥 Users များ", "✅ အတည်ပြုပြီးသား", "📊 အစီရင်ခံစာ"])
    
    # ========== TAB 1: PENDING SUBMISSIONS ==========
    with tab1:
        st.subheader("⏳ အတည်မပြုရသေးသော စာရင်းများ")
        submissions = load_submissions()
        pending = submissions[submissions["status"] == "pending"]
        
        if len(pending) == 0:
            st.info("စာရင်းများ မရှိသေးပါ")
        else:
            for idx, row in pending.iterrows():
                with st.expander(f"📄 #{row['submission_id']} - {row['username']} - {row['location']}"):
                    st.write(f"**ပစ္စည်း:** {row['item_name']}")
                    st.write(f"**Size:** {row['size']}")
                    st.write(f"**အရေအတွက်:** {row['quantity']}")
                    st.write(f"**တစ်ခုဈေး:** {row['unit_price']} ကျပ်")
                    st.write(f"**စုစုပေါင်း:** {row['total_price']} ကျပ်")
                    st.write(f"**တင်ချိန်:** {row['timestamp']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ အတည်ပြုမယ်", key=f"approve_{idx}"):
                            submissions.loc[submissions["submission_id"] == row["submission_id"], "status"] = "approved"
                            submissions.loc[submissions["submission_id"] == row["submission_id"], "approved_by"] = "Admin"
                            submissions.loc[submissions["submission_id"] == row["submission_id"], "approved_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            save_submissions(submissions)
                            st.experimental_rerun()
                    with col2:
                        if st.button(f"❌ ပယ်ဖျက်မယ်", key=f"reject_{idx}"):
                            submissions = submissions[submissions["submission_id"] != row["submission_id"]]
                            save_submissions(submissions)
                            st.experimental_rerun()
    
    # ========== TAB 2: ITEMS MANAGEMENT ==========
    with tab2:
        st.subheader("📦 ပစ္စည်းနှင့်ဈေးနှုန်းများ")
        items = load_items()
        
        with st.form("add_item"):
            col1, col2 = st.columns(2)
            with col1:
                new_item = st.text_input("ပစ္စည်းအမည်")
            with col2:
                new_price = st.number_input("ဈေးနှုန်း (ကျပ်)", min_value=0)
            if st.form_submit_button("➕ ထည့်မယ်"):
                if new_item:
                    new_row = pd.DataFrame({"item_name": [new_item], "unit_price": [new_price]})
                    items = pd.concat([items, new_row], ignore_index=True)
                    save_items(items)
                    st.experimental_rerun()
        
        st.write("---")
        for idx, row in items.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{row['item_name']}**")
            with col2:
                st.write(f"{row['unit_price']} ကျပ်")
            with col3:
                if st.button(f"🗑 ဖျက်", key=f"del_item_{idx}"):
                    items = items.drop(idx)
                    save_items(items)
                    st.experimental_rerun()
    
    # ========== TAB 3: USERS MANAGEMENT ==========
    with tab3:
        st.subheader("👥 User များ")
        users = load_users()
        
        with st.form("add_user"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_username = st.text_input("အမည်")
            with col2:
                new_location = st.text_input("နေရာ")
            with col3:
                is_active = st.checkbox("Active", value=True)
            if st.form_submit_button("➕ User ထည့်မယ်"):
                if new_username:
                    new_row = pd.DataFrame({"username": [new_username], "location": [new_location], "active": [is_active]})
                    users = pd.concat([users, new_row], ignore_index=True)
                    save_users(users)
                    st.experimental_rerun()
        
        st.write("---")
        for idx, row in users.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(row["username"])
            with col2:
                st.write(row["location"])
            with col3:
                new_status = st.checkbox("Active", value=row["active"], key=f"active_{idx}")
                if new_status != row["active"]:
                    users.loc[idx, "active"] = new_status
                    save_users(users)
                    st.experimental_rerun()
            with col4:
                if st.button(f"🗑 ဖျက်", key=f"del_user_{idx}"):
                    users = users.drop(idx)
                    save_users(users)
                    st.experimental_rerun()
    
    # ========== TAB 4: APPROVED RECORDS WITH FILTER ==========
    with tab4:
        st.subheader("✅ အတည်ပြုပြီးသား စာရင်းများ")
        submissions = load_submissions()
        approved = submissions[submissions["status"] == "approved"].copy()
        
        if len(approved) == 0:
            st.info("အတည်ပြုပြီး စာရင်းမရှိသေးပါ")
        else:
            # Date filter fix (errors='coerce' ထည့်ပြီး ရက်စွဲအလွတ်ပြဿနာ ဖြေရှင်းထားပါတယ်)
            st.markdown("### 📅 ရက်စွဲအလိုက် စစ်ထုတ်ရန်")
            approved["approved_date_dt"] = pd.to_datetime(approved["approved_date"], errors='coerce')
            
            # စာရင်းထဲမှာ ရက်စွဲအမှန်ပါတာတွေကိုပဲ ပထမဆုံး စစ်ထုတ်ပါတယ်
            valid_dates = approved["approved_date_dt"].dropna()
            min_d = valid_dates.min() if not valid_dates.empty else datetime.now()
            max_d = valid_dates.max() if not valid_dates.empty else datetime.now()
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("မှ (From)", value=min_d.date())
            with col2:
                end_date = st.date_input("ထိ (To)", value=max_d.date())
            
            mask = (approved["approved_date_dt"].dt.date >= start_date) & (approved["approved_date_dt"].dt.date <= end_date)
            filtered = approved[mask]
            
            st.write(f"**ပြသနေသော စာရင်းအရေအတွက်:** {len(filtered)}")
            st.dataframe(filtered.drop(columns=["approved_date_dt"]))
            
            # Excel download button
            st.markdown("### 📎 Excel ဖိုင်ထုတ်ရန်")
            st.markdown(download_excel(filtered.drop(columns=["approved_date_dt"])), unsafe_allow_html=True)
    
    # ========== TAB 5: REPORT & CHART ==========
    with tab5:
        st.subheader("📊 အစီရင်ခံစာနှင့် ဇယားကွက်")
        submissions = load_submissions()
        approved = submissions[submissions["status"] == "approved"].copy()
        
        if len(approved) == 0:
            st.info("အတည်ပြုပြီး စာရင်းမရှိသေးပါ။ ဇယားမပြနိုင်သေးပါ။")
        else:
            # Data Type ပြဿနာကို ကြိုတင်ကာကွယ်ရန် နံပါတ်အဖြစ် ပြောင်းလဲခြင်း
            approved["total_price"] = pd.to_numeric(approved["total_price"], errors='coerce').fillna(0)
            approved["quantity"] = pd.to_numeric(approved["quantity"], errors='coerce').fillna(0)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            total_amount = approved["total_price"].sum()
            total_items = approved["quantity"].sum()
            total_entries = len(approved)
            
            with col1:
                st.metric("📄 စုစုပေါင်းစာရင်း", total_entries)
            with col2:
                st.metric("📦 စုစုပေါင်းပစ္စည်းအရေအတွက်", int(total_items))
            with col3:
                st.metric("💰 စုစုပေါင်းငွေ (ကျပ်)", f"{total_amount:,.0f}")
            
            st.write("---")
            
            # Bar chart by item
            st.markdown("### 📊 ပစ္စည်းအလိုက် ရောင်းအား (ကျပ်)")
            item_sales = approved.groupby("item_name")["total_price"].sum().sort_values(ascending=False)
            st.bar_chart(item_sales)
            
            # Bar chart by location
            st.markdown("### 📊 နေရာအလိုက် ရောင်းအား (ကျပ်)")
            location_sales = approved.groupby("location")["total_price"].sum().sort_values(ascending=False)
            st.bar_chart(location_sales)

# ========== USER SIDE ==========
else:
    st.title("📝 စာရင်းသွင်းရန်")
    
    users = load_users()
    active_users = users[users["active"] == True]
    
    if len(active_users) == 0:
        st.warning("လက်ရှိတွင် တက်ကြွသော user မရှိပါ။ ကျေးဇူးပြု၍ admin ကို ဆက်သွယ်ပါ။")
    else:
        username = st.selectbox("သင်၏အမည်", active_users["username"].tolist())
        location = active_users[active_users["username"] == username]["location"].values[0]
        
        st.write(f"**နေရာ:** {location}")
        
        items = load_items()
        if len(items) == 0:
            st.warning("ပစ္စည်းများ မရှိသေးပါ။ ကျေးဇူးပြု၍ admin ကို ဆက်သွယ်ပါ။")
        else:
            item_name = st.selectbox("ပစ္စည်းအမျိုးအစား", items["item_name"].tolist())
            unit_price = items[items["item_name"] == item_name]["unit_price"].values[0]
            
            size = st.text_input("Size (ဥပမာ - L, XL, 1kg, 5kg)")
            quantity = st.number_input("အရေအတွက်", min_value=1, step=1)
            
            total_price = unit_price * quantity
            st.info(f"**စုစုပေါင်းဈေး:** {total_price} ကျပ်")
            
            if st.button("📤 စာရင်းတင်မယ် (Submit)"):
                submissions = load_submissions()
                new_id = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_row = pd.DataFrame({
                    "submission_id": [new_id],
                    "username": [username],
                    "location": [location],
                    "item_name": [item_name],
                    "size": [size],
                    "quantity": [quantity],
                    "unit_price": [unit_price],
                    "total_price": [total_price],
                    "status": ["pending"],
                    "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "approved_by": [""],
                    "approved_date": [""]
                })
                submissions = pd.concat([submissions, new_row], ignore_index=True)
                save_submissions(submissions)
                st.success(f"စာရင်းတင်ပြီးပါပြီ။ အိုင်ဒီ: {new_id}")
                st.balloons()