# database.py
# 导入 Python 内置的 sqlite3 模块，用于操作 SQLite 数据库
import sqlite3


# 创建数据库
def create_database():
    # 连接 SQLite 数据库
    # 如果 demo.db 文件不存在，SQLite 会自动创建该数据库文件
    conn = sqlite3.connect("demo.db")
    # 后续通过 cursor 执行 SQL 语句
    # cursor = conn.cursor()
    # 创建 users 用户表
    # IF NOT EXISTS 表示：如果 users 表已经存在，就不会重复创建
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            age INTEGER,
            gender TEXT,
            city TEXT
        )
        """
    )
    # 创建 orders 订单表
    # IF NOT EXISTS 表示：如果 orders 表已经存在，就不会重复创建
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_name TEXT,
            amount REAL,
            order_date TEXT
        )
        """
    )
    # 批量向 users 用户表中插入数据
    # executemany() 可以一次执行多条 INSERT SQL 语句
    conn.executemany(
        """
        INSERT INTO users
        (username, age, gender, city)
        VALUES (?, ?, ?, ?)
        """,
        [
            # 用户 1
            ("张三", 20, "男", "北京"),
            # 用户 2
            ("李四", 25, "女", "上海"),
            # 用户 3
            ("王五", 30, "男", "北京"),
            # 用户 4
            ("赵六", 28, "女", "广州"),
            # 用户 5
            ("孙七", 35, "男", "上海"),
        ],
    )
    # 批量向 orders 订单表中插入数据
    # executemany() 可以一次执行多条 INSERT SQL 语句
    conn.executemany(
        """
        INSERT INTO orders
        (user_id, product_name, amount, order_date)
        VALUES (?, ?, ?, ?)
        """,
        [
            # user_id 表示订单属于哪个用户
            # 这里的 user_id 对应 users 表中的 id
            # 张三购买 iPhone
            (1, "iPhone", 6999, "2026-01-10"),
            # 李四购买 MacBook
            (2, "MacBook", 12999, "2026-02-11"),
            # 王五购买 iPhone
            (3, "iPhone", 7999, "2026-03-12"),
            # 赵六购买 Huawei
            (4, "Huawei", 5999, "2026-04-13"),
            # 孙七购买 MacBook
            (5, "MacBook", 13999, "2026-05-14"),
        ],
    )
    # 提交事务
    # 将前面 INSERT 的数据真正保存到数据库文件中
    conn.commit()
    # 关闭数据库连接
    # 数据库操作完成后，需要释放数据库连接资源
    conn.close()


# 判断当前文件是否是直接运行的主程序
# 如果 database.py 被其他 Python 文件 import，
# 那么下面的代码不会自动执行
if __name__ == "__main__":
    # 调用 create_database() 函数
    # 创建数据库、创建数据表，并插入测试数据
    create_database()