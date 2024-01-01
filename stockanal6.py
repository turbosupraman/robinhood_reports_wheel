# this version works but groups the years together, I need to keep the year seperated



import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file, specifying to use only the first 9 columns
file_path = 'alltimebroker2023.csv'  # Adjust the file path as needed
df = pd.read_csv(file_path, usecols=range(9))

# Convert 'Activity Date' to DateTime and 'Amount' to numeric
df['Activity Date'] = pd.to_datetime(df['Activity Date'])
df['Amount'] = df['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# Group by month and 'Instrument', then sum the 'Amount' for 'STO' and 'BTC' transactions
grouped_data = df[df['Trans Code'].isin(['STO', 'BTC'])].groupby([df['Activity Date'].dt.month, 'Instrument'])['Amount'].sum()

# Assuming df is your DataFrame

# # Group by 'Instrument' and aggregate based on 'Trans Code'
# aggregated_df = df.groupby('Instrument').apply(
#     lambda x: x[x['Trans Code'] == 'BUY']['Amount'].sum() -
#               x[x['Trans Code'] == 'SELL']['Amount'].sum()
# ).reset_index(name='Net Amount')
#
# # Sort the DataFrame by the aggregated 'Net Amount'
# sorted_df = aggregated_df.sort_values(by='Net Amount', ascending=False)
#
# # Display the sorted DataFrame
# print(sorted_df)
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

# Calculate the 7-day moving average of daily profits
weekly_avg_profits = daily_profits.rolling(window=30).mean()

# Plotting cumulative and weekly average profits
plt.figure(figsize=(12, 10))

# Cumulative Profits Plot
plt.subplot(2, 1, 1)  # Two rows, one column, first subplot
cumulative_profits.plot(kind='line')
plt.title('Cumulative Profits Over Time')
plt.xlabel('Day')
plt.ylabel('Cumulative Profits')
plt.grid(True)

# 7-Day Moving Average of Profits Plot
plt.subplot(2, 1, 2)  # Two rows, one column, second subplot
weekly_avg_profits.plot(kind='line')
plt.title('7-Day Moving Average of Daily Profits')
plt.xlabel('Day')
plt.ylabel('Average Daily Profit')
plt.grid(True)

plt.tight_layout()
plt.show()

# Group by 'Instrument' and sum the 'Amount' for total profit per instrument
total_profit_per_instrument = df.groupby('Instrument')['Amount'].sum()

# Sorting instruments by their total profit
sorted_instruments = total_profit_per_instrument.sort_values(ascending=False)

# Display sorted instruments with their total profit
print("Instruments Sorted by Total Profit:")
print(sorted_instruments)

print(f"Total profits{cumulative_profits[-5:]}")


# Defining a function to clean and convert the 'Amount' column values
def convert_amount(value):
    # Check if the value is a string
    if isinstance(value, str):
        # Remove dollar signs and commas from the string
        value = value.replace('$', '').replace(',', '')
        # Convert to float; if value is enclosed in parentheses, make it negative
        return -float(value[1:-1]) if '(' in value else float(value)
    # Return the value as is if it's not a string
    return value

# Apply the conversion function to each value in the 'Amount' column
df['Amount Cleaned'] = df['Amount'].apply(convert_amount)

# Filter the DataFrame to include only rows where 'Trans Code' is 'Buy' or 'Sell'
df_buy_sell = df[df['Trans Code'].isin(['Buy', 'Sell'])]

# Group by 'Instrument' and sum the 'Amount Cleaned' column for each group
total_amount_buy_sell_by_instrument = df_buy_sell.groupby('Instrument')['Amount Cleaned'].sum()

# Print the summed amounts for each instrument
print(total_amount_buy_sell_by_instrument)