import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Power Outage Record Counter", layout="wide")

st.title("📊 Power Outage Record Counter")

FILE_NAME = "Power outage Melli.xlsx"
SHEETS = {
    "November": 2025,
    "December": 2025,
    "January": 2026
}

# ---------------------------------------------------
# Check file exists
# ---------------------------------------------------
if not os.path.exists(FILE_NAME):
    st.error(f"❌ File not found: {FILE_NAME}")
    st.stop()

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
@st.cache_data
def load_data():
    data = {}

    for sheet, year in SHEETS.items():
        try:
            df = pd.read_excel(FILE_NAME, sheet_name=sheet)
            df.columns = df.columns.str.strip()

            required_cols = ["Meterno", "OutageDateTime", "RestoreDateTime"]
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing column '{col}' in sheet '{sheet}'")

            df["OutageDateTime"] = pd.to_datetime(df["OutageDateTime"], errors="coerce")
            df["RestoreDateTime"] = pd.to_datetime(df["RestoreDateTime"], errors="coerce")

            df["OutageDate"] = df["OutageDateTime"].dt.date

            data[sheet] = df

        except Exception as e:
            st.warning(f"⚠ Could not load sheet '{sheet}': {e}")

    return data


data_dict = load_data()

if len(data_dict) == 0:
    st.error("No valid sheets loaded.")
    st.stop()

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
st.sidebar.header("🔎 Filters")

selected_month = st.sidebar.selectbox(
    "Select Month",
    list(data_dict.keys())
)

df = data_dict[selected_month]
year = SHEETS[selected_month]

# ---------------------------------------------------
# Daily Record Count
# ---------------------------------------------------
st.subheader(f"📅 Daily Record Count - {selected_month} {year}")

daily_counts = (
    df.groupby("OutageDate")
    .size()
    .reset_index(name="Number of Records")
    .sort_values("OutageDate")
)

st.dataframe(daily_counts, use_container_width=True)

# ---------------------------------------------------
# Meter-wise Record Check
# ---------------------------------------------------
st.subheader("🔍 Check Records for Specific Meter & Date")

meter_list = sorted(df["Meterno"].dropna().unique())
selected_meter = st.selectbox("Select Meter No", meter_list)

# Generate valid date range for selected month
if selected_month == "November":
    min_date = date(2025, 11, 1)
    max_date = date(2025, 11, 30)
elif selected_month == "December":
    min_date = date(2025, 12, 1)
    max_date = date(2025, 12, 31)
else:  # January
    min_date = date(2026, 1, 1)
    max_date = date(2026, 1, 31)

selected_date = st.date_input(
    "Select Date",
    min_value=min_date,
    max_value=max_date,
    value=min_date
)

if st.button("Check Records"):

    filtered_df = df[
        (df["Meterno"] == selected_meter) &
        (df["OutageDate"] == selected_date)
    ]

    record_count = len(filtered_df)

    st.success(
        f"""
        📌 Meter No: {selected_meter}  
        📅 Date: {selected_date}  
        🔢 Number of Records: {record_count}
        """
    )

    if record_count > 0:
        st.write("### Matching Records")
        st.dataframe(filtered_df, use_container_width=True)
