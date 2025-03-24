from typing import Any, List, Dict, Optional
import os
import argparse
import mysql.connector
from mysql.connector import Error
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP server
mcp = FastMCP("mysql")

# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description='MySQL MCP服务')
    parser.add_argument('--host', type=str, help='数据库主机地址')
    parser.add_argument('--port', type=int, help='数据库端口')
    parser.add_argument('--user', type=str, help='数据库用户名')
    parser.add_argument('--password', type=str, help='数据库密码')
    parser.add_argument('--database', type=str, help='数据库名称')
    parser.add_argument('--connection-timeout', type=int, help='连接超时时间(秒)')
    parser.add_argument('--connect-retry-count', type=int, help='连接重试次数')
    return parser.parse_args()

# 数据库连接配置默认值
DEFAULT_DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": os.getenv("MYSQL_DATABASE", ""),
    "connection_timeout": int(os.getenv("MYSQL_CONNECTION_TIMEOUT", "10")),  # 连接超时时间(秒)
    "connect_retry_count": int(os.getenv("MYSQL_CONNECT_RETRY_COUNT", "3"))  # 连接重试次数
}

# 从命令行参数获取配置
def get_config_from_args():
    args = parse_args()
    cmd_config = {}
    
    if args.host:
        cmd_config["host"] = args.host
    if args.port:
        cmd_config["port"] = args.port
    if args.user:
        cmd_config["user"] = args.user
    if args.password:
        cmd_config["password"] = args.password
    if args.database:
        cmd_config["database"] = args.database
    if args.connection_timeout:
        cmd_config["connection_timeout"] = args.connection_timeout
    if args.connect_retry_count:
        cmd_config["connect_retry_count"] = args.connect_retry_count
    
    # 合并配置
    config = DEFAULT_DB_CONFIG.copy()
    config.update(cmd_config)
    
    return config

# 全局数据库配置
GLOBAL_DB_CONFIG = None

def get_connection(db_config=None):
    """获取数据库连接
    
    Args:
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        数据库连接对象
    """
    # 如果没有提供配置，先尝试使用全局配置，再使用默认配置
    if db_config is None:
        if GLOBAL_DB_CONFIG is not None:
            db_config = GLOBAL_DB_CONFIG.copy()
        else:
            db_config = DEFAULT_DB_CONFIG.copy()
    else:
        # 合并用户提供的配置和全局/默认配置
        if GLOBAL_DB_CONFIG is not None:
            config = GLOBAL_DB_CONFIG.copy()
        else:
            config = DEFAULT_DB_CONFIG.copy()
        config.update(db_config)
        db_config = config
    
    retry_count = 0
    last_error = None
    max_retries = db_config.get("connect_retry_count", 3)
    
    while retry_count < max_retries:
        try:
            # 创建一个配置字典的副本，移除自定义的配置项
            db_config_copy = db_config.copy()
            db_config_copy.pop("connect_retry_count", None)
            
            # 将connection_timeout转换为mysql.connector需要的connect_timeout参数
            if "connection_timeout" in db_config_copy:
                db_config_copy["connect_timeout"] = db_config_copy.pop("connection_timeout")
                
            conn = mysql.connector.connect(**db_config_copy)
            return conn
        except Error as e:
            last_error = e
            retry_count += 1
            if retry_count < max_retries:
                # 只有在还有重试机会的情况下打印重试信息
                print(f"第 {retry_count} 次连接失败，正在重试... 错误: {e}")
    
    # 所有重试都失败后，构建详细的错误信息
    error_message = f"数据库连接错误(重试 {retry_count} 次后): {last_error}"
    if "Can't connect to MySQL server" in str(last_error):
        error_message += f"\n无法连接到MySQL服务器，请检查主机 {db_config['host']} 和端口 {db_config['port']} 是否正确"
        error_message += f"\n连接超时时间为 {db_config.get('connection_timeout', 10)} 秒"
    elif "Access denied" in str(last_error):
        error_message += f"\n访问被拒绝，请检查用户名 {db_config['user']} 和密码是否正确"
    elif "Unknown database" in str(last_error):
        error_message += f"\n未知数据库 {db_config['database']}，请确认数据库名称是否正确"
    raise Exception(error_message)

