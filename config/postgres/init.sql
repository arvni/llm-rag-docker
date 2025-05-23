-- Initialize PostgreSQL database for RAG system
CREATE DATABASE ragdb;
CREATE USER raguser WITH ENCRYPTED PASSWORD 'ragpass123';
GRANT ALL PRIVILEGES ON DATABASE ragdb TO raguser;

\c ragdb;

-- Create tables for document metadata
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP,
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB,
    checksum VARCHAR(64)
);

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES chat_sessions(session_id),
    message_type VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    model_used VARCHAR(100),
    context_used TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for better performance
CREATE INDEX idx_documents_filename ON documents(filename);
CREATE INDEX idx_documents_upload_date ON documents(upload_date);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO raguser;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO raguser;