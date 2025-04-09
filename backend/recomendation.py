# backend/investment_tools/recommendation.py
import joblib
import pandas as pd

# Load trained model
model = joblib.load("/Users/davidlawal/Desktop/Investr-/backend/models/recommendation_model.pkl")

# Define feature list in correct order
FEATURES = [
    "price", "bedrooms", "bathrooms", "sizeSqFeetMax",
    "price_per_bedroom", "price_per_sqft",
    "estimated_rent", "expected_growth_rate",

    # Property type (one-hot)
    "propertyType_Detached",
    "propertyType_Flat",
    "propertyType_House",
    "propertyType_Semi_Detached",
    "propertyType_Terraced",
    "propertyType_Other",

    # Region (one-hot)
    "region_North",
    "region_South",
    "region_East",
    "region_West",
    "region_Central",
    "region_Other"
]

def predict_recommendation(data_dict):
    """
    Accepts a dictionary of model inputs (already processed & encoded),
    returns prediction and confidence.
    """
    df = pd.DataFrame([data_dict])
    prediction = model.predict(df)[0]
    confidence = model.predict_proba(df)[0][prediction] * 100

    return {
        "recommendation": "Buy" if prediction == 1 else "Avoid",
        "confidence": round(confidence, 1)
    }

