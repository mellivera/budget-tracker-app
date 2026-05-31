import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Settings
st.set_page_config(page_title="Budget Tracker", layout="centered")

# 2. Apple Style CSS
st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; }
    div[data-testid="stMetric"] { background-color: #ffffff !important; border-radius: 12px; padding: 15px; border: 1px solid #d1d1d6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #007AFF; color: white; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

st.title("Budget Tracker")

# 3. Connection (Replace with your URL)
URL = "https://docs.google.com/spreadsheets/d/1auQGBXjyMlym_KPrRo1CTTC1UDebQzA2eMtE9tovNSs/edit?gid=0#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=URL, worksheet="Sheet1", ttl="0")
    df = df.dropna(how="all")
except Exception as e:
    st.error("❌ Google says:")
    st.code(e)  # This will show the actual technical error
    st.stop()

# 4. Dashboard
if not df.empty:
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
    spent = df[df["Type"] == "Expense"]["Amount"].sum()
    income = df[df["Type"] == "Income"]["Amount"].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Balance", f"${income - spent:,.2f}")
    col2.metric("Spent", f"${spent:,.2f}")

# 5. Form
with st.form("add_form", clear_on_submit=True):
    amt = st.number_input("Amount", min_value=0.0, step=1.0)
    cat = st.selectbox("Category", ["Food", "Transport", "Fun", "Rent", "Salary"])
    t_type = st.radio("Type", ["Expense", "Income"], horizontal=True)
    
    if st.form_submit_button("Save to Cloud"):
        new_row = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Category": cat, "Amount": amt, "Type": t_type, "Status": "Confirmed"}])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=URL, worksheet="Sheet1", data=updated_df)
        st.success("Saved!")
        st.rerun()

# 6. History
if not df.empty:
    st.write("### History")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True, hide_index=True)
