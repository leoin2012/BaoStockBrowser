# 📈 BaoStock Data Browser

A comprehensive web-based tool for querying BaoStock API data with an intuitive interface.

## Features

- **🎯 Smart Stock Selector**:
  - Dropdown list showing all queryable stocks (code + name)
  - Support keyword search for quick stock location
  - One-click refresh button (🔄) to update stock list
  - Auto-cache to local CSV file, no need to reload every time
  - First-time use automatically fetches complete stock list from API
- **📖 Field Description Tooltips**:
  - All query result table fields have detailed Chinese descriptions
  - Hover over column names to view detailed field descriptions
  - Click "View Field Descriptions" to expand and view all field meanings
  - Includes field descriptions, calculation formulas, units, and other detailed information
  - Field definitions saved in local CSV file (field_descriptions.csv)
  - Support custom extension of field descriptions
- **💾 Industry Data Management**:
  - Query industry classification for all stocks
  - One-click save industry data to local stock_list.csv
  - Auto-merge and update industry fields (industry, industryClassification)
  - Support incremental updates without affecting existing data
- **K-Line Data**: Query historical stock K-line data (daily, weekly, monthly, and minute-level)
- **Dividend & Adjustment**: Get dividend information and adjustment factors
- **Financial Data**: Query quarterly financial statements including:  - Profitability metrics
  - Operating capability
  - Growth ability
  - Debt repayment ability
  - Cash flow
  - DuPont analysis
- **Company Reports**: Performance express reports and forecast reports
- **Security Information**: Trading dates, stock codes, and basic stock information
- **Macro Economy**: Interest rates, reserve ratios, money supply, and SHIBOR data
- **Sector Data**: Industry classification and index constituent stocks (SSE 50, CSI 300, CSI 500)

## Installation

1. Clone this repository or download the files
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Windows)

Simply double-click the `run.bat` file to launch the application. The script will:
- Check if Python is installed
- Automatically install dependencies if needed
- Start the Streamlit server
- Open the application in your default browser

### Manual Start

Alternatively, run the application with Streamlit:

```bash
streamlit run baostock_browser.py
```

The application will open in your default web browser at `http://localhost:8501`

**Note**: Press `Ctrl+C` in the terminal to stop the server

## How to Use

1. **Select API Category**: Choose from the sidebar on the left
2. **Configure Parameters**: Enter required parameters in the left panel
   - Default values are provided for quick testing
   - All parameters can be customized as needed
3. **Execute Query**: Click the "Execute Query" button
4. **View Results**: Results will be displayed in the right panel
5. **Download Data**: Use the "Download CSV" button to export results

## Default Parameters

The tool provides sensible default values for all parameters:

- **Stock Code**: sh.600000 (Pudong Development Bank)
- **Date Range**: Last 30 days (for most queries)
- **Frequency**: Daily (for K-line data)
- **Adjust Flag**: No adjustment (3)

Simply click "Execute Query" to get data immediately, then modify parameters as needed.

## API Categories

### 1. K-Line Data
- `query_history_k_data_plus`: Historical K-line data with multiple frequencies

### 2. Dividend & Adjustment
- `query_dividend_data`: Dividend information
- `query_adjust_factor`: Adjustment factors

### 3. Financial Data
- `query_profit_data`: Quarterly profitability
- `query_operation_data`: Quarterly operating capability
- `query_growth_data`: Quarterly growth ability
- `query_balance_data`: Quarterly debt repayment ability
- `query_cash_flow_data`: Quarterly cash flow
- `query_dupont_data`: Quarterly DuPont analysis

### 4. Company Reports
- `query_performance_express_report`: Performance express reports
- `query_forecast_report`: Performance forecast reports

### 5. Security Info
- `query_trade_dates`: Trading calendar
- `query_all_stock`: All stock codes
- `query_stock_basic`: Basic stock information

### 6. Macro Economy
- `query_deposit_rate_data`: Deposit interest rates
- `query_loan_rate_data`: Loan interest rates
- `query_required_reserve_ratio_data`: Reserve requirement ratios
- `query_money_supply_data_month`: Monthly money supply
- `query_money_supply_data_year`: Annual money supply
- `query_shibor_data`: SHIBOR rates

### 7. Sector Data
- `query_stock_industry`: Industry classification
- `query_sz50_stocks`: SSE 50 constituent stocks
- `query_hs300_stocks`: CSI 300 constituent stocks
- `query_zz500_stocks`: CSI 500 constituent stocks

## Project Files

- `baostock_browser.py`: Main program file
- `requirements.txt`: Python dependencies list
- `run.bat`: Windows one-click startup script
- `field_descriptions.csv`: Field description database (contains Chinese descriptions of all API fields)
- `stock_list.csv`: Stock list cache file (automatically generated after first run)
- `README.md`: Project documentation (Chinese)
- `README_EN.md`: Project documentation (English)

## System Requirements

- Python 3.7+
- streamlit >= 1.28.0
- baostock >= 0.8.8
- pandas >= 2.0.0
## Data Source

All data is provided by [BaoStock](http://www.baostock.com), a free and open-source securities data platform.

## Notes

- The application automatically handles login/logout to BaoStock
- Data is displayed in a tabular format with download capability
- Statistics are available for numeric columns
- All queries include error handling and user feedback

## License

This tool is provided as-is for educational and research purposes.

## Acknowledgments

- Data provided by [BaoStock](http://www.baostock.com)
- Built with [Streamlit](https://streamlit.io)