-- 切换到测试库
USE db_project_test;

-- 创建游戏销量表（game_sales）
CREATE TABLE game_sales (
    Rank INT PRIMARY KEY COMMENT '销量排名（唯一标识）',
    Name VARCHAR(255) NOT NULL COMMENT '游戏名称',
    Platform VARCHAR(50) NOT NULL COMMENT '发行平台（如PS4、Switch）',
    Year INT NOT NULL CHECK (Year BETWEEN 1980 AND 2024) COMMENT '发行年份',
    Genre VARCHAR(50) NOT NULL COMMENT '游戏类型（如Action、RPG）',
    Publisher VARCHAR(100) NOT NULL COMMENT '发行商',
    NA_Sales DECIMAL(5,2) NOT NULL CHECK (NA_Sales >= 0) COMMENT '北美销量（百万）',
    EU_Sales DECIMAL(5,2) NOT NULL CHECK (EU_Sales >= 0) COMMENT '欧洲销量（百万）',
    JP_Sales DECIMAL(5,2) NOT NULL CHECK (JP_Sales >= 0) COMMENT '日本销量（百万）',
    Other_Sales DECIMAL(5,2) NOT NULL CHECK (Other_Sales >= 0) COMMENT '其他地区销量（百万）',
    Global_Sales DECIMAL(6,2) NOT NULL CHECK (Global_Sales >= 0) COMMENT '全球总销量（百万）',
    -- 唯一约束：避免同一游戏在同一平台+同一年份重复
    UNIQUE KEY uk_game_platform_year (Name, Platform, Year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='游戏销量数据表';