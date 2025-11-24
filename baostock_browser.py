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

# Initialize session state for field descriptions
if 'field_descriptions' not in st.session_state:
    st.session_state.field_descriptions = None

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
FIELD_DESC_FILE = "field_descriptions.csv"

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

def update_stock_list_with_industry(industry_df):
    """Update stock_list.csv with industry information"""
    try:
        # Load current stock list
        if os.path.exists(STOCK_LIST_FILE):
            stock_df = pd.read_csv(STOCK_LIST_FILE, encoding='utf-8-sig')
        else:
            st.error("Stock list file not found. Please refresh stock list first.")
            return False
        
        # Select relevant columns from industry data
        industry_cols = ['code', 'industry', 'industryClassification']
        industry_data = industry_df[industry_cols].copy()
        
        # Merge industry information into stock list
        # First, remove existing industry columns if they exist
        if 'industry' in stock_df.columns:
            stock_df = stock_df.drop(columns=['industry'])
        if 'industryClassification' in stock_df.columns:
            stock_df = stock_df.drop(columns=['industryClassification'])
        
        # Merge on 'code' column
        updated_df = stock_df.merge(industry_data, on='code', how='left')
        
        # Save updated data back to CSV
        updated_df.to_csv(STOCK_LIST_FILE, index=False, encoding='utf-8-sig')
        
        # Update session state
        st.session_state.stock_list = updated_df
        
        return True
    except Exception as e:
        st.error(f"Failed to update stock list with industry data: {e}")
        return False

def load_field_descriptions():
    """Load field descriptions from CSV file"""
    if st.session_state.field_descriptions is None:
        if os.path.exists(FIELD_DESC_FILE):
            try:
                df = pd.read_csv(FIELD_DESC_FILE, encoding='utf-8-sig')
                # Create a dictionary for quick lookup: {field_name: (description, detail)}
                desc_dict = {}
                for _, row in df.iterrows():
                    desc_dict[row['field_name']] = {
                        'category': row['api_category'],
                        'description': row['field_description'],
                        'detail': row['field_detail']
                    }
                st.session_state.field_descriptions = desc_dict
                return desc_dict
            except Exception as e:
                st.warning(f"Failed to load field descriptions: {e}")
                return {}
        else:
            st.warning(f"Field description file not found: {FIELD_DESC_FILE}")
            return {}
    return st.session_state.field_descriptions

def get_field_tooltip(field_name):
    """Get tooltip text for a field"""
    field_desc = load_field_descriptions()
    if field_name in field_desc:
        info = field_desc[field_name]
        tooltip = f"**{info['description']}**"
        if info['detail']:
            tooltip += f"\n\n{info['detail']}"
        return tooltip
    return field_name

