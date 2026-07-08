# 🛡️ Acko Insurance Smart AI & Analytics Platform

An end-to-end, digital-first InsurTech prototype combining conversational AI orchestration and predictive machine learning models.This platform replaces traditional insurance friction points with sub-second automated processing systems built over scalable database infrastructure.
---
Dashboard.png

## 🚀 Key Architectural Modules

### 💬 Module 1: Policy Intelligence Chatbot (Core RAG)
* **Purpose:** A 24/7 conversational assistant that instantly parses queries and surfaces accurate answers grounded in real Acko insurance contract clauses.
* **Architecture:** Uses a Retrieval-Augmented Generation (RAG) loop.It chunks and vectorizes reference policy PDFs using recursive character splitting, embeds them into local **ChromaDB** index slots, queries contextual neighbors via semantic vector matching, and formats bulleted responses using the **Google Gemini API**.
* **Audit Pipeline:** Automatically records transaction variables and customer conversations back to local **PostgreSQL** log schemas.

### 📊 Module 2: Premium Quote Predictor
* **Purpose:** Provides instantaneous, algorithmic pricing estimates based on vehicle properties and driver risk histories without requiring manual agent assistance.
* **Architecture:** Uses a **Scikit-learn Random Forest Regressor** trained on a synthetic insurance dataset matching Indian transit risks.Features parameters like Vehicle Segment (Car vs. Bike), Manufacturing Year, Insured Declared Value (IDV), and accrued No Claim Bonus (NCB %) percentages.
* **Dual-Stream Verification Engine:** Features an in-app **Active Session Audit Log** alongside real-time **PostgreSQL aggregations** to visually confirm backend database pipeline writes inside the app dashboard interface.

---

## 🛠️ Technology Stack & Tools

* **Frontend Framework:** Streamlit (Custom Responsive UI Layer)
* **AI Orchestration & Vector Core:** ChromaDB Vector Store & Google Gemini LLM Engine 
* **Predictive Analytics:** Scikit-learn Random Forest (Tabular Ensemble Regressor Machine) 
* **Relational Database Storage:** PostgreSQL Server connected via SQLAlchemy ORM pipelines 
* **Languages & Scripting:** Python 3.10+, SQL (DDL Schema Core Architecture)

---

## 🗄️ Database Table Schema

All frontend interaction sequences register directly into a central PostgreSQL database instance.

```sql
-- 1. Premium Quotation Logging Table Schema
CREATE TABLE quotations (
    id SERIAL PRIMARY KEY,
    vehicle_type VARCHAR(10),        -- car / bike
    vehicle_make VARCHAR(50),        -- Brand Make
    vehicle_model VARCHAR(80),       -- Model Name
    manufacturing_year INT,          -- Calendar Year
    city VARCHAR(80),                -- City Location
    idv FLOAT,                       -- Insured Declared Value
    ncb_percent INT,                 -- No Claim Bonus discount
    annual_premium FLOAT,            -- ML Model Output Predicted Payout
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. RAG Interaction Audit Logs Table Schema
CREATE TABLE chat_logs (
    id SERIAL PRIMARY KEY,
    intent VARCHAR(30),              -- policy_qa
    question TEXT,                   -- Raw User Input Query
    retrieved_source VARCHAR(255),   -- Reference PDF Source File Match
    response TEXT,                   -- Formatted AI Output Reply Text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
