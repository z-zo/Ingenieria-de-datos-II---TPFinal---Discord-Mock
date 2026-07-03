 -- Inicio Docker: docker compose up -d
 -- Ingreso al docker de Scylla: docker exec -it discord_scylla cqlsh

-- 1. Creación del Keyspace (simil a la DB en mongo)
CREATE KEYSPACE IF NOT EXISTS discord_mock 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}; -- por limite nuestro, pero el estandar es 3

USE discord_mock;

-- 2. Estructura de la Tabla (Particionamiento para evitar Hot Partitions)
-- Nota: 'bucket' usa DATE (forzado al día 1 del mes en Python) para optimización.
CREATE TABLE IF NOT EXISTS messages (
    channel_id BIGINT,
    bucket DATE,        
    message_id TIMEUUID, 
    author_id BIGINT,
    content TEXT,
    PRIMARY KEY ((channel_id, bucket), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);