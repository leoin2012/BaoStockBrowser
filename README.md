# 📈 BaoStock 数据浏览器

一个功能全面的网页工具，用于查询 BaoStock API 数据，界面直观易用。

## 功能特性

- **🎯 智能股票选择器**：
  - 下拉框列出所有可查询股票（代码 + 名称）
  - 支持关键字搜索快速定位股票
  - 一键刷新按钮（🔄）更新股票列表
  - 自动缓存到本地CSV文件，无需每次重新加载
  - 首次使用自动从API获取完整股票列表
- **📖 字段说明提示**：
  - 所有查询结果表格字段都有详细的中文说明
  - 点击"View Field Descriptions"展开查看所有字段含义
  - 包含字段描述、计算公式、单位等详细信息
  - 字段定义保存在本地CSV文件（field_descriptions.csv）
  - 支持自定义扩展字段说明
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
3. **使用股票选择器**：
   - 点击下拉框查看所有股票列表
   - 在下拉框中输入关键字快速搜索（支持代码或名称）
   - 点击右侧 🔄 按钮刷新股票列表（从API重新获取）
   - 首次使用会自动加载股票列表并保存到 `stock_list.csv`
   - 后续使用自动从本地文件加载，无需等待
4. **执行查询**：点击"执行查询"按钮
5. **查看结果**：结果将显示在右侧面板
6. **下载数据**：使用"下载CSV"按钮导出结果

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

## 项目文件

- `baostock_browser.py`: 主程序文件
- `requirements.txt`: Python依赖包列表
- `run.bat`: Windows一键启动脚本
- `field_descriptions.csv`: 字段说明数据库（包含所有API字段的中文描述）
- `stock_list.csv`: 股票列表缓存文件（首次运行后自动生成）
- `README.md`: 项目说明文档（中文）
- `README_EN.md`: 项目说明文档（英文）

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
