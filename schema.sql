-- =====================================================================
-- 粤教服务 · 多智能体系统 数据库结构
-- 共 12 张表：sys_user + 学生侧4张 + 员工侧3张 + 客服侧3张 + conversation_log
-- 严格对齐《sql设计草稿.txt》，补充 conversation_log（对话记录表）
-- =====================================================================

-- 统一用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,               -- 用户名/登录账号
    password_hash TEXT NOT NULL,          -- 加密后的密码
    real_name TEXT NOT NULL,              -- 真实姓名
    user_type TEXT NOT NULL,              -- 用户大类（STUDENT 学生 / EMPLOYEE 员工）
    employee_role TEXT,                   -- 员工角色（仅当 user_type='EMPLOYEE' 时有效：普通员工/领导/管理员）
    department TEXT,                      -- 所属部门/院系
    contact_info TEXT,                    -- 联系方式（手机号/邮箱）
    status TEXT DEFAULT '正常',            -- 账号状态（正常/禁用）
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- 留学生智能管家 Agent 相关表
-- =====================================================================

-- 学生行政服务表（请假、考务等申请）
CREATE TABLE IF NOT EXISTS student_admin_service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,          -- 学生ID
    service_type TEXT NOT NULL,           -- 服务类型（请假/考务查询）
    start_time DATETIME,                  -- 开始时间（请假用）
    end_time DATETIME,                    -- 结束时间（请假用）
    reason TEXT,                          -- 申请事由
    status TEXT DEFAULT '待审批',          -- 审批状态（待审批/已通过/已驳回）
    approver_id INTEGER,                  -- 审批人/班主任ID
    related_academic_id INTEGER,          -- 关联教务数据ID（DDL/考试ID）
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 心理健康画像表
CREATE TABLE IF NOT EXISTS student_psych_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL UNIQUE,   -- 学生ID（唯一）
    latest_emotion_tag TEXT,              -- 最新情绪标签（焦虑/平稳等）
    emotion_score INTEGER,                -- 情绪分值（0-100）
    last_interaction_time DATETIME,       -- 最近一次交互时间
    emotion_history TEXT,                 -- 历史情绪波动（JSON字符串）
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 心理预警表
CREATE TABLE IF NOT EXISTS student_psych_alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    trigger_reason TEXT NOT NULL,         -- 触发原因（AI提取的关键词/原句）
    risk_level TEXT NOT NULL,             -- 风险等级（高/中/低）
    status TEXT DEFAULT '未处理',          -- 处理状态（未处理/跟进中/已解除）
    teacher_id INTEGER,                   -- 负责跟进的老师ID
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 售后反馈工单表
CREATE TABLE IF NOT EXISTS student_feedback_ticket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    content TEXT NOT NULL,                -- 投诉/反馈内容摘要
    detail TEXT,                          -- 详细反馈内容
    status TEXT DEFAULT '待处理',          -- 处理进度（待处理/处理中/已解决）
    solution TEXT,                        -- 最终解决方案
    is_notified INTEGER DEFAULT 0,        -- 是否已通知学生（0否 1是）
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- 企业员工智能业务助手 Agent 相关表
-- =====================================================================

-- 意向客户表（销售线索与跟进）
CREATE TABLE IF NOT EXISTS crm_lead (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,          -- 客户姓名
    contact_info TEXT,                    -- 联系方式
    background_info TEXT,                 -- 客户背景与档案
    follow_up_history TEXT,               -- 历史跟进记录（JSON/长文本）
    status TEXT DEFAULT '新增意向',        -- 流转状态（新增意向/跟进中/已签约/已流失）
    owner_employee_id INTEGER NOT NULL,   -- 负责员工ID
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 员工日报表
CREATE TABLE IF NOT EXISTS employee_daily_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    report_date DATE NOT NULL,            -- 日报所属日期
    content TEXT NOT NULL,                -- 结构化后的日报文本
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 学生成绩表
CREATE TABLE IF NOT EXISTS student_score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_name TEXT NOT NULL,            -- 课程名称
    score REAL NOT NULL,                  -- 成绩（REAL支持小数）
    semester TEXT,                        -- 学期
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- 客服与活动 Agent 相关表
-- =====================================================================

-- 课程与项目表
CREATE TABLE IF NOT EXISTS course_project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,           -- 项目/课程名称
    category TEXT,                        -- 类别（语言培训/背景提升/硕博连读等）
    description TEXT,                     -- 项目详情介绍
    target_audience TEXT                  -- 适合人群/学历要求
);

-- 活动与讲座表
CREATE TABLE IF NOT EXISTS event_lecture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,             -- 活动/讲座名称
    event_type TEXT,                      -- 类型（线上/线下）
    start_time DATETIME NOT NULL,         -- 开始时间
    location TEXT,                        -- 地点或线上链接
    max_participants INTEGER,             -- 最大报名人数
    current_participants INTEGER DEFAULT 0 -- 当前报名人数
);

-- 活动报名表
CREATE TABLE IF NOT EXISTS event_registration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,            -- 关联活动ID
    customer_id INTEGER NOT NULL,         -- 报名客户ID
    status TEXT DEFAULT '已报名',          -- 报名状态
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event_lecture(id)
);

-- =====================================================================
-- 补充：对话记录表（心理画像的情绪数据来源）
-- =====================================================================
CREATE TABLE IF NOT EXISTS conversation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    agent_type TEXT NOT NULL,             -- 哪个Agent产生的对话
    user_input TEXT NOT NULL,             -- 用户输入
    ai_output TEXT,                       -- AI回复
    emotion_tag TEXT,                     -- 本次对话情绪标签（供心理画像累积）
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
