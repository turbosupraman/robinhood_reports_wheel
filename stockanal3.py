import pandas as pd

# Load the CSV file, specifying to use only the first 9 columns
file_path = 'Broker-NOV-23.csv'  # Adjust the file path as needed
df = pd.read_csv(file_path, usecols=range(9))

# Convert 'Activity Date' to DateTime and 'Amount' to numeric
df['Activity Date'] = pd.to_datetime(df['Activity Date'])
df['Amount'] = df['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# Group by month and 'Instrument', then sum the 'Amount' for 'STO' and 'BTC' transactions
grouped_data = df[df['Trans Code'].isin(['STO', 'BTC'])].groupby([df['Activity Date'].dt.month, 'Instrument'])['Amount'].sum()

# Display the results including total for each month, formatted with two decimal places
for month, month_data in grouped_data.groupby(level=0):
    month_total = round(month_data.sum(), 2)
    print(f"Month: {month}, Total for Month: {month_total}")
    for instrument, amount in month_data.items():
        print(f"  Instrument: {instrument}, Total Amount: {round(amount, 2)}")
    print("\n")