def display_dataframe_with_tooltips(df, api_category=""):
    """Display dataframe with column tooltips"""
    if df.empty:
        st.info("No data to display")
        return
    
    # Load field descriptions
    field_desc = load_field_descriptions()
    
    # Create column configuration with help text for tooltips
    column_config = {}
    for col_name in df.columns:
        if col_name in field_desc:
            info = field_desc[col_name]
            # Combine description and detail for tooltip
            help_text = info['description']
            if info['detail']:
                help_text += f"\n{info['detail']}"
            
            column_config[col_name] = st.column_config.TextColumn(
                col_name,
                help=help_text,
                width="medium"
            )
        else:
            column_config[col_name] = st.column_config.TextColumn(
                col_name,
                help=f"{col_name} (No description available)",
                width="medium"
            )
    
    # Display field descriptions in an expander (as backup reference)
    with st.expander("📖 View All Field Descriptions", expanded=False):
        cols_per_row = 2
        columns = list(df.columns)
        
        for i in range(0, len(columns), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col_name in enumerate(columns[i:i+cols_per_row]):
                with cols[j]:
                    if col_name in field_desc:
                        info = field_desc[col_name]
                        st.markdown(f"**`{col_name}`**")
                        st.caption(f"📝 {info['description']}")
                        if info['detail']:
                            st.caption(f"ℹ️ {info['detail']}")
                    else:
                        st.markdown(f"**`{col_name}`**")
                        st.caption("No description available")
                    st.markdown("---")
    
    # Display the dataframe with column configuration
    st.dataframe(
        df, 
        column_config=column_config,
        use_container_width=True, 
        height=400,
        hide_index=True
    )

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

# Sidebar for API selection with expandable menu
st.sidebar.title("📚 API Interface Selection")

# Initialize session state for selected API
if 'selected_api' not in st.session_state:
    st.session_state.selected_api = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None

# Define API structure with categories and functions
API_STRUCTURE = {
    "K-Line Data": {
        "icon": "📊",
        "apis": {
            "query_history_k_data_plus": "历史K线数据，支持多种频率"
        }
    },
    "Dividend & Adjustment": {
        "icon": "💰",
        "apis": {
            "query_dividend_data": "分红信息",
            "query_adjust_factor": "复权因子"
        }
    },
    "Financial Data": {
        "icon": "📈",
        "apis": {
            "query_profit_data": "季度盈利能力",
            "query_operation_data": "季度营运能力",
            "query_growth_data": "季度成长能力",
            "query_balance_data": "季度偿债能力",
            "query_cash_flow_data": "季度现金流量",
            "query_dupont_data": "季度杜邦分析"
        }
    },
    "Company Reports": {
        "icon": "📋",
        "apis": {
            "query_performance_express_report": "业绩快报",
            "query_forecast_report": "业绩预告"
        }
    },
    "Security Info": {
        "icon": "🔍",
        "apis": {
            "query_trade_dates": "交易日历",
            "query_all_stock": "所有股票代码",
            "query_stock_basic": "股票基本信息"
        }
    },
    "Macro Economy": {
        "icon": "🌐",
        "apis": {
            "query_deposit_rate_data": "存款利率",
            "query_loan_rate_data": "贷款利率",
            "query_required_reserve_ratio_data": "存款准备金率",
            "query_money_supply_data_month": "月度货币供应量",
            "query_money_supply_data_year": "年度货币供应量",
            "query_shibor_data": "SHIBOR利率"
        }
    },
    "Sector Data": {
        "icon": "🏢",
        "apis": {
            "query_stock_industry": "行业分类",
            "query_sz50_stocks": "上证50成分股",
            "query_hs300_stocks": "沪深300成分股",
            "query_zz500_stocks": "中证500成分股"
        }
    }
}

# Display API menu with expanders
for category, info in API_STRUCTURE.items():
    with st.sidebar.expander(f"{info['icon']} {category}", expanded=(st.session_state.selected_category == category)):
        for api_name, api_desc in info['apis'].items():
            # Create button for each API
            button_label = f"{api_name} | {api_desc}"
            if st.button(button_label, key=f"btn_{api_name}", use_container_width=True):
                st.session_state.selected_api = api_name
                st.session_state.selected_category = category
                st.rerun()

# Get current selections
api_category = st.session_state.selected_category
api_function = st.session_state.selected_api

# Display current selection
if api_category and api_function:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**当前选择：**")
    st.sidebar.info(f"{API_STRUCTURE[api_category]['icon']} {api_category}\n\n🔹 {api_function}")
else:
    st.sidebar.markdown("---")
    st.sidebar.info("👆 请从上方菜单选择一个API接口")

# Main content area with two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parameters")
    
    # Check if API is selected
    if not api_category or not api_function:
        st.info("👈 请从左侧菜单选择一个API接口开始查询")
        st.markdown("""
        ### 使用说明
        
        1. **选择API接口**：点击左侧菜单中的API分类，展开后选择具体的查询接口
        2. **配置参数**：在此处输入查询所需的参数（已提供默认值）
        3. **执行查询**：点击"执行查询"按钮获取数据
        4. **查看结果**：查询结果将显示在右侧面板
        5. **导出数据**：可以下载CSV格式的查询结果
        
        ### 功能特性
        
        - 🎯 **智能股票选择器**：支持搜索和一键刷新
        - 📖 **字段说明提示**：鼠标悬停查看字段含义
        - 📊 **数据可视化**：自动统计数值列
        - 💾 **数据导出**：支持CSV格式下载
        """)
    
    # K-Line Data APIs
    elif api_category == "K-Line Data":
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
                            st.session_state.is_industry_data = False
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
    
    # Dividend & Adjustment APIs
    elif api_category == "Dividend & Adjustment":
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
                            # Mark that this is industry data for save button
                            st.session_state.is_industry_data = True
                        else:
                            st.error(f"Query failed: {rs.error_msg}")
            
            # Add save button for industry data
            st.markdown("---")
            st.markdown("### 💾 Save Industry Data")
            st.info("💡 Click the button below to save/update industry information to local stock_list.csv")
            
            if st.button("💾 Save Industry Data to stock_list.csv", type="secondary", use_container_width=True):
                if 'result_df' in st.session_state and not st.session_state.result_df.empty:
                    if 'is_industry_data' in st.session_state and st.session_state.is_industry_data:
                        with st.spinner("Updating stock_list.csv with industry data..."):
                            if update_stock_list_with_industry(st.session_state.result_df):
                                st.success("✅ Successfully updated stock_list.csv with industry information!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to update stock_list.csv")
                    else:
                        st.warning("⚠️ Current data is not industry data. Please query industry data first.")
                else:
                    st.warning("⚠️ No industry data to save. Please execute query first.")
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
        
        # Display dataframe with tooltips
        display_dataframe_with_tooltips(st.session_state.result_df, api_category)
        
        # Action buttons
        col_download, col_save = st.columns([1, 1])
        
        with col_download:
            # Download button
            csv = st.session_state.result_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"baostock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_save:
            # Save industry data button (only show for industry data)
            if 'is_industry_data' in st.session_state and st.session_state.is_industry_data:
                if st.button("💾 Save to stock_list.csv", use_container_width=True, type="secondary"):
                    with st.spinner("Updating stock_list.csv..."):
                        if update_stock_list_with_industry(st.session_state.result_df):
                            st.success("✅ Successfully updated stock_list.csv!")
                            st.balloons()
                        else:
                            st.error("❌ Failed to update stock_list.csv")
        
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
