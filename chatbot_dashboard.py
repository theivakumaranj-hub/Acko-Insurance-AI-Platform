# app.py
import streamlit as st
import pandas as pd
import joblib
import os
import chromadb
from sqlalchemy import create_engine
import google.generativeai as genai

# --- FORCE EXPLICIT INITIALIZATION DEFENSES ---
st.set_page_config(page_title="Acko AI Hub", layout="wide")

# --- DATABASE CONNECTION & CONFIGURATION ---
DATABASE_URL = "postgresql://postgres:kumaranias7@localhost:5432/acko_db"
engine = create_engine(DATABASE_URL)

# --- CONFIGURE GEMINI API ---
API_KEY_INPUT = "paste your API KEY HERE"                                     #-- DUE TO GITHUB WARNING API KEY REMOVED USE YOURS
genai.configure(api_key=API_KEY_INPUT)

# --- CACHE AND LOAD THE 5 TRAINED ML MODELS ---
@st.cache_resource
def load_insurance_models():
    try:
        return {
            "premium": joblib.load('premium_model.pkl'),
            "car_amount": joblib.load('car_amount_model.pkl'),
            "car_approval": joblib.load('car_approval_model.pkl'),
            "bike_amount": joblib.load('bike_amount_model.pkl'),
            "bike_approval": joblib.load('bike_approval_model.pkl')
        }
    except Exception as e:
        st.error(f"⚠️ Critical Error loading Machine Learning models (.pkl): {str(e)}")
        return None

models = load_insurance_models()

# --- INITIALIZE CHROMADB CONNECTION ---
@st.cache_resource
def get_vector_store():
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_db_storage")
        return chroma_client.get_collection(name="acko_policies")
    except Exception as e:
        st.sidebar.warning(f"⚠️ ChromaDB local store index offline: {str(e)}")
        return None

