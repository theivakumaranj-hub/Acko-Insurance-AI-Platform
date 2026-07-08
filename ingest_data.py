import os
import pandas as pd
import chromadb
from sqlalchemy import create_engine

# Loud debug statement to force a terminal response
print("🚀 Script execution triggered successfully! Starting pipelines...")

# --- DATABASE CONFIGURATIONS ---
# Remember to swap 'YOUR_PASSWORD' with your actual local PostgreSQL password!
DATABASE_URL = "postgresql://postgres:kumaranias7@localhost:5432/acko_db"
engine = create_engine(DATABASE_URL)

def ingest_policy_documents():
    print("\n⏳ Starting Document Ingestion into ChromaDB...")
    from langchain_community.document_loaders import PyPDFDirectoryLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    pdf_folder_path = "data/policies/"
    if not os.path.exists(pdf_folder_path) or not os.listdir(pdf_folder_path):
        print(f"⚠️ Warning: Please place your policy PDFs inside '{pdf_folder_path}' first.")
        return
        
    loader = PyPDFDirectoryLoader(pdf_folder_path)
    raw_documents = loader.load()
    print(f"📄 Successfully read {len(raw_documents)} raw pages from PDF documents.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_chunks = text_splitter.split_documents(raw_documents)
    print(f"✂️ Split documents into {len(split_chunks)} searchable text paragraphs.")
    
    chroma_client = chromadb.PersistentClient(path="./chroma_db_storage")
    collection = chroma_client.get_or_create_collection(name="acko_policies")
    
    documents_list = [chunk.page_content for chunk in split_chunks]
    metadatas_list = [{"source": os.path.basename(chunk.metadata.get('source', 'unknown'))} for chunk in split_chunks]
    ids_list = [f"id_{i}" for i in range(len(split_chunks))]
    
    collection.add(
        documents=documents_list,
        metadatas=metadatas_list,
        ids=ids_list
    )
    print("✅ Module 1 Vector Store completed and persisted to disk!")

def ingest_csv_datasets():
    print("\n⏳ Starting CSV Data Migration into PostgreSQL...")
    
    bike_quote_path = "data/csv/acko_bike_quotation.csv"
    car_quote_path = "data/csv/acko_car_quotation.csv"
    bike_claims_path = "data/csv/acko_bike_claims.csv"
    car_claims_path = "data/csv/acko_car_claims.csv"
    
    # 1. PROCESS AND COMBINE QUOTATIONS DATA
    quotes_dfs = []
    if os.path.exists(bike_quote_path):
        print("🏍️ Reading Bike Quotations CSV...")
        df_bike_q = pd.read_csv(bike_quote_path)
        df_bike_q['vehicle_type'] = 'bike'
        quotes_dfs.append(df_bike_q)
        
    if os.path.exists(car_quote_path):
        print("🚗 Reading Car Quotations CSV...")
        df_car_q = pd.read_csv(car_quote_path)
        df_car_q['vehicle_type'] = 'car'
        quotes_dfs.append(df_car_q)
        
    # 1. PROCESS AND COMBINE QUOTATIONS DATA
    # ... (keep the reading code the same) ...
    if quotes_dfs:
        print("📊 Merging and uploading quotations to PostgreSQL...")
        df_all_quotes = pd.concat(quotes_dfs, ignore_index=True)
        
        # CHANGED 'append' TO 'replace' HERE 👇
        df_all_quotes.to_sql('quotations', con=engine, if_exists='replace', index=False)
        print(f"✅ Successfully loaded {len(df_all_quotes)} combined records into 'quotations' table.")
    else:
        print("⚠️ No quotation CSV files were discovered.")

    # 2. PROCESS AND COMBINE CLAIMS DATA
    claims_dfs = []
    if os.path.exists(bike_claims_path):
        print("🏍️ Reading Bike Claims CSV...")
        df_bike_c = pd.read_csv(bike_claims_path)
        df_bike_c['vehicle_type'] = 'bike'
        claims_dfs.append(df_bike_c)
        
    if os.path.exists(car_claims_path):
        print("🚗 Reading Car Claims CSV...")
        df_car_c = pd.read_csv(car_claims_path)
        df_car_c['vehicle_type'] = 'car'
        claims_dfs.append(df_car_c)
        
    if claims_dfs:
        print("📊 Merging and uploading claims to PostgreSQL...")
        df_all_claims = pd.concat(claims_dfs, ignore_index=True)
        
        # CHANGED 'append' TO 'replace' HERE 👇
        df_all_claims.to_sql('claims', con=engine, if_exists='replace', index=False)
        print(f"✅ Successfully loaded {len(df_all_claims)} combined records into 'claims' table.")
    else:
        print("⚠️ No claim CSV files were discovered.")

# This explicit block tells Python to run the functions above when executed
if __name__ == "__main__":
    ingest_policy_documents()
    ingest_csv_datasets()
    print("\n🚀 All background data pipelines have been loaded successfully!")