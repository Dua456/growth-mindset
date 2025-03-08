import streamlit as st
import pandas as pd
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="File Converter", layout="wide")
st.title("File Converter & Cleaner")
st.write("Upload CSV or Excel files, clean data, and convert formats.")

def load_file(file):
    """Load CSV or Excel file into a DataFrame."""
    ext = file.name.split('.')[-1].lower()
    if ext == "csv":
        return pd.read_csv(file)
    elif ext == "xlsx":
        return pd.read_excel(file)
    else:
        st.error("Unsupported file type!")
        return None

# Upload files
files = st.file_uploader("Upload CSV or Excel Files.", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        st.markdown(f"## {file.name}")
        df = load_file(file)
        if df is None:
            continue

        # Preview data inside an expander for better UI
        with st.expander("Preview Data"):
            st.dataframe(df.head())

        # Option to remove duplicates
        if st.checkbox(f"Remove Duplicates - {file.name}"):
            df = df.drop_duplicates()
            st.success("Duplicates removed!")
            st.dataframe(df.head())

        # Option to fill missing numeric values with the mean
        if st.checkbox(f"Fill Missing Numeric Values with Mean - {file.name}"):
            df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
            st.success("Missing numeric values filled with mean.")
            st.dataframe(df.head())

        # Option to clean extra whitespace in column names and string columns
        if st.checkbox(f"Clean Whitespace in Data - {file.name}"):
            # Clean column names
            df.columns = df.columns.str.strip()
            # Clean string-type columns
            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = df[col].str.strip()
            st.success("Whitespace cleaned from column names and string columns.")
            st.dataframe(df.head())

        # Option to select specific columns to keep
        selected_columns = st.multiselect(
            f"Select Columns to Include - {file.name}",
            options=df.columns,
            default=list(df.columns)
        )
        if selected_columns:
            df = df[selected_columns]
            st.dataframe(df.head())

        # Show a chart if numeric columns exist
        numeric_cols = df.select_dtypes(include="number")
        if not numeric_cols.empty and st.checkbox(f"Show Chart (first 2 numeric columns) - {file.name}"):
            st.bar_chart(numeric_cols.iloc[:, :2])

        # Choose output format and prepare file for download
        format_choice = st.radio(f"Convert {file.name} to:", options=["CSV", "Excel"], key=file.name)
        output = BytesIO()
        if format_choice == "CSV":
            df.to_csv(output, index=False)
            mime = "text/csv"
            new_name = file.name.rsplit('.', 1)[0] + ".csv"
        else:
            df.to_excel(output, index=False, engine="openpyxl")
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            new_name = file.name.rsplit('.', 1)[0] + ".xlsx"
        
        output.seek(0)
        st.download_button("Download Processed File", file_name=new_name, data=output, mime=mime)
        st.success("Processing complete!")
