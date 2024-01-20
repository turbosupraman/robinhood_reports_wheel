import pandas as pd
from tabulate import tabulate

# Load the CSV file into a DataFrame
file_path = 'Broker-NOV-23.csv'

# Define the starting cash amount
starting_cash = 80000  # Replace this with your actual starting cash amount

# Read the CSV file, skipping bad lines
data = pd.read_csv(file_path, on_bad_lines='skip')

# Convert 'Activity Date' to datetime format
data['Activity Date'] = pd.to_datetime(data['Activity Date'])

# Clean the 'Amount' column by removing dollar signs and parentheses, and converting to float
data['Amount'] = data['Amount'].replace('[\$,()]', '', regex=True).astype(float) * \
                 data['Amount'].str.contains('\(').map({True: -1, False: 1})

# Clean out everything after "/" in the 'Description' column
#data['Description'] = data['Description'].str.split('/', expand=True)[0]
#data['Description'] = data['Description'].str.split('\\\\', expand=True)[0]
data['Description'] = data['Description'].str.split('\n', expand=True)[0]



# Convert 'Quantity' to numeric, setting errors to 'coerce' which will turn non-numeric values to NaN
data['Quantity'] = pd.to_numeric(data['Quantity'], errors='coerce')

# Fill NaNs in 'Price' with zeros after removing any dollar signs and converting to float
data['Price'] = data['Price'].replace('[\$,]', '', regex=True).astype(float).fillna(0)

# Identify option assignment transactions
option_assignments = data[data['Description'].str.contains("Option Assigned", na=False)].copy()
option_assignments['Stock Impact'] = option_assignments['Quantity'] * option_assignments['Price']

'''
# Update the transaction codes with descriptions
data['Trans Code'] = data['Trans Code'].map({
    'STO': 'Sell To Open',
    'BTC': 'Buy To Close',
    'OASGN': 'Option Assignment',
    'XENT_RWR': 'Roundup/Transfer',
    'XENT': 'Transfer',
    'ACH': 'Deposit'
}, na_action='ignore')


# Recalculate the monthly summaries
monthly_cash_movements = data.groupby(data['Activity Date'].dt.to_period('M'))['Amount'].sum()
monthly_option_profits = data[data['Trans Code'].isin(['Sell To Open', 'Buy To Close'])].groupby(data['Activity Date'].dt.to_period('M'))['Amount'].sum()
'''

# Recalculate the monthly summaries
monthly_cash_movements = data.groupby(data['Activity Date'].dt.to_period('M'))['Amount'].sum()
monthly_option_profits = data[data['Trans Code'].isin(['STO', 'BTC'])].groupby(data['Activity Date'].dt.to_period('M'))['Amount'].sum()


monthly_stock_impact = option_assignments.groupby(option_assignments['Activity Date'].dt.to_period('M'))['Stock Impact'].sum()

# Combine the summaries into a single DataFrame
monthly_summary = pd.DataFrame({
    'Monthly Cash Movements': monthly_cash_movements,
    'Monthly Option Profits': monthly_option_profits,
    'Monthly Stock Impact': monthly_stock_impact
}).fillna(0)  # Fill NaN with 0 where there are no transactions of a type in a month

# Add the starting cash amount to the cumulative cash balance
monthly_summary['Cumulative Cash Balance'] = monthly_summary['Monthly Cash Movements'].cumsum()
monthly_summary['Cumulative Stock Impact'] = monthly_summary['Monthly Stock Impact'].cumsum()

# Add a row for the starting balance before the first activity date
if not monthly_summary.empty:
    # Convert starting_month to Period (the same type as the DataFrame index)
    starting_month = (monthly_summary.index.min() - 1).to_timestamp()
    starting_month = pd.Period(starting_month, freq='M')
    starting_row = pd.DataFrame({
        'Monthly Cash Movements': [0],
        'Monthly Option Profits': [0],
        'Monthly Stock Impact': [0],
        'Cumulative Cash Balance': [starting_cash],
        'Cumulative Stock Impact': [0]
    }, index=[starting_month])

    monthly_summary = pd.concat([starting_row, monthly_summary])

# Sort the summary by date
monthly_summary = monthly_summary.sort_index()

# Round the numeric columns to two decimal places
monthly_summary_rounded = monthly_summary.round(2)

# Abbreviate column names
monthly_summary_rounded.columns = ['Mon Cash Mov', 'Mon Opt Profits', 'Mon Stock Impact', 'Cum Cash Bal', 'Cum Stock Impact']

# all months for the year
total_sum_all_months = monthly_option_profits.sum()

print(data.to_string())

# Print the monthly summary in a more compact tabular format
print(tabulate(monthly_summary_rounded, headers='keys', tablefmt='plain', floatfmt=".2f"))

print('Total option profits for the year',total_sum_all_months)

