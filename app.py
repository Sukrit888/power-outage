import streamlit as st
import pandas as pd

st.set_page_config(page_title="Power Outage Record Counter", layout="wide")

st.title("📊 Power Outage Record Counter")
st.write("Analyze outage records by day and by meter number.")

# ---------------------------------------------------
# Load Excel File
# ---------------------------------------------------
@st.cache_data
def load_data():
    file_path = "Power outage Melli.xlsx"

    sheets = ["January", "November", "December"]
    data = {}

    for sheet in sheets:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet)

            # Standardize column names (remove extra spaces)
            df.columns = df.columns.str.strip()

            # Convert datetime columns
            df["Outage Date Time"] = pd.to_datetime(
                df["Outage Date Time"], errors="coerce"
            )
            df["Restore Date Time"] = pd.to_datetime(
                df["Restore Date Time"], errors="coerce"
            )

            # Extract Date only
            df["Outage Date"] = df["Outage Date Time"].dt.date

            data[sheet] = df

        except Exception as e:
            st.error(f"Error loading sheet {sheet}: {e}")

    return data


data_dict = load_data()

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
st.sidebar.header("🔎 Filters")

selected_month = st.sidebar.selectbox(
    "Select Month",
    ["January", "November", "December"]
)

df = data_dict[selected_month]

# ---------------------------------------------------
# 1️⃣ Daily Record Count
# ---------------------------------------------------
st.subheader(f"📅 Daily Record Count - {selected_month}")

daily_counts = (
    df.groupby("Outage Date")
      .size()
      .reset_index(name="Number of Records")
      .sort_values("Outage Date")
)

st.dataframe(daily_counts, use_container_width=True)

# ---------------------------------------------------
# 2️⃣ Meter-wise Record Check
# ---------------------------------------------------
st.subheader("🔍 Check Records for Specific Meter & Date")

meter_list = df["Meter No"].dropna().unique()

selected_meter = st.selectbox("Select Meter No", meter_list)

selected_date = st.date_input("Select Date")

if st.button("Check Records"):

    filtered_df = df[
        (df["Meter No"] == selected_meter) &
        (df["Outage Date"] == selected_date)
    ]

    record_count = len(filtered_df)

    st.success(
        f"""
        Meter No: {selected_meter}  
        Date: {selected_date}  
        Number of Records: {record_count}
        """
    )

    if record_count > 0:
        st.write("### Matching Records")
        st.dataframe(filtered_df, use_container_width=True)
