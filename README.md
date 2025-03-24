# MySQL MCP 工具

MySQL MCP 是一个基于 MCP（Model-Control-Panel）框架的 MySQL 数据库操作工具，提供了简单易用的 API 来执行 SQL 查询、管理表结构、操作数据等功能。

## MCP 框架简介

MCP（Model-Control-Panel）是一个强大的工具框架，允许您将工具函数暴露为API，使模型（如AI助手）能够直接调用这些函数。MySQL MCP 将 MySQL 数据库操作封装为 MCP 工具，便于与 Cursor IDE 等工具集成使用。

## 如何使用 MCP

### 1. 配置 MCP

在 `~/.cursor/mcp.json` 中添加以下配置：

```json
{
    "mcpServers": {
        "mysql-mcp": {
            "command": "/path/to/uv",
            "args": [
                "--directory",
                "/path/to/mysql-mcp",
                "run",
                "mysql-mcp.py",
                "--host", "xxx.xxx.xxx.xxx",
                "--port", "3306",
                "--user", "root",
                "--password", "********",
                "--database", "your_database",
                "--connection-timeout", "10",
                "--connect-retry-count", "3"
            ]
        }
    }
}
```

### 2. 启动 MCP 服务

配置完成后，Cursor IDE 会自动启动 MCP 服务，无需手动操作。如需单独运行：

```bash
python mysql-mcp.py
```

### 3. 在 MCP 环境中调用工具函数

在 Cursor IDE 中，AI 助手可以直接调用 MySQL MCP 工具：

```python
# 查询所有数据库
await mcp_mysql_mcp_execute_query("SHOW DATABASES")

# 列出当前数据库的所有表
await mcp_mysql_mcp_list_tables()

# 执行复杂查询
await mcp_mysql_mcp_execute_query("SELECT * FROM users WHERE age > %s", [18])
```

## 可用 MCP 工具函数

### 1. 执行查询：mcp_mysql_mcp_execute_query

```python
# 执行 SELECT 查询
result = await mcp_mysql_mcp_execute_query(query="SELECT * FROM users WHERE age > %s", params=[18])

# 执行 SHOW DATABASES 查询
result = await mcp_mysql_mcp_execute_query(query="SHOW DATABASES")

# 查询结果格式
# {
#     "success": true,
#     "rows": [{"id": 1, "name": "张三", "age": 25}, ...],
#     "row_count": 10
# }
```

### 2. 列出表：mcp_mysql_mcp_list_tables

```python
# 列出当前数据库的所有表
result = await mcp_mysql_mcp_list_tables()

# 列出特定数据库的所有表
result = await mcp_mysql_mcp_list_tables(database_name="information_schema")

# 返回结果格式
# {
#     "success": true,
#     "database": "your_database",
#     "tables": ["users", "products", "orders"],
#     "count": 3
# }
```

### 3. 获取表结构：mcp_mysql_mcp_describe_table

```python
# 获取表结构
result = await mcp_mysql_mcp_describe_table(table_name="users")

# 返回结果格式
# {
#     "success": true,
#     "table": "users",
#     "columns": [
#         {"Field": "id", "Type": "int(11)", "Null": "NO", "Key": "PRI", "Default": null, "Extra": "auto_increment"},
#         {"Field": "name", "Type": "varchar(100)", "Null": "NO", "Key": "", "Default": null, "Extra": ""}
#     ]
# }
```

### 4. 切换数据库：mcp_mysql_mcp_use_database

```python
# 切换到另一个数据库
result = await mcp_mysql_mcp_use_database(database_name="another_database")

# 返回结果格式
# {
#     "success": true,
#     "message": "已切换到数据库 another_database",
#     "current_database": "another_database"
# }
```

### 5. 其他数据操作工具

- **创建表**：`mcp_mysql_mcp_create_table(table_name, columns_def)`
- **插入数据**：`mcp_mysql_mcp_insert_data(table_name, data)`
- **更新数据**：`mcp_mysql_mcp_update_data(table_name, data, condition, params)`
- **删除数据**：`mcp_mysql_mcp_delete_data(table_name, condition, params)`

## 功能特点

- 执行 SQL 查询语句并获取结果
- 列出数据库中的所有表
- 获取表结构信息
- 创建新表
- 插入、更新和删除数据
- 切换数据库
- 自动处理连接错误和重试
- 提供详细的错误信息和原因分析

## 错误处理

所有工具函数都会返回详细的错误信息和原因分析，便于快速定位和解决问题：

```python
# 查询不存在的表
result = await mcp_mysql_mcp_execute_query(query="SELECT * FROM non_existing_table")
# 返回: {"error": "执行查询失败: Table 'your_database.non_existing_table' doesn't exist\n原因：查询的表不存在", "query": "SELECT * FROM non_existing_table"}
```

## 安装与配置

### 安装

1. 确保您已安装 Python 3.12 或更高版本
2. 克隆仓库到本地：

```bash
git clone https://github.com/Liu-creators/mysql-mcp.git
cd mysql-mcp
```

3. 创建并激活虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # 在 Windows 上使用 .venv\Scripts\activate
```

4. 安装依赖：

```bash
pip install -e .
```

### 其他配置方式

除了 MCP 配置外，还可以通过以下方式配置：

#### 环境变量

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=your_database
export MYSQL_CONNECTION_TIMEOUT=10
export MYSQL_CONNECT_RETRY_COUNT=3
```

#### 命令行参数

```bash
python mysql-mcp.py --host localhost --port 3306 --user root --password your_password --database your_database
```

## 扩展与自定义

您可以修改源代码来添加更多功能或调整现有功能的行为。主要的扩展点包括：

- 在 `mysql-mcp.py` 中添加新的工具函数
- 修改现有函数的错误处理和返回值
- 调整数据库连接的默认配置

## 许可证

[MIT 许可证](LICENSE)
