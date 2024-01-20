import pandas as pd

# Load the CSV file, specifying to use only the first 9 columns
file_path = 'Broker-NOV-23.csv'  # Adjust the file path as needed
df = pd.read_csv(file_path, usecols=range(9))

# Convert 'Activity Date' to DateTime and 'Amount' to numeric
df['Activity Date'] = pd.to_datetime(df['Activity Date'])
df['Amount'] = df['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# Filter for 'STO' and 'BTC' transactions
filtered_df = df[df['Trans Code'].isin(['STO', 'BTC'])]

# Group by month, 'Instrument', and 'Trans Code', then sum the 'Amount'
grouped_data = filtered_df.groupby([df['Activity Date'].dt.month, 'Instrument', 'Trans Code'])['Amount'].sum()

# Preparing to display the results in a structured format
output = {}
for month, month_data in grouped_data.groupby(level=0):
    print(f"Month: {month}")
    for instrument, instrument_data in month_data.groupby(level=1):
        print(f"  Instrument: {instrument}")
        for trans_code, amount in instrument_data.items():
            print(f"    {trans_code}: {amount}")
    print("\n")
