import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Blood Bank", page_icon="🩸", layout="wide")

DATA_FILE = "blood_donors.csv"

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Name", "Blood", "Age", "Contact", "Last Donation"])
        df.to_csv(DATA_FILE, index=False)
        return df

# Save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Original data (important for filters reset)
original_df = load_data()
df = original_df.copy()

st.title("🩸 Blood Bank Management System")

# ================= SIDEBAR (INPUT + FILTERS) =================
st.sidebar.header("➕ Add Donor")

name = st.sidebar.text_input("Name")
blood = st.sidebar.selectbox("Blood Group", ["A+","A-","B+","B-","O+","O-","AB+","AB-"])
age = st.sidebar.number_input("Age", min_value=18, max_value=65)
contact = st.sidebar.text_input("Contact")
date = st.sidebar.date_input("Last Donation")

if st.sidebar.button("Add Donor"):
    if name.strip() == "" or contact.strip() == "":
        st.warning("Please fill all fields")
    else:
        diff = (datetime.today().date() - date).days

        if diff < 90:
            st.warning("Donor not eligible (must wait 90 days)")
        else:
            new = pd.DataFrame([[name, blood, age, contact, str(date)]],
                               columns=df.columns)
            df = pd.concat([original_df, new], ignore_index=True)
            save_data(df)
            st.success("Donor added successfully")

# ================= FILTER SECTION =================
st.sidebar.header("🔍 Filters")

search = st.sidebar.text_input("Search (Name / Blood Group)")

blood_filter = st.sidebar.multiselect(
    "Blood Group Filter",
    options=sorted(original_df["Blood"].dropna().unique()),
    default=[]
)

age_range = st.sidebar.slider(
    "Age Range",
    18, 65, (18, 65)
)

# Apply filters
filtered_df = original_df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
    ]

if blood_filter:
    filtered_df = filtered_df[filtered_df["Blood"].isin(blood_filter)]

filtered_df = filtered_df[
    (filtered_df["Age"] >= age_range[0]) &
    (filtered_df["Age"] <= age_range[1])
]

# ================= DISPLAY =================
st.subheader("📋 Donor List")

st.dataframe(filtered_df, use_container_width=True)

# ================= STATS =================
st.subheader("📊 Statistics")

col1, col2 = st.columns(2)

col1.metric("Total Donors", len(filtered_df))
col2.metric("Unique Blood Groups", filtered_df["Blood"].nunique())

if not filtered_df.empty:
    st.bar_chart(filtered_df["Blood"].value_counts())

# ================= DELETE =================
st.subheader("🗑 Delete Donor")

if not filtered_df.empty:
    del_name = st.selectbox("Select Donor", filtered_df["Name"])

    if st.button("Delete"):
        original_df = original_df[original_df["Name"] != del_name]
        save_data(original_df)
        st.success("Deleted successfully")
        #python -m streamlit run "d:/OneDrive/Documents/Blood Bank Managment.py"
        #  