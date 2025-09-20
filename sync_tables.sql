-- Tabla para dispositivos de usuario
CREATE TABLE IF NOT EXISTS user_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(50), -- 'mobile', 'web', 'desktop'
    platform VARCHAR(50), -- 'ios', 'android', 'web'
    app_version VARCHAR(50),
    last_sync TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, device_id)
);

-- Tabla para logs de sincronización
CREATE TABLE IF NOT EXISTS sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL, -- 'pull', 'push', 'conflict'
    records_count INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    sync_duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla para conflictos de sincronización
CREATE TABLE IF NOT EXISTS sync_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    local_data JSONB,
    server_data JSONB,
    conflict_type VARCHAR(50), -- 'update_conflict', 'delete_conflict', 'version_conflict'
    resolution VARCHAR(50), -- 'local_wins', 'server_wins', 'manual'
    resolved_by UUID REFERENCES auth.users(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, device_id, table_name, record_id)
);

-- Tabla para metadatos de sincronización por tabla
CREATE TABLE IF NOT EXISTS sync_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    last_sync_version INTEGER DEFAULT 0,
    last_sync_timestamp TIMESTAMPTZ,
    record_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, table_name)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_user_devices_user_id ON user_devices(user_id);
CREATE INDEX IF NOT EXISTS idx_user_devices_device_id ON user_devices(device_id);
CREATE INDEX IF NOT EXISTS idx_user_devices_active ON user_devices(is_active);

CREATE INDEX IF NOT EXISTS idx_sync_logs_user_id ON sync_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_logs_device_id ON sync_logs(device_id);
CREATE INDEX IF NOT EXISTS idx_sync_logs_table_name ON sync_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_sync_logs_created_at ON sync_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_sync_conflicts_user_id ON sync_conflicts(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_conflicts_device_id ON sync_conflicts(device_id);
CREATE INDEX IF NOT EXISTS idx_sync_conflicts_table_name ON sync_conflicts(table_name);
CREATE INDEX IF NOT EXISTS idx_sync_conflicts_unresolved ON sync_conflicts(resolved_at) WHERE resolved_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_sync_metadata_user_id ON sync_metadata(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_metadata_table_name ON sync_metadata(table_name);

-- Políticas RLS (Row Level Security)
ALTER TABLE user_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_conflicts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_metadata ENABLE ROW LEVEL SECURITY;

-- Políticas para user_devices
CREATE POLICY "Users can manage their own devices" ON user_devices
    FOR ALL USING (auth.uid() = user_id);

-- Políticas para sync_logs
CREATE POLICY "Users can view their own sync logs" ON sync_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own sync logs" ON sync_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Políticas para sync_conflicts
CREATE POLICY "Users can manage their own sync conflicts" ON sync_conflicts
    FOR ALL USING (auth.uid() = user_id);

-- Políticas para sync_metadata
CREATE POLICY "Users can manage their own sync metadata" ON sync_metadata
    FOR ALL USING (auth.uid() = user_id);

-- Función para limpiar logs antiguos (opcional)
CREATE OR REPLACE FUNCTION cleanup_old_sync_logs()
RETURNS void AS $$
BEGIN
    -- Eliminar logs de más de 30 días
    DELETE FROM sync_logs 
    WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- Eliminar dispositivos inactivos de más de 90 días
    DELETE FROM user_devices 
    WHERE is_active = false 
    AND updated_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar metadatos de sincronización
CREATE OR REPLACE FUNCTION update_sync_metadata(
    p_user_id UUID,
    p_table_name VARCHAR,
    p_record_count INTEGER
)
RETURNS void AS $$
BEGIN
    INSERT INTO sync_metadata (user_id, table_name, record_count, last_sync_timestamp, last_sync_version)
    VALUES (p_user_id, p_table_name, p_record_count, NOW(), 1)
    ON CONFLICT (user_id, table_name)
    DO UPDATE SET
        record_count = p_record_count,
        last_sync_timestamp = NOW(),
        last_sync_version = sync_metadata.last_sync_version + 1,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