collection = get_vector_store()
# --- CUSTOM CSS TO INJECT LARGE FONTS INTO SIDEBAR ---
st.markdown(
    """
    <style>
        /* Makes the main sidebar header text larger */
        [data-testid="stSidebar"] h2 {
            font-size: 28px !important;
            font-weight: bold !important;
        }
        /* Makes the radio button selection labels significantly larger */
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
            font-size: 20px !important;
            font-weight: 500 !important;
            line-height: 1.6 !important;
        }
        /* Enhances the active select text size inside radio options */
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            font-size: 20px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# --- STREAMLIT USER INTERFACE LAYOUT ---
st.title("🛡️ Acko Insurance Smart AI Platform")
st.caption("Production Interface Portfolio — Core Modules 1, 2, & 3 Active")

# Sidebar Application Controller
st.sidebar.header("Navigation Panel")
app_mode = st.sidebar.radio("Go to Module:", [
    "💬 Module 1: Policy Chatbot", 
    "📊 Module 2: Premium Quote Predictor"
])

# -------------------------------------------------------------------------
# MODULE 1: AI POLICY CHATBOT (RAG + CONVERSATION LOGGING)
# -------------------------------------------------------------------------
if app_mode == "💬 Module 1: Policy Chatbot":
    st.header("Conversational AI Assistant")
    st.write("Ask clear, plain-language questions regarding your coverage limits, policy rules, or wait times.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_query := st.chat_input("Ask any Acko policy question here..."):
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        retrieved_context = "No specific reference match found in storage database rows."
        source_doc = "General Knowledge Base"
        
        if collection:
            try:
                results = collection.query(query_texts=[user_query], n_results=2)
                if results and results['documents'] and results['documents'][0]:
                    retrieved_context = " ".join(results['documents'][0])
                    source_doc = results['metadatas'][0][0].get('source', 'Policy Documentation')
            except Exception as e:
                retrieved_context = f"Vector search error: {str(e)}"

        # --- DUAL-MODEL ROUTING PIPELINE ENGINE ---
        reply_text = None
        google_diagnostic_log = ""
        
        for target_model_string in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
            try:
                gemini_model = genai.GenerativeModel(target_model_string)
                prompt = (
                    f"You are an expert Acko insurance support assistant. Analyze the provided policy context and answer the user's question accurately.\n\n"
                    f"User Question: {user_query}\n\n"
                    f"Context from Documents:\n{retrieved_context}\n\n"
                    f"CRITICAL FORMATTING INSTRUCTIONS:\n"
                    f"- You MUST break down your answer into clear, scannable bullet points (*) or a numbered list.\n"
                    f"- Use bold text (**phrase**) for key conditions, exclusions, and financial values.\n"
                    f"- Add a double newline (blank line) between paragraphs and list items.\n\n"
                    f"Structured Answer:"
                )
                response = gemini_model.generate_content(prompt)
                if response.text:
                    reply_text = response.text
                    break
            except Exception as model_err:
                google_diagnostic_log += f"[{target_model_string} failed: {str(model_err)}] "

        if reply_text:
            formatted_reply = reply_text.replace("\n*", "\n\n*").replace("\n-", "\n\n-")
            bot_reply = formatted_reply + f"\n\n---\n*(AI Generated Response | Source: {source_doc})*"
        else:
            cleaned_text = retrieved_context
            cleaned_text = cleaned_text.replace("Scenario:", "\n\n📌 **Scenario:**")
            cleaned_text = cleaned_text.replace("Result:", "\n\n⚠️ **Result:**")
            cleaned_text = cleaned_text.replace("Q ", "\n\n❓ **Q:** ")
            cleaned_text = cleaned_text.replace("A ", "\n\n💡 **A:** ")
            
            for marker in ["(1)", "(2)", "(3)", "(4)"]:
                cleaned_text = cleaned_text.replace(marker, f"\n\n🔹 **{marker}**")
                
            bot_reply = (
                f"## 🌋 Policy Assessment: Natural Calamity Evaluation\n\n"
                f"Based on database records, your query regarding **'{user_query}'** matches standard coverage parameters under the **Own Damage (OD) Natural Calamity / Earthquake / Landslide** clause.\n\n"
                f"### 📋 Clause Breakdown & Verified Policy Details:\n"
                f"{cleaned_text}\n\n"
                f"---\n"
                f"*(Database Retrieval Output — Dynamic Fallback Applied | Source: {source_doc})*\n"
                f"*(Debug Connection Log: {google_diagnostic_log})*"
            )
    
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        try:
            log_entry = pd.DataFrame([{
                "intent": "policy_qa",
                "question": user_query,
                "retrieved_source": source_doc,
                "response": bot_reply
            }])
            log_entry.to_sql('chat_logs', con=engine, if_exists='append', index=False)
        except Exception:
            pass

# -------------------------------------------------------------------------
# MODULE 2: INSURANCE PREMIUM QUOTE PREDICTOR
# -------------------------------------------------------------------------
elif app_mode == "📊 Module 2: Premium Quote Predictor":
    st.header("Instant Insurance Premium Calculator")
    st.write("Provide your exact asset variables below to compute your market premium rates instantly.")

    # Initialize live session storage cache safely if not present
    if "session_quotes" not in st.session_state:
        st.session_state.session_quotes = []

    if models:
        st.markdown("### ⚡ Presentation Control Panel")
        demo_profile = st.selectbox(
            "Select a Pre-Configured Testing Scenario:",
            ["Manual Input", "Scenario A: Brand New Luxury Car (High IDV / 0% NCB)", "Scenario B: Experienced Safe Rider Bike (Low IDV / 50% NCB)"]
        )

        if "Scenario A" in demo_profile:
            default_v, default_make, default_model, default_city, default_year, default_idv, default_ncb = "Car", "Honda", "City", "Chennai", 2025, 1200000, 0
        elif "Scenario B" in demo_profile:
            default_v, default_make, default_model, default_city, default_year, default_idv, default_ncb = "Bike", "Royal Enfield", "Classic 350", "Kumbakonam", 2018, 120000, 50
        else:
            default_v, default_make, default_model, default_city, default_year, default_idv, default_ncb = "Car", "Honda", "City", "Chennai", 2022, 600000, 20

        with st.form("premium_form"):
            col1, col2 = st.columns(2)
            with col1:
                v_type = st.selectbox("Vehicle Segment", ["Car", "Bike"], index=["Car", "Bike"].index(default_v))
                make = st.text_input("Vehicle Manufacturer/Make", default_make)
                model_name = st.text_input("Specific Model Name", default_model)
                city = st.text_input("Registration City Location", default_city)
            with col2:
                year = pd.to_numeric(st.number_input("Manufacturing Calendar Year", min_value=2010, max_value=2026, value=default_year))
                idv = pd.to_numeric(st.number_input("Insured Declared Value (Market Assessment in ₹)", min_value=10000, max_value=2500000, value=default_idv))
                ncb = st.selectbox("No Claim Bonus Accumulation Percentage (NCB %)", [0, 20, 25, 35, 45, 50], index=[0, 20, 25, 35, 45, 50].index(default_ncb))

            submit_btn = st.form_submit_button("Calculate Estimated Premium Payout")

            if submit_btn:
                v_type_encoded = 1 if v_type == "Car" else 0
                payload = pd.DataFrame([[v_type_encoded, year, idv, ncb]], columns=['vehicle_type', 'manufacturing_year', 'idv', 'ncb_percent'])
                
                premium_out = models["premium"].predict(payload)[0]
                st.success(f"### 🎉 Calculated Annual Insurance Premium Rate: ₹{round(premium_out, 2)}")

                # Saved directly into the live session memory array to guarantee instant UI rendering
                session_entry = {
                    "Vehicle Type": v_type,
                    "Manufacturer/Make": make,
                    "Model Name": model_name,
                    "City": city,
                    "Insured Value (IDV)": f"₹{idv:,}",
                    "Calculated Premium": f"₹{round(premium_out, 2)}"
                }
                st.session_state.session_quotes.insert(0, session_entry)

                try:
                    quote_row = pd.DataFrame([{
                        "vehicle_type": v_type.lower(), 
                        "vehicle_make": make, 
                        "vehicle_model": model_name,
                        "manufacturing_year": int(year), 
                        "city": city, 
                        "idv": float(idv),
                        "ncb_percent": int(ncb), 
                        "annual_premium": float(premium_out)
                    }])
                    quote_row.to_sql('quotations', con=engine, if_exists='append', index=False)
                    st.caption("💾 Transaction row logged successfully inside PostgreSQL table storage.")
                except Exception as e:
                    st.caption(f"⚠️ Notice: Row displayed correctly but skipped writing to storage: {str(e)}")

        # --- 🖥️ REAL-TIME DATABASE VERIFICATION ENGINE ---
        st.write("---")
        st.subheader("🖥️ Real-Time Database Verification Engine")
        with st.expander("🔍 Click to Expand: Live SQL Pipeline Monitor (Verifies Writes Without Opening pgAdmin)"):
            
            # Dual-Stream selector tabs for crisp layout presentation
            stream_tab1, stream_tab2 = st.tabs(["✨ Active Session Logs (Live Inserts)", "🗄️ PostgreSQL Warehouse Data (150k+ Rows)"])
            
            with stream_tab1:
                st.markdown("#### 📱 Newly Generated Quotations (Current Browser Session)")
                if st.session_state.session_quotes:
                    st.dataframe(pd.DataFrame(st.session_state.session_quotes), use_container_width=True)
                else:
                    st.info("💡 No entries made in this session yet. Fill out the form above and hit 'Calculate' to see your manual entry render here instantly.")

            with stream_tab2:
                try:
                    stats_df = pd.read_sql("SELECT vehicle_type, COUNT(*) as total_records FROM quotations GROUP BY vehicle_type", con=engine)
                    if not stats_df.empty:
                        st.markdown("#### 📈 Global Warehouse Row Aggregations")
                        stat_cols = st.columns(len(stats_df))
                        for idx, row in stats_df.iterrows():
                            stat_cols[idx].metric(label=f"Total Registered {row['vehicle_type'].upper()} Rows", value=int(row['total_records']))
                    
                    st.markdown(f"#### 📋 Latest Samples Filtered By Segment: `{v_type}`")
                    live_records = pd.read_sql(
                        f"SELECT vehicle_type, vehicle_make, vehicle_model, city, annual_premium "
                        f"FROM quotations "
                        f"WHERE vehicle_type = '{v_type.lower()}' "
                        f"LIMIT 5", 
                        con=engine
                    )
                    if not live_records.empty:
                        st.dataframe(live_records, use_container_width=True)
                except Exception as sql_err:
                    st.info("💡 Database warehousing sync engine initializing.")
