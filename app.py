import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64

st.set_page_config(page_title="စာရင်းကိုင်စနစ်", layout="wide")

# Initialize
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

def load_items(): return pd.read_csv("items.csv")
def load_users(): return pd.read_csv("users.csv")
def load_submissions(): return pd.read_csv("submissions.csv")
def save_items(df): df.to_csv("items.csv", index=False)
def save_users(df): df.to_csv("users.csv", index=False)
def save_submissions(df): df.to_csv("submissions.csv", index=False)

def download_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Records')
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="records.xlsx"><button>📥 Download Excel</button></a>'

st.sidebar.title("🔐 ဝင်ရောက်မည့်ပုံစံ")
user_type = st.sidebar.radio("သင်က", ["📝 ဝန်ထမ်း (User)", "👑 စာရင်းကိုင် (Admin)"])

if user_type == "👑 စာရင်းကိုင် (Admin)":
    st.title("👑 Admin Dashboard")
    t1, t2, t3, t4, t5 = st.tabs(["📋 စာရင်းများ", "📦 ပစ္စည်းများ", "👥 Users", "✅ အတည်ပြုပြီးသား", "📊 အစီရင်ခံစာ"])
    
    with t1:
        st.subheader("⏳ အတည်မပြုရသေးသော စာရင်းများ")
        df = load_submissions()
        pending = df[df["status"] == "pending"]
        if pending.empty:
            st.info("စာရင်းမရှိသေးပါ")
        else:
            for i, r in pending.iterrows():
                with st.expander(f"📄 #{r['submission_id']} - {r['username']}"):
                    st.write(f"ပစ္စည်း: {r['item_name']} | Size: {r['size']} | အရေအတွက်: {r['quantity']} | ဈေး: {r['unit_price']} | စုစု: {r['total_price']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ အတည်ပြု", key=f"app_{i}"):
                        df.loc[df["submission_id"] == r["submission_id"], "status"] = "approved"
                        df.loc[df["submission_id"] == r["submission_id"], "approved_by"] = "Admin"
                        df.loc[df["submission_id"] == r["submission_id"], "approved_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_submissions(df)
                        st.rerun()
                    if c2.button("❌ ပယ်ဖျက်", key=f"rej_{i}"):
                        df = df[df["submission_id"] != r["submission_id"]]
                        save_submissions(df)
                        st.rerun()
    
    with t2:
        st.subheader("📦 ပစ္စည်းများ")
        items = load_items()
        with st.form("add_item"):
            col1, col2 = st.columns(2)
            new_name = col1.text_input("ပစ္စည်းအမည်")
            new_price = col2.number_input("ဈေးနှုန်း", min_value=0)
            if st.form_submit_button("➕ ထည့်") and new_name:
                items = pd.concat([items, pd.DataFrame({"item_name": [new_name], "unit_price": [new_price]})], ignore_index=True)
                save_items(items)
                st.rerun()
        for idx, row in items.iterrows():
            c1, c2, c3 = st.columns([3,2,1])
            c1.write(row["item_name"])
            c2.write(f"{row['unit_price']} ကျပ်")
            if c3.button("🗑", key=f"del_{idx}"):
                save_items(items.drop(idx))
                st.rerun()
    
    with t3:
        st.subheader("👥 Users")
        users = load_users()
        with st.form("add_user"):
            col1, col2, col3 = st.columns(3)
            u = col1.text_input("အမည်")
            loc = col2.text_input("နေရာ")
            act = col3.checkbox("Active", True)
            if st.form_submit_button("➕ ထည့်") and u:
                users = pd.concat([users, pd.DataFrame({"username": [u], "location": [loc], "active": [act]})], ignore_index=True)
                save_users(users)
                st.rerun()
        for idx, row in users.iterrows():
            c1, c2, c3, c4 = st.columns([2,2,1,1])
            c1.write(row["username"])
            c2.write(row["location"])
            new_act = c3.checkbox("Active", row["active"], key=f"act_{idx}")
            if new_act != row["active"]:
                users.loc[idx, "active"] = new_act
                save_users(users)
                st.rerun()
            if c4.button("🗑", key=f"del_u_{idx}"):
                save_users(users.drop(idx))
                st.rerun()
    
    with t4:
        st.subheader("✅ အတည်ပြုပြီးသား")
        df = load_submissions()
        approved = df[df["status"] == "approved"].copy()
        if approved.empty:
            st.info("မရှိသေးပါ")
        else:
            st.dataframe(approved)
            st.markdown(download_excel(approved), unsafe_allow_html=True)
    
    with t5:
        st.subheader("📊 အစီရင်ခံစာ")
        df = load_submissions()
        approved = df[df["status"] == "approved"].copy()
        if approved.empty:
            st.info("မရှိသေးပါ")
        else:
            approved["total_price"] = pd.to_numeric(approved["total_price"], errors='coerce').fillna(0)
            approved["quantity"] = pd.to_numeric(approved["quantity"], errors='coerce').fillna(0)
            c1, c2, c3 = st.columns(3)
            c1.metric("စုစုပေါင်းစာရင်း", len(approved))
            c2.metric("ပစ္စည်းအရေအတွက်", int(approved["quantity"].sum()))
            c3.metric("စုစုပေါင်းငွေ (ကျပ်)", f"{approved['total_price'].sum():,.0f}")
            st.bar_chart(approved.groupby("item_name")["total_price"].sum())
            st.bar_chart(approved.groupby("location")["total_price"].sum())

else:
    st.title("📝 စာရင်းသွင်းရန်")
    users = load_users()
    active = users[users["active"] == True]
    if active.empty:
        st.warning("User မရှိပါ")
    else:
        name = st.selectbox("အမည်", active["username"].tolist())
        loc = active[active["username"] == name]["location"].values[0]
        st.write(f"နေရာ: {loc}")
        items = load_items()
        if items.empty:
            st.warning("ပစ္စည်းမရှိသေးပါ")
        else:
            item = st.selectbox("ပစ္စည်း", items["item_name"].tolist())
            price = items[items["item_name"] == item]["unit_price"].values[0]
            size = st.text_input("Size")
            qty = st.number_input("အရေအတွက်", 1, step=1)
            total = price * qty
            st.info(f"စုစုပေါင်း: {total} ကျပ်")
            if st.button("📤 တင်မယ်"):
                subs = load_submissions()
                new_id = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_row = pd.DataFrame([{
                    "submission_id": new_id, "username": name, "location": loc,
                    "item_name": item, "size": size, "quantity": qty, "unit_price": price,
                    "total_price": total, "status": "pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "approved_by": "", "approved_date": ""
                }])
                save_submissions(pd.concat([subs, new_row], ignore_index=True))
                st.success("တင်ပြီးပါပြီ")
                st.balloons()