@mcp.tool()
async def execute_query(query: str, params: Optional[List[Any]] = None, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """执行SQL查询语句，返回查询结果

    Args:
        query: SQL查询语句
        params: 查询参数，用于参数化查询，防止SQL注入
        db_config: 数据库连接配置参数，如果为None则使用默认配置

    Returns:
        包含查询结果的字典
    """
    if not query:
        return {"error": "查询语句不能为空"}
    
    if params is None:
        params = []
    
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        
        # 判断是否是需要返回结果集的查询
        query_upper = query.strip().upper()
        if query_upper.startswith("SELECT") or query_upper.startswith("SHOW") or query_upper.startswith("DESCRIBE") or query_upper.startswith("EXPLAIN"):
            results = cursor.fetchall()
            return {
                "success": True,
                "rows": results,
                "row_count": len(results)
            }
        else:
            # 对于非查询性质的SQL，如INSERT, UPDATE, DELETE等
            conn.commit()
            return {
                "success": True,
                "affected_rows": cursor.rowcount,
                "last_insert_id": cursor.lastrowid
            }
    except Error as e:
        error_message = f"执行查询失败: {str(e)}"
        if "Unknown column" in str(e):
            error_message += "\n原因：查询中包含未知的列名"
        elif "Table" in str(e) and "doesn't exist" in str(e):
            error_message += "\n原因：查询的表不存在"
        elif "Syntax error" in str(e):
            error_message += "\n原因：SQL语法错误"
        return {"error": error_message, "query": query}
    except Exception as e:
        return {"error": f"执行过程中发生未知错误: {str(e)}", "query": query}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@mcp.tool()
async def list_tables(database_name: Optional[str] = None, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """列出指定数据库中的所有表
    
    Args:
        database_name: 数据库名称，如果为None则使用默认数据库
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        包含表列表的字典
    """
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor()
        
        # 如果指定了数据库名称，查询指定数据库的表
        if database_name:
            cursor.execute(f"SHOW TABLES FROM {database_name}")
        else:
            cursor.execute("SHOW TABLES")
            
        tables = [table[0] for table in cursor.fetchall()]
        
        return {
            "success": True,
            "database": database_name or conn.database,
            "tables": tables,
            "count": len(tables)
        }
    except Error as e:
        error_message = f"获取表列表失败: {str(e)}"
        if "Access denied" in str(e):
            error_message += "\n原因：当前用户没有足够权限执行SHOW TABLES命令"
        elif "Unknown database" in str(e):
            error_message += f"\n原因：数据库 {database_name} 不存在"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"获取表列表时发生未知错误: {str(e)}"}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@mcp.tool()
async def describe_table(table_name: str, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """获取表结构
    
    Args:
        table_name: 表名
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        包含表结构信息的字典
    """
    if not table_name:
        return {"error": "表名不能为空"}
        
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        return {
            "success": True,
            "table": table_name,
            "columns": columns
        }
    except Error as e:
        error_message = f"获取表结构失败: {str(e)}"
        if "doesn't exist" in str(e):
            error_message += f"\n原因：表 {table_name} 不存在"
        elif "Access denied" in str(e):
            error_message += "\n原因：当前用户没有足够权限查看表结构"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"获取表结构时发生未知错误: {str(e)}"}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@mcp.tool()
async def create_table(table_name: str, columns_def: str, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """创建新表
    
    Args:
        table_name: 表名
        columns_def: 列定义，例如 "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), age INT"
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        包含创建结果的字典
    """
    if not table_name or not columns_def:
        return {"error": "表名和列定义不能为空"}
        
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor()
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        cursor.execute(create_sql)
        conn.commit()
        return {
            "success": True,
            "message": f"表 {table_name} 创建成功"
        }
    except Error as e:
        error_message = f"创建表失败: {str(e)}"
        if "already exists" in str(e):
            error_message += f"\n原因：表 {table_name} 已经存在"
        elif "Access denied" in str(e):
            error_message += "\n原因：当前用户没有创建表的权限"
        elif "syntax error" in str(e).lower():
            error_message += f"\n原因：列定义 '{columns_def}' 存在语法错误"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"创建表时发生未知错误: {str(e)}"}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@mcp.tool()
async def insert_data(table_name: str, data: Dict[str, Any], db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """向表中插入数据
    
    Args:
        table_name: 表名
        data: 要插入的数据，字段名和值的字典
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        包含插入结果的字典
    """
    if not table_name or not data:
        return {"error": "表名和数据不能为空"}
        
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor()
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())
        
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(insert_sql, values)
        conn.commit()
        
        return {
            "success": True,
            "inserted_id": cursor.lastrowid,
            "message": f"数据成功插入到表 {table_name}"
        }
    except Error as e:
        error_message = f"插入数据失败: {str(e)}"
        if "doesn't exist" in str(e):
            error_message += f"\n原因：表 {table_name} 不存在"
        elif "Unknown column" in str(e):
            error_message += "\n原因：插入数据中包含表中不存在的列"
        elif "cannot be null" in str(e):
            error_message += "\n原因：某个NOT NULL字段被设置为NULL值"
        elif "Duplicate entry" in str(e):
            error_message += "\n原因：插入的数据违反了唯一键约束"
        elif "Data too long" in str(e):
            error_message += "\n原因：插入的数据超出了字段的长度限制"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"插入数据时发生未知错误: {str(e)}"}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@mcp.tool()
