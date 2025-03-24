# MySQL MCP 工具

MySQL MCP 是一个基于 MCP（Model-Control-Panel）框架的 MySQL 数据库操作工具，提供了简单易用的 API 来执行 SQL 查询、管理表结构、操作数据等功能。

## 功能特点

- 执行 SQL 查询语句并获取结果
- 列出数据库中的所有表
- 获取表结构信息
- 创建新表
- 插入、更新和删除数据
- 切换数据库
- 自动处理连接错误和重试
- 提供详细的错误信息和原因分析

## 安装

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

## 配置

MySQL 连接信息可以通过环境变量、命令行参数、代码中直接指定或MCP配置文件：

### 环境变量

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=your_database
export MYSQL_CONNECTION_TIMEOUT=10
export MYSQL_CONNECT_RETRY_COUNT=3
```

### 命令行参数

```bash
python mysql-mcp.py --host localhost --port 3306 --user root --password your_password --database your_database
```

### MCP 配置文件

在 `~/.cursor/mcp.json` 中添加以下配置：

```json
{
    "mcpServers": {
        {
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
}
```

## 使用方法

### 启动服务

```bash
python mysql-mcp.py
```

### 可用工具函数

#### 1. 执行查询：execute_query

```python
# 执行 SELECT 查询
result = await execute_query("SELECT * FROM users WHERE age > %s", [18])

# 执行 INSERT 语句
result = await execute_query("INSERT INTO users (name, age) VALUES ('张三', 25)")

# 执行 SHOW DATABASES 查询
result = await execute_query("SHOW DATABASES")
```

#### 2. 列出表：list_tables

```python
# 列出当前数据库的所有表
result = await list_tables()

# 列出特定数据库的所有表
result = await list_tables(database_name="information_schema")
```

#### 3. 获取表结构：describe_table

```python
# 获取表结构
result = await describe_table("users")
```

#### 4. 创建表：create_table

```python
# 创建新表
columns_def = "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, age INT, email VARCHAR(255) UNIQUE"
result = await create_table("new_users", columns_def)
```

#### 5. 插入数据：insert_data

```python
# 插入数据
data = {"name": "李四", "age": 30, "email": "lisi@example.com"}
result = await insert_data("users", data)
```

#### 6. 更新数据：update_data

```python
# 更新数据
data = {"age": 31, "email": "lisi_new@example.com"}
result = await update_data("users", data, "name = %s", ["李四"])
```

#### 7. 删除数据：delete_data

```python
# 删除数据
result = await delete_data("users", "age < %s", [18])
```

#### 8. 切换数据库：use_database

```python
# 切换到另一个数据库
result = await use_database("another_database")
```

## 错误处理

所有工具函数都会返回详细的错误信息和原因分析，便于快速定位和解决问题：

```python
# 查询不存在的表
result = await execute_query("SELECT * FROM non_existing_table")
# 返回: {"error": "执行查询失败: Table 'your_database.non_existing_table' doesn't exist\n原因：查询的表不存在", "query": "SELECT * FROM non_existing_table"}
```

## 扩展与自定义

您可以修改源代码来添加更多功能或调整现有功能的行为。主要的扩展点包括：

- 在 `mysql-mcp.py` 中添加新的工具函数
- 修改现有函数的错误处理和返回值
- 调整数据库连接的默认配置

## 许可证

[MIT 许可证](LICENSE)
