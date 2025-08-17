-- PostgreSQL初始化脚本
-- 为MIRIX记忆系统创建必要的表结构和扩展

-- 创建vector扩展（用于向量相似度搜索）
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建记忆存储表
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN ('core', 'episodic', 'semantic', 'procedural', 'resource', 'knowledge')),
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embedding维度
    metadata JSONB DEFAULT '{}',
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    retention_until TIMESTAMP WITH TIME ZONE, -- 记忆保留截止时间
    tags TEXT[] DEFAULT '{}'
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_memories_session_id ON memories(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_retention ON memories(retention_until);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memories_metadata ON memories USING GIN(metadata);

-- 向量相似度搜索索引
CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 全文搜索索引
CREATE INDEX IF NOT EXISTS idx_memories_content_fts ON memories USING GIN(to_tsvector('english', content));

-- 创建用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(user_id, session_id)
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity);

-- 创建用户画像表
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    cognitive_profile JSONB DEFAULT '{}',
    knowledge_profile JSONB DEFAULT '{}',
    interaction_profile JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- 创建记忆关系表（用于记忆间的关联）
CREATE TABLE IF NOT EXISTS memory_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_memory_id UUID REFERENCES memories(id) ON DELETE CASCADE,
    target_memory_id UUID REFERENCES memories(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    strength FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_memory_relationships_source ON memory_relationships(source_memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_relationships_target ON memory_relationships(target_memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_relationships_type ON memory_relationships(relationship_type);

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入默认配置
INSERT INTO system_config (key, value, description) VALUES
('memory_retention_policy', '{"core": -1, "episodic": 365, "semantic": -1, "procedural": -1, "resource": 180, "knowledge": -1}', 'Memory retention policy in days (-1 means permanent)'),
('similarity_thresholds', '{"default": 0.7, "strict": 0.85, "loose": 0.5}', 'Similarity thresholds for memory retrieval'),
('max_memory_per_type', '{"core": 1000, "episodic": 10000, "semantic": 50000, "procedural": 5000, "resource": 20000, "knowledge": 100000}', 'Maximum memories per type per user')
ON CONFLICT (key) DO NOTHING;

-- 创建统计视图
CREATE OR REPLACE VIEW memory_stats AS
SELECT 
    user_id,
    memory_type,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence,
    MIN(created_at) as first_memory,
    MAX(created_at) as last_memory
FROM memories 
GROUP BY user_id, memory_type;

-- 创建清理过期记忆的函数
CREATE OR REPLACE FUNCTION cleanup_expired_memories()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM memories 
    WHERE retention_until IS NOT NULL 
    AND retention_until < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 创建更新记忆保留期限的函数
CREATE OR REPLACE FUNCTION update_memory_retention()
RETURNS VOID AS $$
DECLARE
    config_data JSONB;
    memory_record RECORD;
    retention_days INTEGER;
BEGIN
    -- 获取保留策略配置
    SELECT value INTO config_data 
    FROM system_config 
    WHERE key = 'memory_retention_policy';
    
    -- 更新所有没有设置保留期限的记忆
    FOR memory_record IN 
        SELECT id, memory_type, created_at 
        FROM memories 
        WHERE retention_until IS NULL
    LOOP
        retention_days := (config_data ->> memory_record.memory_type)::INTEGER;
        
        IF retention_days > 0 THEN
            UPDATE memories 
            SET retention_until = memory_record.created_at + (retention_days || ' days')::INTERVAL
            WHERE id = memory_record.id;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器，自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化完成日志
INSERT INTO system_config (key, value, description) VALUES
('db_initialized_at', to_jsonb(NOW()), 'Database initialization timestamp')
ON CONFLICT (key) DO UPDATE SET value = to_jsonb(NOW());

COMMIT;