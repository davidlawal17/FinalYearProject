# backend/investment_tools/recommendation.py
import joblib
import pandas as pd

# Load trained model
model = joblib.load("/Users/davidlawal/Desktop/Investr-/backend/models/recommendation_model.pkl")

# Define feature list in correct order
FEATURES = [
    "price",
    "bedrooms",
    "bathrooms",
    "sizeSqFeetMax",
    "price_per_bedroom",
    "price_per_sqft",
    "estimated_rent",
    "expected_growth_rate",

    # Property types (one-hot)
    "propertyType_Detached",
    "propertyType_Flat",
    "propertyType_House",
    "propertyType_Other",
    "propertyType_Semi_Detached",
    "propertyType_Terraced",

    # Region (one-hot)
    "region_Central",
    "region_East",
    "region_North",
    "region_Other",
    "region_South",
    "region_West"
]


def predict_recommendation(data_dict):
    """
    Accepts a dictionary of model inputs (already processed & encoded),
    ensures feature order and completeness, then returns prediction and confidence.
    """
    # Enforce correct feature order and fill missing values
    ordered_features = [data_dict.get(f, 0) for f in FEATURES]

    # Create DataFrame in expected format
    df = pd.DataFrame([ordered_features], columns=FEATURES)

    # Make predictions
    prediction = model.predict(df)[0]
    confidence = model.predict_proba(df)[0][prediction] * 100

    return {
        "recommendation": "Buy" if prediction == 1 else "Avoid",
        "confidence": round(confidence, 1)
    }


