"""
SQLite 数据访问层
================= 功能说明：
1. 使用 Python 标准库 sqlite3 操作 SQLite 数据库。
2. 提供数据库连接方法。
3. 提供数据库表结构初始化方法。
4. 提供种子数据初始化方法。
5. 提供数据库统一就绪入口 ensure_ready()。
数据库表结构：
- 具体 DDL（CREATE TABLE）统一维护在 schema.sql 文件中。
- 本文件不直接编写 CREATE TABLE SQL，避免数据库结构分散在多个文件中。
数据库文件位置：
- 当前 Python 文件所在目录下的 yuejiao.db
- schema.sql 与本文件位于同一目录。
注意：
- SQLite 数据库文件会在第一次连接时自动创建。
- 如果 yuejiao.db 不存在，sqlite3.connect() 会创建一个新的空数据库。
- 因此，运行本项目时应确保使用的是正确的工作目录和数据库文件。
"""

from __future__ import annotations
import os
import sqlite3
from datetime import datetime, timezone

# ============================================================================
# 一、基础路径配置
# ============================================================================
# 当前 Python 文件所在目录。
# 例如：
# D:\projects\项目阶段\yuejiao\backend\db.py
# 那么：BASE_DIR =
# D:\projects\项目阶段\yuejiao\backend
#
# 使用 __file__ 获取路径，而不是依赖程序当前工作目录，
# 可以避免因为从不同目录启动程序而导致数据库路径发生变化。
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SQLite 数据库文件的绝对路径。
# 数据库文件与当前 Python 文件放在同一个目录：
#
# backend/
# ├── db.py
# ├── schema.sql
# └── yuejiao.db
DB_PATH = os.path.join(BASE_DIR, "yuejiao.db")  # 数据库路径
# 数据库表结构文件路径。
# schema.sql 中保存所有 CREATE TABLE 等数据库初始化 SQL。
# 数据库脚本的路径 里面写了数据的 crud 等 ，数据表的创建删除等等 后续直接执行该脚本
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


# ============================================================================
# 二、数据库路径与连接
# ============================================================================
def get_db_path() -> str:
    """获取当前项目实际使用的 SQLite 数据库路径。
    返回：
    str: yuejiao.db 的绝对路径。
    说明：
    其他模块如果需要知道数据库文件位置，
    应调用本方法，而不是自己重新拼接数据库路径。
    """
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    """创建并返回一个 SQLite 数据库连接。
    返回： sqlite3.Connection: SQLite 数据库连接对象。
    配置：
    1. row_factory 设置为 sqlite3.Row。
    这样查询结果既可以通过下标访问： row[0]
    也可以通过字段名访问： row["username"]
    2. 开启 SQLite 外键约束。
    SQLite 默认情况下不一定启用 FOREIGN KEY，
    因此每次建立连接后都显式执行： PRAGMA foreign_keys = ON
    注意：
    调用方负责在使用完成后关闭连接。
    推荐使用： with get_connection() as conn:
    或者使用 try/finally 确保连接关闭。
    """
    # 连接 SQLite 数据库。
    # 如果 DB_PATH 对应的数据库文件不存在，
    # sqlite3.connect() 会自动创建一个新的数据库文件。
    conn = sqlite3.connect(DB_PATH)
    # 将查询结果设置为 sqlite3.Row。
    # 这样可以通过字段名称读取数据：
    # row["id"]
    # row["username"]
    # row["real_name"]
    conn.row_factory = sqlite3.Row
    # 开启 SQLite 外键约束。
    # 例如 event_registration 表中的：
    # FOREIGN KEY (event_id)
    # REFERENCES event_lecture(id)
    # 开启后，SQLite 会对外键关系进行约束检查。
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================================
# 三、数据库表结构初始化
# ============================================================================
def init_db() -> None:
    """初始化数据库表结构。
    工作流程：
    1. 读取 schema.sql。
    2. 创建数据库连接。
    3. 执行 schema.sql 中的全部 SQL。
    4. 提交事务。
    5. 关闭数据库连接。
    说明： 数据库表结构统一维护在 schema.sql 中，因此修改表结构时主要修改 schema.sql。
    注意： schema.sql 中通常应该使用： CREATE TABLE IF NOT EXISTS ... 这样程序重复启动时不会因为表已经存在而报错。
    """
    # 读取数据库结构定义文件。
    # 使用 UTF-8 编码，确保中文字段注释和 SQL 内容正常读取。
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    # 获取数据库连接。
    conn = get_connection()
    try:
        # 执行 schema.sql 中的全部 SQL。
        # executescript() 可以一次执行多条 SQL，
        # 非常适合执行包含多个 CREATE TABLE 的 schema 文件。
        conn.executescript(schema)
        # 提交数据库结构变更。
        conn.commit()
    finally:
        # 无论初始化成功还是失败，都关闭数据库连接。
        conn.close()


