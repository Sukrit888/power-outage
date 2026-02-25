import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Power Outage Record Counter", layout="wide")

st.title("📊 Power Outage Record Counter")
st.markdown("Analyze outage records by day and by meter number.")

FILE_NAME = "Power outage Melli.xlsx"
SHEETS = ["January", "November", "December"]

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

    for sheet in SHEETS:
        try:
            df = pd.read_excel(FILE_NAME, sheet_name=sheet)

            # Clean column names
            df.columns = df.columns.str.strip()

            required_cols = [
                "Meterno",
                "OutageDateTime",
                "RestoreDateTime"
            ]

            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing column '{col}' in sheet '{sheet}'")

            # Convert to datetime
            df["OutageDateTime"] = pd.to_datetime(df["OutageDateTime"], errors="coerce")
            df["RestoreDateTime"] = pd.to_datetime(df["RestoreDateTime"], errors="coerce")

            # Extract date
            df["OutageDate"] = df["OutageDateTime"].dt.date

            data[sheet] = df

        except Exception as e:
            st.warning(f"⚠ Could not load sheet '{sheet}': {e}")

    return data


data_dict = load_data()

if len(data_dict) == 0:
    st.error("No valid sheets loaded. Please check Excel structure.")
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

# ---------------------------------------------------
# 1️⃣ Daily Record Count
# ---------------------------------------------------
st.subheader(f"📅 Daily Record Count - {selected_month}")

daily_counts = (
    df.groupby("OutageDate")
    .size()
    .reset_index(name="Number of Records")
    .sort_values("OutageDate")
)

st.dataframe(daily_counts, use_container_width=True)

# ---------------------------------------------------
# 2️⃣ Meter-wise Record Check
# ---------------------------------------------------
st.subheader("🔍 Check Records for Specific Meter & Date")

meter_list = sorted(df["Meterno"].dropna().unique())

selected_meter = st.selectbox("Select Meter No", meter_list)

selected_date = st.date_input("Select Date")

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
