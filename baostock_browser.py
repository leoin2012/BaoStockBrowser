import streamlit as st
import baostock as bs
import pandas as pd
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="BaoStock Data Browser",
    page_icon="📈",
    layout="wide"
)

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize session state for stock list
if 'stock_list' not in st.session_state:
    st.session_state.stock_list = None
if 'stock_list_loaded' not in st.session_state:
    st.session_state.stock_list_loaded = False

# Login to baostock
def login_baostock():
    if not st.session_state.logged_in:
        lg = bs.login()
        if lg.error_code == '0':
            st.session_state.logged_in = True
            return True
        else:
            st.error(f"Login failed: {lg.error_msg}")
            return False
    return True

# Logout from baostock
def logout_baostock():
    if st.session_state.logged_in:
        bs.logout()
        st.session_state.logged_in = False

# Convert result to DataFrame
def result_to_dataframe(rs):
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    if data_list:
        return pd.DataFrame(data_list, columns=rs.fields)
    return pd.DataFrame()

# Stock list management
STOCK_LIST_FILE = "stock_list.csv"

def load_stock_list_from_file():
    """Load stock list from local CSV file"""
    if os.path.exists(STOCK_LIST_FILE):
        try:
            df = pd.read_csv(STOCK_LIST_FILE, encoding='utf-8-sig')
            return df
        except Exception as e:
            st.warning(f"Failed to load stock list from file: {e}")
    return None

def refresh_stock_list():
    """Refresh stock list from BaoStock API"""
    if login_baostock():
        with st.spinner("Refreshing stock list from BaoStock API..."):
            rs = bs.query_stock_basic()
            if rs.error_code == '0':
                df = result_to_dataframe(rs)
                if not df.empty:
                    # Save to local file
                    df.to_csv(STOCK_LIST_FILE, index=False, encoding='utf-8-sig')
                    st.session_state.stock_list = df
                    st.session_state.stock_list_loaded = True
                    st.success(f"✅ Stock list refreshed! Total {len(df)} stocks loaded.")
                    return df
                else:
                    st.error("No stock data returned")
            else:
                st.error(f"Failed to refresh stock list: {rs.error_msg}")
    return None

def get_stock_list():
    """Get stock list (from cache, file, or API)"""
    # If already loaded in session, return it
    if st.session_state.stock_list is not None:
        return st.session_state.stock_list
    
    # Try to load from file
    df = load_stock_list_from_file()
    if df is not None:
        st.session_state.stock_list = df
        st.session_state.stock_list_loaded = True
        return df
    
    # If no file exists, refresh from API
    return refresh_stock_list()

def stock_selector(label="Stock Code", key=None, help_text="Select or search stock"):
    """Create a searchable stock selector with refresh button"""
    col_select, col_refresh = st.columns([4, 1])
    
    with col_refresh:
        st.write("")  # Add spacing
        if st.button("🔄", key=f"refresh_{key}", help="Refresh stock list"):
            refresh_stock_list()
    
    with col_select:
        stock_list = get_stock_list()
        
        if stock_list is not None and not stock_list.empty:
            # Create display options: "code - name"
            stock_list['display'] = stock_list['code'] + ' - ' + stock_list['code_name']
            options = [''] + stock_list['display'].tolist()
            
            selected = st.selectbox(
                label,
                options=options,
                key=key,
                help=help_text
            )
            
            # Extract code from selection
            if selected:
                code = selected.split(' - ')[0]
                return code
            return ""
        else:
            # Fallback to text input if stock list not available
            st.warning("Stock list not loaded. Using text input.")
            return st.text_input(label, value="", key=key, help=help_text)
    
    return ""

# Main title
st.title("📈 BaoStock Data Browser")
st.markdown("---")

# Sidebar for API selection
st.sidebar.title("API Interface Selection")
api_category = st.sidebar.selectbox(
    "Select API Category",
    ["K-Line Data", "Dividend & Adjustment", "Financial Data", "Company Reports", 
     "Security Info", "Macro Economy", "Sector Data"]
)