async def update_data(table_name: str, data: Dict[str, Any], condition: str, params: Optional[List[Any]] = None, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """更新表中的数据
    
    Args:
        table_name: 表名
        data: 要更新的数据，字段名和值的字典
        condition: WHERE条件子句
        params: 条件参数列表
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        包含更新结果的字典
    """
    if not table_name or not data or not condition:
        return {"error": "表名、数据和条件不能为空"}
    
    if params is None:
        params = []
        
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values()) + params
        
        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        cursor.execute(update_sql, values)
        conn.commit()
        
        return {
            "success": True,
            "affected_rows": cursor.rowcount,
            "message": f"表 {table_name} 中的数据更新成功"
        }
    except Error as e:
        error_message = f"更新数据失败: {str(e)}"
        if "doesn't exist" in str(e):
            error_message += f"\n原因：表 {table_name} 不存在"
        elif "Unknown column" in str(e):
            error_message += "\n原因：更新数据中包含表中不存在的列"
        elif "cannot be null" in str(e):
            error_message += "\n原因：某个NOT NULL字段被设置为NULL值"
        elif "Duplicate entry" in str(e):
            error_message += "\n原因：更新后的数据违反了唯一键约束"
        elif "Data too long" in str(e):
            error_message += "\n原因：更新的数据超出了字段的长度限制"
        elif "syntax error" in str(e).lower():
            error_message += f"\n原因：WHERE条件 '{condition}' 存在语法错误"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"更新数据时发生未知错误: {str(e)}"}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@mcp.tool()
async def delete_data(table_name: str, condition: str, params: Optional[List[Any]] = None, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """从表中删除数据
    
    Args:
        table_name: 表名
        condition: WHERE条件子句
        params: 条件参数列表
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        包含删除结果的字典
    """
    if not table_name or not condition:
        return {"error": "表名和条件不能为空"}
    
    if params is None:
        params = []
        
    try:
        conn = get_connection(db_config)
        cursor = conn.cursor()
        
        delete_sql = f"DELETE FROM {table_name} WHERE {condition}"
        cursor.execute(delete_sql, params)
        conn.commit()
        
        return {
            "success": True,
            "affected_rows": cursor.rowcount,
            "message": f"从表 {table_name} 中删除数据成功"
        }
    except Error as e:
        error_message = f"删除数据失败: {str(e)}"
        if "doesn't exist" in str(e):
            error_message += f"\n原因：表 {table_name} 不存在"
        elif "syntax error" in str(e).lower():
            error_message += f"\n原因：WHERE条件 '{condition}' 存在语法错误" 
        elif "foreign key constraint fails" in str(e):
            error_message += "\n原因：删除操作违反了外键约束"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"删除数据时发生未知错误: {str(e)}"}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@mcp.tool()
async def use_database(database_name: str, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """切换到指定的数据库
    
    Args:
        database_name: 数据库名称
        db_config: 数据库连接配置参数，如果为None则使用默认配置
        
    Returns:
        包含切换结果的字典
    """
    if not database_name:
        return {"error": "数据库名称不能为空"}
    
    try:
        # 创建新的配置
        if db_config is None:
            if GLOBAL_DB_CONFIG is not None:
                db_config = GLOBAL_DB_CONFIG.copy()
            else:
                db_config = DEFAULT_DB_CONFIG.copy()
        else:
            db_config = db_config.copy()
        
        # 更新数据库名称
        db_config["database"] = database_name
        
        # 测试连接
        conn = get_connection(db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        # 更新全局配置
        global GLOBAL_DB_CONFIG
        if GLOBAL_DB_CONFIG is not None:
            GLOBAL_DB_CONFIG["database"] = database_name
        
        return {
            "success": True,
            "message": f"已切换到数据库 {database_name}",
            "current_database": current_db
        }
    except Error as e:
        error_message = f"切换数据库失败: {str(e)}"
        if "Unknown database" in str(e):
            error_message += f"\n原因：数据库 {database_name} 不存在"
        elif "Access denied" in str(e):
            error_message += "\n原因：当前用户没有访问该数据库的权限"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"切换数据库时发生未知错误: {str(e)}"}

if __name__ == "__main__":
    # 从命令行参数获取配置
    GLOBAL_DB_CONFIG = get_config_from_args()
    
    # 修改传输方式以适应 Cursor 环境，比如使用 'ws' 传输
    mcp.run(transport='stdio')
    