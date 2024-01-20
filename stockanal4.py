import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file, specifying to use only the first 9 columns
file_path = 'Broker-NOV-23.csv'  # Adjust the file path as needed
df = pd.read_csv(file_path, usecols=range(9))

# Convert 'Activity Date' to DateTime and 'Amount' to numeric
df['Activity Date'] = pd.to_datetime(df['Activity Date'])
df['Amount'] = df['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# Group by month and 'Instrument', then sum the 'Amount' for 'STO' and 'BTC' transactions
grouped_data = df[df['Trans Code'].isin(['STO', 'BTC'])].groupby([df['Activity Date'].dt.month, 'Instrument'])['Amount'].sum()

# Identifying the top instrument for the year
annual_top_instrument = grouped_data.groupby(level=1).sum().idxmax()

# Displaying the results including total for each month and running sum for the top instrument
running_sum = 0
for month, month_data in grouped_data.groupby(level=0):
    month_total = round(month_data.sum(), 2)
    print(f"Month: {month}, Total for Month: {month_total}")
    for instrument, amount in month_data.items():
        print(f"  Instrument: {instrument}, Total Amount: {round(amount, 2)}")
    if annual_top_instrument in month_data.index:
        running_sum += month_data[annual_top_instrument]
        print(f"  Running Sum for {annual_top_instrument}: {round(running_sum, 2)}")
    print("\n")

# Filter for 'STO' and 'BTC' transactions for the whole year
yearly_data = df[df['Trans Code'].isin(['STO', 'BTC'])]

# Group by 'Activity Date' and sum the 'Amount' for daily profits
daily_profits = yearly_data.groupby('Activity Date')['Amount'].sum()

# Calculate cumulative daily profits
cumulative_profits = daily_profits.cumsum()

# Plotting cumulative profits vs. days
plt.figure(figsize=(10, 6))
cumulative_profits.plot(kind='line')
plt.title('Cumulative Profits vs Days for the Year')
plt.xlabel('Day')
plt.ylabel('Cumulative Profits')
plt.grid(True)
plt.show()

# Group by 'Instrument' and sum the 'Amount' for total profit per instrument
total_profit_per_instrument = df.groupby('Instrument')['Amount'].sum()

# Sorting instruments by their total profit
sorted_instruments = total_profit_per_instrument.sort_values(ascending=False)

# Display sorted instruments with their total profit
print("Instruments Sorted by Total Profit:")
print(sorted_instruments)
