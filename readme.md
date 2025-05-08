# EMI Calculator

A sophisticated Loan EMI (Equated Monthly Installment) calculator built with Python and PyQt5, featuring an interactive GUI and dynamic visualizations.

## Features

- Modern dark-themed user interface
- Real-time EMI calculations
- Interactive graphs and visualizations
- Lump-sum prepayment analysis
- Comprehensive payment breakdown

## Dependencies

- Python 3.x
- PyQt5
- Matplotlib
- NumPy

## Installation

```bash
pip install PyQt5 matplotlib numpy
```

## Usage

Run the application using:

```bash
python pyLoan.py
```

## Calculator Components

### Input Parameters

1. **Loan Parameters**
   - Downpayment (₹)
   - Total Loan Amount (₹)
   - Interest Rate (% per annum)
   - Tenure (years)

2. **Optional Prepayment**
   - Lump sum amount (₹)
   - Year of payment

### Output Information

- Principal amount after downpayment
- Monthly EMI amount
- Total payment over loan tenure
- Total interest payable
- Interest to Principal ratio
- Revised EMI details after lump-sum payment (if applicable)

### Visualizations

The application provides three types of graphs:
1. Payment Breakdown Pie Chart
2. Outstanding Principal Over Time
3. EMI Components Over Time (Principal vs Interest)

## Technical Details

### Key Functions

1. `calculate_emi(principal, annual_rate, tenure_years)`
   - Calculates the monthly EMI using the formula:
   ```
   EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
   ```
   Where:
   - P = Principal amount
   - r = Monthly interest rate (annual rate/12/100)
   - n = Total number of months

2. `calculate_outstanding_principal(principal, annual_rate, tenure_years, paid_months)`
   - Calculates the remaining principal amount after a specific number of months

3. `calculate_new_emi_after_lump(principal, annual_rate, tenure_years, lump_sum, nth_year)`
   - Recalculates EMI after a lump-sum payment in a specific year

### GUI Components

- Built using PyQt5
- Dark theme implementation
- Tabbed interface for calculator and graphs
- Real-time validation of input values
- Interactive matplotlib graphs

## Error Handling

- Input validation for all numerical fields
- Proper error messages for invalid inputs
- Boundary checking for loan calculations

## Data Visualization

The application provides three main visualizations:
1. **Payment Breakdown**: Pie chart showing the distribution between principal and interest
2. **Outstanding Principal**: Line graph showing the decrease in principal over time
3. **EMI Components**: Stacked area chart showing the proportion of principal and interest in each EMI payment