# ============================================================================
# 四、数据库查询结果转换
# ============================================================================
def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    """将 SQLite 查询结果 sqlite3.Row 转换成普通 Python 字典。
    参数：row:
    sqlite3.Row 对象。
    如果没有查询到数据，可以传入 None。
    返回： dict:
    查询结果对应的字典。
    None:
    当传入 row 为 None 时返回 None。
    示例：
    row = conn.execute(
    "SELECT * FROM sys_user WHERE id = ?",
    (1,)
    ).fetchone()
    user = row_to_dict(row)
    最终结果类似：
    {
    "id": 1,
    "username": "student_zhang",
    "real_name": "张三",
    ...
    }
    这个方法主要用于：
    SQLite Row -> Python dict -> JSON/API 响应
    """
    # 没有查询到记录时，直接返回 None。
    if row is None:
        return None
    # row.keys() 获取所有字段名称，
    # 然后构造普通 Python 字典。
    return {k: row[k] for k in row.keys()}


# ============================================================================
# 五、统一时间格式
# ============================================================================
def now_str() -> str:
    """获取当前 UTC 时间，并转换为字符串。
    返回格式： YYYY-MM-DD HH:MM:SS
    示例： 2026-08-31 01:30:00
    说明：
    使用 timezone.utc 统一使用 UTC 时间，
    可以避免服务器部署在不同时区时产生时间混乱。
    注意：
    数据库中的 CURRENT_TIMESTAMP 同样通常使用 UTC 时间。
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ============================================================================
# 六、种子数据初始化
# ============================================================================
def seed_if_empty() -> None:
    """初始化数据库演示/基础种子数据。
    逻辑：
    1. 查询 sys_user 表当前是否已经存在数据。
    2. 如果已经存在数据，则认为数据库已经初始化过， 直接返回，不重复插入。
    3. 如果没有数据，则依次插入：
    - 系统用户
    - 课程与项目
    - 活动与讲座
    - 意向客户
    - 学生成绩
    - 请假申请
    - 心理画像
    说明：该方法主要用于开发环境、演示环境快速生成基础数据。
    注意,当前判断条件是： sys_user 中存在至少一条数据
    只要 sys_user 不为空，就不会再次执行整个种子数据初始化。
    """
    # 获取数据库连接。
    conn = get_connection()
    try:
        # --------------------------------------------------------------------
        # 6.1 检查数据库是否已经存在用户数据
        # --------------------------------------------------------------------
        cur = conn.execute("SELECT COUNT(*) AS c FROM sys_user")
        # fetchone() 获取第一条查询结果。
        # 因为 SELECT COUNT(*) 一定会返回一行，
        # 所以这里可以直接读取 ["c"]。
        if cur.fetchone()["c"] > 0:
            # 数据库已经存在用户数据，
            # 认为种子数据已经初始化过。
            return
        # --------------------------------------------------------------------
        # 6.2 系统用户
        # --------------------------------------------------------------------
        # 用户数据说明：
        # STUDENT：
        # 学生用户
        # EMPLOYEE：
        # 员工用户
        # employee_role：
        # 员工角色，例如：
        # - 普通员工
        # - 领导
        # password_hash：
        # 当前使用 "hash" 作为演示占位值。
        # 正式生产环境应使用真正的密码哈希算法，
        # 例如 bcrypt / Argon2 等，而不能保存明文密码。
        users = [
            (
                "student_zhang",
                "hash",
                "张三",
                "STUDENT",
                None,
                "新加坡本科班",
                "1348907728",
            ),
            (
                "student_li",
                "hash",
                "李四",
                "STUDENT",
                None,
                "新加坡本科班",
                "13800000001",
            ),
            (
                "student_wang",
                "hash",
                "王五",
                "STUDENT",
                None,
                "德国双元制班",
                "13800000002",
            ),
            (
                "emp_consultant",
                "hash",
                "陈顾问",
                "EMPLOYEE",
                "普通员工",
                "双元制事业部",
                "13900000001",
            ),
            (
                "emp_leader",
                "hash",
                "刘主任",
                "EMPLOYEE",
                "领导",
                "国际教育中心",
                "13900000002",
            ),
            (
                "emp_teacher",
                "hash",
                "赵班主任",
                "EMPLOYEE",
                "普通员工",
                "学生事务部",
                "13900000003",
            ),
        ]
        # 批量插入系统用户。
        # 使用 executemany() 可以一次插入多条数据，
        # 比逐条 execute() 更适合初始化种子数据。
        conn.executemany(
            """
        INSERT INTO sys_user (
        username,
        password_hash,
        real_name,
        user_type,
        employee_role,
        department,
        contact_info
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            users,
        )
        # --------------------------------------------------------------------
        # 6.3 课程与项目
        # --------------------------------------------------------------------
        # 每条课程数据包含：
        # 1. project_name： 项目/课程名称
        # 2. category：项目所属类别
        # 3. description： 项目详细介绍
        # 4. target_audience：
        # 目标人群/学历要求
        courses = [
            (
                "2+2 新加坡定向培养本科班",
                "新加坡本科",
                "国内两年+新加坡两年，第四年获世界排名 200-500 大学本科文凭",
                "应往届初中毕业生",
            ),
            (
                "2+2+1 本硕连读",
                "新加坡本硕",
                "2+2 本科后最快 1 年硕士，可申请 TOP200 名校",
                "应往届初中毕业生",
            ),
            (
                "0.5/1+2 新加坡定向培养本科班",
                "新加坡本科",
                "国内 0.5/1 年预科+新加坡 2 年，第三年获本科文凭",
                "高二在读、应往届高中/中职中技毕业",
            ),
            (
                "0.5/1+2+1 本硕连读",
                "新加坡本硕",
                "0.5/1+2 本科后最快 1 年硕士",
                "高二在读、应往届高中/中职中技毕业",
            ),
            (
                "6+6 酒店运营大专就业班",
                "新加坡就业",
                "6 个月理论+6 个月带薪实习，实习结束 100%推荐就业",
                "职高/中专/中职/技校满 17 岁",
            ),
            (
                "9+6 航空运营大专就业班",
                "新加坡就业",
                "9 个月理论+6 个月带薪实习，实习结束 100%推荐就业",
                "职高/中专/中职/技校满 17 岁",
            ),
            (
                "一年制专升本",
                "学历提升",
                "国外名校专升本 1-1.5 年，回国受教育部认证",
                "专科毕业生",
            ),
            (
                "一年制本升硕",
                "学历提升",
                "国外名校本升硕仅需一年，回国受教育部认证",
                "本科毕业生",
            ),
            (
                "德国双元制职业教育",
                "德国双元制",
                "企业+学校双元培训，免学费享补贴，可申永居",
                "18-35 岁高中及以上，动手能力强",
            ),
        ]
        # 批量写入课程/项目数据。
        conn.executemany(
            """
        INSERT INTO course_project (
        project_name,
        category,
        description,
        target_audience
        )
        VALUES (?, ?, ?, ?)
        """,
            courses,
        )
        # --------------------------------------------------------------------
        # 6.4 活动与讲座
        # --------------------------------------------------------------------
        # 活动字段说明：
        # event_name： 活动名称
        # event_type： 活动类型，例如线上/线下
        # start_time：活动开始时间
        # location： 线上会议地址或线下活动地点
        # max_participants： 最大报名人数
        events = [
            (
                "新加坡定向培养留学分享会（线上）",
                "线上",
                "2026-09-10 19:00",
                "腾讯会议",
                100,
            ),
            (
                "招生官见面会（广州线下）",
                "线下",
                "2026-09-20 14:00",
                "广州市天河区",
                50,
            ),
            (
                "德国双元制宣讲会",
                "线上",
                "2026-09-15 20:00",
                "腾讯会议",
                80,
            ),
        ]
        # 批量插入活动数据。
        conn.executemany(
            """
        INSERT INTO event_lecture (
        event_name,
        event_type,
        start_time,
        location,
        max_participants
        )
        VALUES (?, ?, ?, ?, ?)
        """,
            events,
        )
        # --------------------------------------------------------------------
        # 6.5 CRM 意向客户
        # --------------------------------------------------------------------
        # 意向客户数据主要用于 CRM 演示。
        # owner_employee_id：表示负责跟进该客户的员工 ID。
        # 当前种子数据中设置为 4，
        # 对应前面插入的 emp_consultant。
        leads = [
            (
                "许同学",
                "13800001111",
                "19 岁，高中刚毕业，家里经济中等，想快速升学",
                '[{"time":"2026-08-20","note":"初次咨询"}]',
                "跟进中",
                4,
            ),
            (
                "曹同学",
                "13800002222",
                "本科毕业，想一年制本升硕",
                '[{"time":"2026-08-22","note":"询问学费"}]',
                "新增意向",
                4,
            ),
            (
                "黄同学",
                "13800003333",
                "职高中专，17 岁，就业导向",
                "[]",
                "新增意向",
                4,
            ),
        ]
        # 批量插入 CRM 意向客户。
        conn.executemany(
            """
        INSERT INTO crm_lead (
        customer_name,
        contact_info,
        background_info,
        follow_up_history,
        status,
        owner_employee_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            leads,
        )
        # --------------------------------------------------------------------
        # 6.6 学生成绩
        # --------------------------------------------------------------------
        # student_id：
        # 学生用户在 sys_user 表中的 ID。
        # # course_name：
        # 课程名称。
        # score：
        # 学生成绩，允许使用小数。
        # # semester：
        # 所属学期。
        scores = [
            (1, "英语", 88.5, "2026 春季"),
            (1, "数学", 76.0, "2026 春季"),
            (2, "英语", 92.0, "2026 春季"),
        ]
        # 批量插入学生成绩。
        conn.executemany(
            """
        INSERT INTO student_score (
        student_id,
        course_name,
        score,
        semester
        )
        VALUES (?, ?, ?, ?)
        """,
            scores,
        )
        # --------------------------------------------------------------------
        # 6.7 学生请假申请
        # --------------------------------------------------------------------
        # 创建一条学生请假申请。
        # # student_id = 1：
        # 对应 student_zhang。
        # # approver_id = 6：
        # 对应 emp_teacher。
        # # status：
        # 当前状态为“待审批”。
        conn.execute(
            """
        INSERT INTO student_admin_service (
        student_id,
        service_type,
        start_time,
        end_time,
        reason,
        status,
        approver_id
        )
        VALUES (
        1,
        '请假',
        '2026-09-01',
        '2026-09-02',
        '身体不适',
        '待审批',
        6
        )
        """
        )
        # --------------------------------------------------------------------
        # 6.8 学生心理画像
        # --------------------------------------------------------------------
        # 创建学生初始心理画像。
        # # latest_emotion_tag：
        # 当前最新情绪标签。
        # # emotion_score：
        # 情绪评分。
        # # emotion_history：
        # 历史情绪记录。
        # # 当前使用空 JSON 数组作为初始历史：
        # []
        conn.execute(
            """
        INSERT INTO student_psych_profile (
        student_id,
        latest_emotion_tag,
        emotion_score,
        emotion_history
        )
        VALUES (
        1,
        '平稳',
        20,
        '[]'
        )
        """
        )
        # --------------------------------------------------------------------
        # 6.9 提交所有种子数据
        # --------------------------------------------------------------------
        # 前面所有 INSERT 都属于当前事务。
        # 在这里统一提交，确保数据正式写入数据库。
        conn.commit()
    finally:
        # 无论执行过程中是否出现异常，都关闭数据库连接。
        conn.close()


# ============================================================================
# 七、数据库统一初始化入口
# ============================================================================
def ensure_ready() -> None:
    """确保数据库已经完成初始化并具备基础数据。
    执行顺序：
    第一步：
    init_db()
    初始化数据库表结构。
    第二步：
    seed_if_empty()
    如果数据库没有用户数据，则写入种子数据。
    项目启动时只需要调用： ensure_ready()
    即可完成数据库初始化。
    """
    # 第一步：创建数据库表结构。 只是创建了数据表，但是数据表中还不存在数据
    init_db()
    # 第二步：检查并写入种子数据。
    seed_if_empty()


ensure_ready()
