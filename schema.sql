-- Enable UUID extension if not already active
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'manager')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. QUOTATIONS TABLE
CREATE TABLE quotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(10) NOT NULL CHECK (vehicle_type IN ('car', 'bike')),
    vehicle_make VARCHAR(50) NOT NULL,
    vehicle_model VARCHAR(80) NOT NULL,
    manufacturing_year INT NOT NULL,
    city VARCHAR(80) NOT NULL,
    idv FLOAT NOT NULL,
    ncb_percent INT NOT NULL,
    predicted_premium FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. CLAIMS TABLE
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(10) NOT NULL CHECK (vehicle_type IN ('car', 'bike')),
    policy_number VARCHAR(50) NOT NULL,
    incident_date DATE NOT NULL,
    damage_type VARCHAR(50) NOT NULL,
    affected_parts VARCHAR(200) NOT NULL,
    damage_severity VARCHAR(20) NOT NULL CHECK (damage_severity IN ('minor', 'moderate', 'major')),
    image_s3_key VARCHAR(255),
    form_s3_key VARCHAR(255),
    predicted_amount FLOAT NOT NULL,
    approval_probability FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'review')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. CHAT_LOGS TABLE
CREATE TABLE chat_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    intent VARCHAR(30) NOT NULL,
    question TEXT NOT NULL,
    retrieved_source VARCHAR(255),
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM quotations WHERE city = 'Chennai';