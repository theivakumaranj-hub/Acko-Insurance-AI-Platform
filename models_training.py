# models_training.py (Optimized 1-Model Version)
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

print("⏳ Initiating Premium Predictor Training Pipeline...")

bike_quote_path = "data/csv/acko_bike_quotation.csv"
car_quote_path = "data/csv/acko_car_quotation.csv"

def robust_column_finder(df, keywords):
    for col in df.columns:
        if any(kw in col.lower() for kw in keywords):
            return col
    return None

if os.path.exists(bike_quote_path) and os.path.exists(car_quote_path):
    df_bike_q = pd.read_csv(bike_quote_path)
    df_bike_q['vehicle_type'] = 0
    df_car_q = pd.read_csv(car_quote_path)
    df_car_q['vehicle_type'] = 1
    df_all_quotes = pd.concat([df_bike_q, df_car_q], ignore_index=True)
    
    idv_col = robust_column_finder(df_all_quotes, ['idv', 'value', 'declared']) or 'idv'
    ncb_col = robust_column_finder(df_all_quotes, ['ncb', 'bonus']) or 'ncb_percent'
    year_col = robust_column_finder(df_all_quotes, ['year', 'manufacture']) or 'manufacturing_year'
    target_col = robust_column_finder(df_all_quotes, ['premium', 'price', 'annual']) or 'annual_premium'
    
    X_prem = pd.DataFrame({
        'vehicle_type': df_all_quotes['vehicle_type'],
        'manufacturing_year': df_all_quotes[year_col],
        'idv': df_all_quotes[idv_col],
        'ncb_percent': df_all_quotes[ncb_col]
    })
    
    prem_model = RandomForestRegressor(n_estimators=50, random_state=42)
    prem_model.fit(X_prem, df_all_quotes[target_col])
    joblib.dump(prem_model, 'premium_model.pkl')
    print("✅ Successfully trained and updated premium_model.pkl!")