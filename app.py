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
        pd.DataFrame({"item_name": [], "unit_price": []}).to_csv("items.csv", index=False)
    if not os.path.exists("users.csv"):
        pd.DataFrame({"username": [], "location": [], "active": []}).to_csv("users.csv", index=False)
    if not os.path.exists("submissions.csv"):
        pd.DataFrame({
            "submission_id": [], "username": [], "location": [], "item_name": [],
            "size": [], "quantity": [], "unit_price": [], "total_price": [],
            "status": [], "timestamp": [], "approved_by": [], "approved_date": []
        }).to_csv("submissions.csv", index=False)

init_files()

# Load/Save functions
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

# Excel download
def download_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Approved_Records')
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="approved_records.xlsx"><button style="padding:8px 16px; background-color:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;">📥 Download Excel</button></a>'

# Sidebar
st.sidebar.title("🔐 ဝင်ရောက်မည့်ပုံစံ")
user_type = st.sidebar.radio("သင်က", ["📝 ဝန်ထမ်း (User)", "👑 စာရင်းကိုင် (Admin)"])

if user_type == "👑 စာရင်းကိုင် (Admin)":
    st.title("👑 Admin Dashboard")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 စာရင်းများ", "📦 ပစ္စည်းများ", "👥 Users များ", "✅ အတည်ပြုပြီးသား", "📊 အစီရင်ခံစာ"])
    
    # ===== TAB 1 =====
    with tab1:
        st.subheader("⏳ အတည်မပြုရသေးသော စာရင်းများ")
        submissions = load_submissions()
        pending = submissions[submissions["status"] == "pending"]
        if pending.empty:
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
                    if col1.button("✅ အတည်ပြုမယ်", key=f"approve_{idx}"):
                        submissions.loc[submissions["submission_id"] == row["submission_id"], "status"] = "approved"
                        submissions.loc[submissions["submission_id"] == row["submission_id"], "approved_by"] = "Admin"
                        submissions.loc[submissions["submission_id"] == row["submission_id"], "approved_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_submissions(submissions)
                        st.experimental_rerun()
                    if col2.button("❌ ပယ်ဖျက်မယ်", key=f"reject_{idx}"):
                        submissions = submissions[submissions["submission_id"] != row["submission_id"]]
                        save_submissions(submissions)
                        st.experimental_rerun()
    
    # ===== TAB 2 =====
    with tab2:
        st.subheader("📦 ပစ္စည်းနှင့်ဈေးနှုန်းများ")
        items = load_items()
        with st.form("add_item"):
            col1, col2 = st.columns(2)
            new_item = col1.text_input("ပစ္စည်းအမည်")
            new_price = col2.number_input("ဈေးနှုန်း (ကျပ်)", min_value=0)
            if st.form_submit_button("➕ ထည့်မယ်") and new_item:
                new_row = pd.DataFrame({"item_name": [new_item], "unit_price": [new_price]})
                items = pd.concat([items, new_row], ignore_index=True)
                save_items(items)
                st.experimental_rerun()
        st.write("---")
        for idx, row in items.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{row['item_name']}**")
            col2.write(f"{row['unit_price']} ကျပ်")
            if col3.button("🗑 ဖျက်", key=f"del_item_{idx}"):
                items = items.drop(idx)
                save_items(items)
                st.experimental_rerun()
    
    # ===== TAB 3 =====
    with tab3:
        st.subheader("👥 User များ")
        users = load_users()
        with st.form("add_user"):
            col1, col2, col3 = st.columns(3)
            new_username = col1.text_input("အမည်")
            new_location = col2.text_input("နေရာ")
            is_active = col3.checkbox("Active", True)
            if st.form_submit_button("➕ User ထည့်မယ်") and new_username:
                new_row = pd.DataFrame({"username": [new_username], "location": [new_location], "active": [is_active]})
                users = pd.concat([users, new_row], ignore_index=True)
                save_users(users)
                st.experimental_rerun()
        st.write("---")
        for idx, row in users.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            col1.write(row["username"])
            col2.write(row["location"])
            new_status = col3.checkbox("Active", row["active"], key=f"active_{idx}")
            if new_status != row["active"]:
                users.loc[idx, "active"] = new_status
                save_users(users)
                st.experimental_rerun()
            if col4.button("🗑 ဖျက်", key=f"del_user_{idx}"):
                users = users.drop(idx)
                save_users(users)
                st.experimental_rerun()
    
    # ===== TAB 4 =====
    with tab4:
        st.subheader("✅ အတည်ပြုပြီးသား စာရင်းများ")
        submissions = load_submissions()
        approved = submissions[submissions["status"] == "approved"].copy()
        if approved.empty:
            st.info("အတည်ပြုပြီး စာရင်းမရှိသေးပါ")
        else:
            approved["approved_date_dt"] = pd.to_datetime(approved["approved_date"], errors='coerce')
            valid_dates = approved["approved_date_dt"].dropna()
            if not valid_dates.empty:
                col1, col2 = st.columns(2)
                start = col1.date_input("မှ (From)", valid_dates.min().date())
                end = col2.date_input("ထိ (To)", valid_dates.max().date())
                mask = (approved["approved_date_dt"].dt.date >= start) & (approved["approved_date_dt"].dt.date <= end)
                filtered = approved[mask]
                st.write(f"**ပြသနေသော စာရင်းအရေအတွက်:** {len(filtered)}")
                st.dataframe(filtered.drop(columns=["approved_date_dt"]))
                st.markdown(download_excel(filtered.drop(columns=["approved_date_dt"])), unsafe_allow_html=True)
    
    # ===== TAB 5 =====
    with tab5:
        st.subheader("📊 အစီရင်ခံစာနှင့် ဇယားကွက်")
        submissions = load_submissions()
        approved = submissions[submissions["status"] == "approved"].copy()
        if approved.empty:
            st.info("အတည်ပြုပြီး စာရင်းမရှိသေးပါ။")
        else:
            approved["total_price"] = pd.to_numeric(approved["total_price"], errors='coerce').fillna(0)
            approved["quantity"] = pd.to_numeric(approved["quantity"], errors='coerce').fillna(0)
            c1, c2, c3 = st.columns(3)
            c1.metric("📄 စုစုပေါင်းစာရင်း", len(approved))
            c2.metric("📦 စုစုပေါင်းပစ္စည်းအရေအတွက်", int(approved["quantity"].sum()))
            c3.metric("💰 စုစုပေါင်းငွေ (ကျပ်)", f"{approved['total_price'].sum():,.0f}")
            st.markdown("### 📊 ပစ္စည်းအလိုက် ရောင်းအား")
            st.bar_chart(approved.groupby("item_name")["total_price"].sum().sort_values(ascending=False))
            st.markdown("### 📊 နေရာအလိုက် ရောင်းအား")
            st.bar_chart(approved.groupby("location")["total_price"].sum().sort_values(ascending=False))

# ===== USER SIDE =====
else:
    st.title("📝 စာရင်းသွင်းရန်")
    users = load_users()
    active_users = users[users["active"] == True]
    if active_users.empty:
        st.warning("တက်ကြွသော user မရှိပါ။")
    else:
        username = st.selectbox("သင်၏အမည်", active_users["username"].tolist())
        location = active_users[active_users["username"] == username]["location"].values[0]
        st.write(f"**နေရာ:** {location}")
        items = load_items()
        if items.empty:
            st.warning("ပစ္စည်းများ မရှိသေးပါ။")
        else:
            item = st.selectbox("ပစ္စည်းအမျိုးအစား", items["item_name"].tolist())
            price = items[items["item_name"] == item]["unit_price"].values[0]
            size = st.text_input("Size (ဥပမာ - L, XL, 1kg, 5kg)")
            qty = st.number_input("အရေအတွက်", min_value=1, step=1)
            total = price * qty
            st.info(f"**စုစုပေါင်းဈေး:** {total} ကျပ်")
            if st.button("📤 စာရင်းတင်မယ်"):
                submissions = load_submissions()
                new_id = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_row = pd.DataFrame([{
                    "submission_id": new_id, "username": username, "location": location,
                    "item_name": item, "size": size, "quantity": qty, "unit_price": price,
                    "total_price": total, "status": "pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "approved_by": "", "approved_date": ""
                }])
                save_submissions(pd.concat([submissions, new_row], ignore_index=True))
                st.success(f"စာရင်းတင်ပြီးပါပြီ။ အိုင်ဒီ: {new_id}")
                st.balloons()
