import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import io

st.set_page_config(page_title="Power Outage Matrix Generator", layout="wide")

st.title("⚡ Power Outage Monthly Matrix Generator")

# Month configuration
MONTH_CONFIG = {
    "November 2025": (2025, 11),
    "December 2025": (2025, 12),
    "January 2026": (2026, 1),
}

uploaded_file = st.file_uploader("Upload Power outage Excel file", type=["xlsx"])

if uploaded_file:

    selected_month = st.selectbox("Select Month", list(MONTH_CONFIG.keys()))
    year, month = MONTH_CONFIG[selected_month]

    if st.button("Generate Output Matrix"):

        with st.spinner("Processing..."):

            # Read only selected sheet
            sheet_name = selected_month.split()[0]  # November / December / January
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

            df.columns = df.columns.str.strip()

            # Convert datetime
            df["OutageDateTime"] = pd.to_datetime(df["OutageDateTime"], errors="coerce")
            df["OutageDate"] = df["OutageDateTime"].dt.date

            # Filter correct month/year
            df = df[
                (df["OutageDateTime"].dt.year == year) &
                (df["OutageDateTime"].dt.month == month)
            ]

            # FAST pivot (vectorized)
            pivot_df = (
                df.groupby(["Meterno", "OutageDate"])
                .size()
                .unstack(fill_value=0)
            )

            # Ensure all dates exist as columns
            num_days = calendar.monthrange(year, month)[1]
            all_dates = [datetime(year, month, d).date() for d in range(1, num_days + 1)]
            pivot_df = pivot_df.reindex(columns=all_dates, fill_value=0)

            pivot_df.index.name = "Meterno"

        st.success("Matrix Generated Successfully!")

        st.dataframe(pivot_df, use_container_width=True)

        # Prepare Excel for download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pivot_df.to_excel(writer, sheet_name="OUTPUT")

        st.download_button(
            label="📥 Download Excel Output",
            data=output.getvalue(),
            file_name=f"OUTPUT_{selected_month.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