# Main content area with two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parameters")
    
    # K-Line Data APIs
    if api_category == "K-Line Data":
        api_function = st.selectbox("Select Function", ["query_history_k_data_plus"])
        
        if api_function == "query_history_k_data_plus":
            code = stock_selector("Stock Code", key="kline_code", help_text="Select stock for K-line data")
            if not code:
                code = "sh.600000"  # Default value
            
            frequency = st.selectbox("Frequency", ["d", "w", "m", "5", "15", "30", "60"], 
                                    index=0, help="d=daily, w=weekly, m=monthly, 5/15/30/60=minutes")
            
            # Default date range: last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            start_date_input = st.date_input("Start Date", value=start_date)
            end_date_input = st.date_input("End Date", value=end_date)
            
            adjustflag = st.selectbox("Adjust Flag", ["3", "1", "2"], 
                                     index=0, help="3=No adjust, 1=Back adjust, 2=Forward adjust")
            
            # Fields selection based on frequency
            if frequency in ["5", "15", "30", "60"]:
                default_fields = "date,time,code,open,high,low,close,volume,amount,adjustflag"
            else:
                default_fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
            
            fields = st.text_area("Fields", value=default_fields, height=100)
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        rs = bs.query_history_k_data_plus(
                            code, fields,
                            start_date=start_date_input.strftime("%Y-%m-%d"),
                            end_date=end_date_input.strftime("%Y-%m-%d"),
                            frequency=frequency,
                            adjustflag=adjustflag
                        )
                        
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = f"K-Line Data: {code}"
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
    
    # Dividend & Adjustment APIs
    elif api_category == "Dividend & Adjustment":
        api_function = st.selectbox("Select Function", ["query_dividend_data", "query_adjust_factor"])
        
        if api_function == "query_dividend_data":
            code = stock_selector("Stock Code", key="dividend_code", help_text="Select stock for dividend data")
            if not code:
                code = "sh.600000"  # Default value
            year = st.text_input("Year", value="2023")
            yearType = st.selectbox("Year Type", ["report", "operate"], 
                                   help="report=Report year, operate=Operation year")
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        rs = bs.query_dividend_data(code=code, year=year, yearType=yearType)
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = f"Dividend Data: {code} ({year})"
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
        
        elif api_function == "query_adjust_factor":
            code = stock_selector("Stock Code", key="adjust_code", help_text="Select stock for adjust factor")
            if not code:
                code = "sh.600000"  # Default value
            start_date_input = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
            end_date_input = st.date_input("End Date", value=datetime.now())
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        rs = bs.query_adjust_factor(
                            code=code,
                            start_date=start_date_input.strftime("%Y-%m-%d"),
                            end_date=end_date_input.strftime("%Y-%m-%d")
                        )
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = f"Adjust Factor: {code}"
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
    
    # Financial Data APIs
    elif api_category == "Financial Data":
        api_function = st.selectbox("Select Function", [
            "query_profit_data", "query_operation_data", "query_growth_data",
            "query_balance_data", "query_cash_flow_data", "query_dupont_data"
        ])
        
        code = stock_selector("Stock Code", key="financial_code", help_text="Select stock for financial data")
        if not code:
            code = "sh.600000"  # Default value
        year = st.number_input("Year", min_value=2000, max_value=datetime.now().year, value=2023)
        quarter = st.selectbox("Quarter", [1, 2, 3, 4], index=0)
        
        if st.button("Execute Query", type="primary"):
            if login_baostock():
                with st.spinner("Querying data..."):
                    if api_function == "query_profit_data":
                        rs = bs.query_profit_data(code=code, year=year, quarter=quarter)
                    elif api_function == "query_operation_data":
                        rs = bs.query_operation_data(code=code, year=year, quarter=quarter)
                    elif api_function == "query_growth_data":
                        rs = bs.query_growth_data(code=code, year=year, quarter=quarter)
                    elif api_function == "query_balance_data":
                        rs = bs.query_balance_data(code=code, year=year, quarter=quarter)
                    elif api_function == "query_cash_flow_data":
                        rs = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
                    elif api_function == "query_dupont_data":
                        rs = bs.query_dupont_data(code=code, year=year, quarter=quarter)
                    
                    if rs.error_code == '0':
                        df = result_to_dataframe(rs)
                        st.session_state.result_df = df
                        st.session_state.query_info = f"{api_function}: {code} ({year}Q{quarter})"
                    else:
                        st.error(f"Query failed: {rs.error_msg}")
    
    # Company Reports APIs
    elif api_category == "Company Reports":
        api_function = st.selectbox("Select Function", [
            "query_performance_express_report", "query_forecast_report"
        ])
        
        code = stock_selector("Stock Code", key="report_code", help_text="Select stock for company reports")
        if not code:
            code = "sh.600000"  # Default value
        start_date_input = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
        end_date_input = st.date_input("End Date", value=datetime.now())
        
        if st.button("Execute Query", type="primary"):
            if login_baostock():
                with st.spinner("Querying data..."):
                    if api_function == "query_performance_express_report":
                        rs = bs.query_performance_express_report(
                            code,
                            start_date=start_date_input.strftime("%Y-%m-%d"),
                            end_date=end_date_input.strftime("%Y-%m-%d")
                        )
                    elif api_function == "query_forecast_report":
                        rs = bs.query_forecast_report(
                            code,
                            start_date=start_date_input.strftime("%Y-%m-%d"),
                            end_date=end_date_input.strftime("%Y-%m-%d")
                        )
                    
                    if rs.error_code == '0':
                        df = result_to_dataframe(rs)
                        st.session_state.result_df = df
                        st.session_state.query_info = f"{api_function}: {code}"
                    else:
                        st.error(f"Query failed: {rs.error_msg}")
    
    # Security Info APIs
    elif api_category == "Security Info":
        api_function = st.selectbox("Select Function", [
            "query_trade_dates", "query_all_stock", "query_stock_basic"
        ])
        
        if api_function == "query_trade_dates":
            start_date_input = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
            end_date_input = st.date_input("End Date", value=datetime.now())
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        rs = bs.query_trade_dates(
                            start_date=start_date_input.strftime("%Y-%m-%d"),
                            end_date=end_date_input.strftime("%Y-%m-%d")
                        )
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = "Trade Dates"
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
        
        elif api_function == "query_all_stock":
            day_input = st.date_input("Query Date", value=datetime.now())
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        rs = bs.query_all_stock(day=day_input.strftime("%Y-%m-%d"))
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = f"All Stocks ({day_input})"
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
        
        elif api_function == "query_stock_basic":
            use_selector = st.checkbox("Use stock selector", value=False, help="Check to use dropdown selector")
            
            if use_selector:
                code = stock_selector("Stock Code", key="basic_code", help_text="Select stock for basic info")
                code_name = ""
            else:
                code = st.text_input("Stock Code", value="", help="Leave empty to query all stocks")
                code_name = st.text_input("Stock Name", value="", help="Support fuzzy search, leave empty to query all")
            
            st.info("💡 Tip: Leave both fields empty to get all A-share stocks basic information")
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        # If both parameters are empty, query all stocks
                        if not code and not code_name:
                            rs = bs.query_stock_basic()
                            query_desc = "All Stocks"
                        elif code:
                            rs = bs.query_stock_basic(code=code)
                            query_desc = f"Code: {code}"
                        else:
                            rs = bs.query_stock_basic(code_name=code_name)
                            query_desc = f"Name: {code_name}"
                        
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = f"Stock Basic Info - {query_desc}"
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
    
    # Macro Economy APIs
    elif api_category == "Macro Economy":
        api_function = st.selectbox("Select Function", [
            "query_deposit_rate_data", "query_loan_rate_data", 
            "query_required_reserve_ratio_data", "query_money_supply_data_month",
            "query_money_supply_data_year", "query_shibor_data"
        ])
        
        if api_function in ["query_money_supply_data_month"]:
            start_date_str = st.text_input("Start Date (YYYY-MM)", value="2023-01")
            end_date_str = st.text_input("End Date (YYYY-MM)", value="2023-12")
        elif api_function in ["query_money_supply_data_year"]:
            start_date_str = st.text_input("Start Year (YYYY)", value="2020")
            end_date_str = st.text_input("End Year (YYYY)", value="2023")
        else:
            start_date_input = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
            end_date_input = st.date_input("End Date", value=datetime.now())
            start_date_str = start_date_input.strftime("%Y-%m-%d")
            end_date_str = end_date_input.strftime("%Y-%m-%d")
        
        if st.button("Execute Query", type="primary"):
            if login_baostock():
                with st.spinner("Querying data..."):
                    if api_function == "query_deposit_rate_data":
                        rs = bs.query_deposit_rate_data(start_date=start_date_str, end_date=end_date_str)
                    elif api_function == "query_loan_rate_data":
                        rs = bs.query_loan_rate_data(start_date=start_date_str, end_date=end_date_str)
                    elif api_function == "query_required_reserve_ratio_data":
                        rs = bs.query_required_reserve_ratio_data(start_date=start_date_str, end_date=end_date_str)
                    elif api_function == "query_money_supply_data_month":
                        rs = bs.query_money_supply_data_month(start_date=start_date_str, end_date=end_date_str)
                    elif api_function == "query_money_supply_data_year":
                        rs = bs.query_money_supply_data_year(start_date=start_date_str, end_date=end_date_str)
                    elif api_function == "query_shibor_data":
                        rs = bs.query_shibor_data(start_date=start_date_str, end_date=end_date_str)
                    
                    if rs.error_code == '0':
                        df = result_to_dataframe(rs)
                        st.session_state.result_df = df
                        st.session_state.query_info = api_function
                    else:
                        st.error(f"Query failed: {rs.error_msg}")
    
    # Sector Data APIs
    elif api_category == "Sector Data":
        api_function = st.selectbox("Select Function", [
            "query_stock_industry", "query_sz50_stocks", 
            "query_hs300_stocks", "query_zz500_stocks"
        ])
        
        if api_function == "query_stock_industry":
            code = stock_selector("Stock Code (optional)", key="industry_code", help_text="Select stock or leave empty for all")
            date_input = st.date_input("Query Date", value=datetime.now())
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        if code:
                            rs = bs.query_stock_industry(code=code, date=date_input.strftime("%Y-%m-%d"))
                        else:
                            rs = bs.query_stock_industry()
                        
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = "Stock Industry"
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
        else:
            date_input = st.date_input("Query Date", value=datetime.now())
            
            if st.button("Execute Query", type="primary"):
                if login_baostock():
                    with st.spinner("Querying data..."):
                        if api_function == "query_sz50_stocks":
                            rs = bs.query_sz50_stocks(date=date_input.strftime("%Y-%m-%d"))
                        elif api_function == "query_hs300_stocks":
                            rs = bs.query_hs300_stocks(date=date_input.strftime("%Y-%m-%d"))
                        elif api_function == "query_zz500_stocks":
                            rs = bs.query_zz500_stocks(date=date_input.strftime("%Y-%m-%d"))
                        
                        if rs.error_code == '0':
                            df = result_to_dataframe(rs)
                            st.session_state.result_df = df
                            st.session_state.query_info = api_function
                        else:
                            st.error(f"Query failed: {rs.error_msg}")

# Right column for results
with col2:
    st.subheader("Query Results")
    
    if 'result_df' in st.session_state and not st.session_state.result_df.empty:
        st.info(f"Query: {st.session_state.query_info}")
        st.write(f"Total Records: {len(st.session_state.result_df)}")
        
        # Display dataframe
        st.dataframe(st.session_state.result_df, use_container_width=True, height=400)
        
        # Download button
        csv = st.session_state.result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"baostock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Show basic statistics for numeric columns
        numeric_cols = st.session_state.result_df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            with st.expander("View Statistics"):
                st.write(st.session_state.result_df[numeric_cols].describe())
    else:
        st.info("No data to display. Please execute a query from the left panel.")

# Footer
st.markdown("---")
st.markdown("**BaoStock Data Browser** | Data source: [www.baostock.com](http://www.baostock.com)")

# Cleanup on app close
if st.session_state.logged_in:
    logout_baostock()
