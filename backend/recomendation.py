# backend/investment_tools/recommendation.py
import joblib
import pandas as pd

model = joblib.load("backend/models/recommendation_model.pkl")


FEATURES = [
    "price", "bedrooms", "bathrooms", "sizeSqFeetMax",
    "price_per_bedroom", "price_per_sqft",
    "estimated_rent", "rent_to_price_ratio", "bedrooms_per_100k", "region_score",
    "region_Central", "region_East", "region_North", "region_Other",
    "region_South", "region_West",
    "propertyType_Detached", "propertyType_Flat", "propertyType_House",
    "propertyType_Other", "propertyType_Semi_Detached", "propertyType_Terraced"
]

def predict_recommendation(data_dict):
    ordered_features = [data_dict.get(f, 0) for f in FEATURES]
    df = pd.DataFrame([ordered_features], columns=FEATURES)
    prediction = model.predict(df)[0]
    confidence = model.predict_proba(df)[0][prediction] * 100
    return {
        "recommendation": "Buy" if prediction == 1 else "Avoid",
        "confidence": round(confidence, 1)
    }
