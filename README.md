# 📈 BaoStock 数据浏览器

一个功能全面的网页工具，用于查询 BaoStock API 数据，界面直观易用。

## 功能特性

- **K线数据**：查询历史股票K线数据（日线、周线、月线和分钟级别）
- **分红送股与复权**：获取分红信息和复权因子
- **财务数据**：查询季度财务报表，包括：
  - 盈利能力指标
  - 营运能力指标
  - 成长能力指标
  - 偿债能力指标
  - 现金流量指标
  - 杜邦分析指标
- **公司报告**：业绩快报和业绩预告
- **证券信息**：交易日历、股票代码和基本股票信息
- **宏观经济**：利率、存款准备金率、货币供应量和SHIBOR数据
- **板块数据**：行业分类和指数成分股（上证50、沪深300、中证500）

## 安装

1. 克隆此仓库或下载文件
2. 安装所需依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 快速启动（Windows）

直接双击 `run.bat` 文件即可启动应用程序。脚本将自动：
- 检查是否安装了 Python
- 如需要，自动安装依赖包
- 启动 Streamlit 服务器
- 在默认浏览器中打开应用程序

### 手动启动

或者，使用 Streamlit 运行应用程序：

```bash
streamlit run baostock_browser.py
```

应用程序将在默认浏览器中打开，地址为 `http://localhost:8501`

**注意**：在终端中按 `Ctrl+C` 可停止服务器

## 如何使用

1. **选择API类别**：从左侧边栏选择
2. **配置参数**：在左侧面板输入所需参数
   - 提供了默认值以便快速测试
   - 所有参数都可以根据需要自定义
3. **执行查询**：点击"执行查询"按钮
4. **查看结果**：结果将显示在右侧面板
5. **下载数据**：使用"下载CSV"按钮导出结果

## 默认参数

工具为所有参数提供了合理的默认值：

- **股票代码**：sh.600000（浦发银行）
- **日期范围**：最近30天（大多数查询）
- **频率**：日线（K线数据）
- **复权类型**：不复权（3）

只需点击"执行查询"即可立即获取数据，然后根据需要修改参数。

## API 分类

### 1. K线数据
- `query_history_k_data_plus`：历史K线数据，支持多种频率

### 2. 分红送股与复权
- `query_dividend_data`：分红信息
- `query_adjust_factor`：复权因子

### 3. 财务数据
- `query_profit_data`：季度盈利能力
- `query_operation_data`：季度营运能力
- `query_growth_data`：季度成长能力
- `query_balance_data`：季度偿债能力
- `query_cash_flow_data`：季度现金流量
- `query_dupont_data`：季度杜邦分析

### 4. 公司报告
- `query_performance_express_report`：业绩快报
- `query_forecast_report`：业绩预告

### 5. 证券信息
- `query_trade_dates`：交易日历
- `query_all_stock`：所有股票代码
- `query_stock_basic`：股票基本信息

### 6. 宏观经济
- `query_deposit_rate_data`：存款利率
- `query_loan_rate_data`：贷款利率
- `query_required_reserve_ratio_data`：存款准备金率
- `query_money_supply_data_month`：月度货币供应量
- `query_money_supply_data_year`：年度货币供应量
- `query_shibor_data`：SHIBOR利率

### 7. 板块数据
- `query_stock_industry`：行业分类
- `query_sz50_stocks`：上证50成分股
- `query_hs300_stocks`：沪深300成分股
- `query_zz500_stocks`：中证500成分股

## 系统要求

- Python 3.7+
- streamlit >= 1.28.0
- baostock >= 0.8.8
- pandas >= 2.0.0

## 数据来源

所有数据由 [BaoStock](http://www.baostock.com) 提供，这是一个免费开源的证券数据平台。

## 注意事项

- 应用程序自动处理 BaoStock 的登录/登出
- 数据以表格格式显示，支持下载
- 数值列提供统计信息
- 所有查询都包含错误处理和用户反馈

## 许可证

本工具按原样提供，仅用于教育和研究目的。

## 致谢

- 数据由 [BaoStock](http://www.baostock.com) 提供
- 使用 [Streamlit](https://streamlit.io) 构建
