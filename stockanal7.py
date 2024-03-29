
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file, specifying to use only the first 9 columns
file_path = 'alltimebroker2023.csv'  # Adjust the file path as needed
df = pd.read_csv(file_path, usecols=range(9))

# Convert 'Activity Date' to DateTime and 'Amount' to numeric
df['Activity Date'] = pd.to_datetime(df['Activity Date'])
df['Amount'] = df['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)


# Group by year, month, and 'Instrument', then sum the 'Amount' for 'STO' and 'BTC' transactions
#grouped_data = df[df['Trans Code'].isin(['STO', 'BTC'])].groupby([df['Activity Date'].dt.year, df['Activity Date'].dt.month, 'Instrument'])['Amount'].sum()

# Group by year, month, and 'Instrument', then sum the 'Amount' for 'STO', 'BTC' and CDIV transactions
grouped_data = df[df['Trans Code'].isin(['STO', 'BTC', 'CDIV'])].groupby([df['Activity Date'].dt.year, df['Activity Date'].dt.month, 'Instrument'])['Amount'].sum()


# annual_top_instrument = grouped_data.groupby(level=1).sum().idxmax()
# Identifying the top instrument for each year and month
annual_top_instrument = grouped_data.groupby(level=[0, 1, 2]).sum().idxmax()

# Displaying the results including total for each month and sorted instruments by profits
for (year, month), month_data in grouped_data.groupby(level=[0, 1]):
    month_total = round(month_data.sum(), 2)
    print(f"Year: {year}, Month: {month}, Total for Month: {month_total}")

    # Sort the instruments for this month by their profit
    sorted_month_data = month_data.sort_values(ascending=False)

    # Display all instruments and their amounts for this month
    for instrument, amount in sorted_month_data.items():
        print(f"  Instrument: {instrument}, Total Amount: {round(amount, 2)}")

    print("\n")

# Filter for 'STO' and 'BTC' transactions for the whole year
yearly_data = df[df['Trans Code'].isin(['STO', 'BTC', 'CDIV'])]


# Group by 'Activity Date' and sum the 'Amount' for daily profits
daily_profits = yearly_data.groupby('Activity Date')['Amount'].sum()

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
print(sorted_instruments.to_string()) # JD

print('/n/n')
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



# Applying the conversion function to the 'Amount' column
df['Amount Cleaned'] = df['Amount'].apply(convert_amount)

# Convert 'Quantity' column to numeric (assuming it's currently a string)
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')

# Filtering for only 'Buy' and 'Sell' transactions
df_buy_sell = df[df['Trans Code'].isin(['Buy', 'Sell'])]

# Adjusting quantity based on transaction type
df_buy_sell['Adjusted Quantity'] = df_buy_sell.apply(lambda row: row['Quantity'] if row['Trans Code'] == 'Buy' else -row['Quantity'], axis=1)

# Grouping by 'Instrument' and summing the 'Adjusted Quantity' column
total_quantity_by_instrument = df_buy_sell.groupby('Instrument')['Adjusted Quantity'].sum().round()

# Remove entries with zero quantity
non_zero_quantities = total_quantity_by_instrument[total_quantity_by_instrument != 0]

# Filter out stocks with positive quantity (stocks you own)
stocks_sold_or_none_owned = df_buy_sell.groupby('Instrument').filter(lambda x: x['Adjusted Quantity'].sum() <= 0)

# Summing the total amount for stocks sold or none owned, and rounding to two decimal places
total_amount = stocks_sold_or_none_owned['Amount Cleaned'].sum().round(2)

# Display the total quantity owned for each instrument, excluding zero quantities
print("Total Quantity Owned by Instrument (Excluding Zero Quantities):")
print(non_zero_quantities.to_string())

# Display the total amount (profit or loss) for stocks sold or none owned, rounded to two decimal places
print("\nTotal Amount (Profit/Loss) for Stocks Sold or None Owned:")
print(total_amount)
