# MySQL-MCP

一个基于MCP（Model Control Protocol）的MySQL数据库操作工具，提供简单易用的数据库管理接口。

## 项目简介

MySQL-MCP 是一个用Python编写的工具，通过MCP协议提供MySQL数据库操作能力。它封装了MySQL常用操作，包括查询数据、管理表结构、数据增删改查等功能，使数据库操作更加便捷。

## 功能特点

- 执行SQL查询并获取结果
- 查看数据库中的表列表
- 查看表结构详情
- 创建新表
- 插入数据记录
- 更新已有数据
- 删除数据记录
- 切换数据库
- 支持参数化查询，防止SQL注入
- 完善的错误处理和提示信息

## 环境要求

- Python 3.12 或更高版本
- MySQL服务器

## 安装方法

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/mysql-mcp.git
cd mysql-mcp
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -e .
```

## 使用方法
mcp 文件中使用

```json
{
  "mcpServers": {
    "mysql-mcp": {
      "command": "/Users/userName/.local/bin/uv",
      "args": [
        "--directory",
        "path/mysql-mcp",
        "run",
        "mysql-mcp.py",
        "--host", "localhost",
        "--port","3306",
        "--user","root",
        "--password","root",
        "--database","db",
        "--connection-timeout","10",
        "--connect-retry-count","3"
      ]
    }
  }
}
```

### 配置数据库连接

通过环境变量配置：

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=your_database
export MYSQL_CONNECTION_TIMEOUT=10
export MYSQL_CONNECT_RETRY_COUNT=3
```

或通过命令行参数配置：

```bash
python mysql-mcp.py --host localhost --port 3306 --user root --password your_password --database your_database
```

### 工具功能说明

#### 1. 执行SQL查询

执行任意SQL查询语句，支持SELECT、INSERT、UPDATE、DELETE、SHOW等。

#### 2. 查看表列表

列出指定数据库中的所有表。

#### 3. 查看表结构

获取指定表的结构信息，包括字段名、类型、约束等。

#### 4. 创建新表

创建新的数据库表，可指定字段定义和约束。

#### 5. 插入数据

向指定表中插入数据记录。

#### 6. 更新数据

根据条件更新表中的数据。

#### 7. 删除数据

根据条件从表中删除数据。

#### 8. 切换数据库

切换当前连接的数据库。

## 示例

```python
# 使用示例
from mysql_mcp import execute_query, list_tables, describe_table

# 查询数据
result = await execute_query("SELECT * FROM users LIMIT 10")
print(result)

# 获取表列表
tables = await list_tables()
print(tables)

# 查看表结构
structure = await describe_table("users")
print(structure)
```

## 错误处理

工具提供详细的错误信息和原因解释，便于问题排查：

- 连接错误：显示主机、端口等配置信息
- 访问权限错误：提示检查用户名和密码
- 数据库或表不存在错误：提示检查名称是否正确
- SQL语法错误：提示检查SQL语句
- 数据约束错误：提示违反了哪种约束

## 贡献方式

欢迎提交问题报告和功能建议，也欢迎提交Pull Request。

## 许可证

[MIT](LICENSE)
