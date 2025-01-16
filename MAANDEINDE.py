import pandas as pd
import streamlit as st
import io

# List to hold filenames of files that cause errors
error_files = []


# Function to process individual files
def file_processor(uploaded_file):
    try:
        # Read the entire file with the correct delimiter
        df = pd.read_csv(uploaded_file, sep=';', header=None, encoding='ISO-8859-1', engine='python')
        expected_columns = [1, 2, 5, 7, 17]

        # Check if these columns exist in the dataframe
        if len(df.columns) < 18:
            error_files.append(uploaded_file.name)
            st.error(f"{uploaded_file.name} doesn't have enough columns.")
            return None

        # Select only the relevant columns if they exist
        df = df.iloc[:, expected_columns]

        # Rename columns (adjust according to data example)
        df.columns = ['DATE', 'ACCOUNT NUMBER', 'CREDITOR NAME', 'AMOUNT', 'BATCH NAME']

        # Clean up data (e.g., remove extra spaces, convert amounts)
        df['ACCOUNT NUMBER'] = df['ACCOUNT NUMBER'].str.strip()  # Remove any leading/trailing spaces
        df['ACCOUNT NUMBER'] = df['ACCOUNT NUMBER'].apply(lambda x: x.lstrip('0') if isinstance(x, str) else x)  # Remove leading zeros
        df['CREDITOR NAME'] = df['CREDITOR NAME'].str.strip()

        # Fix the date column

        # Fix the date column
        df = date_fixer(df)

        # Convert the 'AMOUNT' column to integer (after removing any extra characters, like spaces)
        df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce') / 100  # Handle invalid values gracefully
        df = df.iloc[1:-2]
        # Return the cleaned dataframe
        return df

    except pd.errors.EmptyDataError:
        # Handle empty files separately
        error_files.append(uploaded_file.name)
        st.error(f"{uploaded_file.name} is empty or doesn't contain valid data.")
        return None
    except Exception as e:
        # Handle other errors
        error_files.append(uploaded_file.name)
        st.error(f"Error reading {uploaded_file.name}: {e}")
        return None


# Function to fix the date column
def date_fixer(df):
    # Handle date format (assuming the first row has the date, or adjust as needed)
    date = df.iloc[0, 0]  # Get the date from the first row
    df['DATE'] = date
    df['DATE'] = pd.to_datetime(df['DATE'].astype(str), format='%Y%m%d')

    # Change the format to dd/mm/yyyy
    df['DATE'] = df['DATE'].dt.strftime('%d/%m/%Y')

    return df


# List to hold file paths
path_names = []

# Title for the app
st.markdown(
        """
        <div style="background-color: #f9f9f9; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <h3 style="color: #333;">Instructions</h3>
            <ul>
                <li>THIS IS THE BANK BATCH CONVERTER for STANDARD BANK.</li>
                <li>Upload the required files:
                    <ul>
                        <li>Upload the files exported from STD BANK, leave them as is.</li>
                        <li>tip: save all these files to a dedicated exports folder -> CTRL + A(to select all)-> Click Open.</li>
                    </ul>
                </li>
                <li>Click the "Go" button to process the files.</li>
                <li>Download the processed file using the provided download button.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(f"<h2 style='color: orange; font-weight: bold;'>BANK BATCH CONVERTER</h2>", unsafe_allow_html=True)


# File uploader widget for multiple files
uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True)

# If files are uploaded, process them
if uploaded_files:
    # Create an empty list to hold processed dataframes
    processed_dfs = []

    # Process each uploaded file
    for uploaded_file in uploaded_files:
        # Add file name to path_names list
        path_names.append(uploaded_file.name)

        # Process the file and get the dataframe
        df = file_processor(uploaded_file)

        # If the file failed to process, skip it
        if df is None:
            continue

        # Append the processed dataframe to the list
        processed_dfs.append(df)

    # Concatenate all dataframes into one
    if processed_dfs:
        final_df = pd.concat(processed_dfs, ignore_index=True)

        # Show the concatenated dataframe (this is the preview for the final file)
        st.write("Final Preview:")
        st.write(final_df)

        # Save the final concatenated dataframe to an Excel file
        final_df.to_excel("processed_files.xlsx", index=False)

        # Provide the user with a download button for the Excel file
        with open("processed_files.xlsx", "rb") as f:
            st.download_button("Download Processed Excel File", f, file_name="processed_files.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Display error files, if any
        if error_files:
            st.write("The following files caused errors and were skipped:")
            st.write(error_files)

    else:
        st.write("No files processed successfully.")
else:
    st.write("Please upload some files.")
