import pandas as pd

# Load the CSV file, specifying to use only the first 9 columns
file_path = 'Broker-NOV-23.csv'  # Adjust the file path as needed
df = pd.read_csv(file_path, usecols=range(9))

# Convert 'Activity Date' to DateTime
df['Activity Date'] = pd.to_datetime(df['Activity Date'])

# Convert 'Amount' to numeric, removing currency symbols and handling negative amounts
df['Amount'] = df['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# Check if 'BTC' amounts are already negative, if not, negate them
df['Net Amount'] = df.apply(lambda row: -row['Amount'] if row['Trans Code'] == 'BTC' and row['Amount'] > 0 else row['Amount'], axis=1)

# Filter for 'STO' and 'BTC', group by month, and sum the 'Net Amount'
monthly_totals = df[df['Trans Code'].isin(['STO', 'BTC'])].groupby(df['Activity Date'].dt.month)['Net Amount'].sum()

print(monthly_totals)
