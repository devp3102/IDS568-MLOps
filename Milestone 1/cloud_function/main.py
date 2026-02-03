import functions_framework
import joblib
import numpy as np
from flask import jsonify

model = None

def load_model():
    global model
    if model is None:
        model = joblib.load("model.pkl")
    return model

@functions_framework.http
def predict(request):
    
    clf = load_model()
    
    request_json = request.get_json(silent=True)
    
    if not request_json or 'features' not in request_json:
        return jsonify({"error": "Missing 'features' in request"}), 400
    
    try:
        features = request_json['features']
        features_array = np.array([features])
        
        prediction = int(clf.predict(features_array)[0])
        
        species_names = ["Setosa", "Versicolor", "Virginica"]
        species = species_names[prediction]
        
        return jsonify({
            "prediction": prediction,
            "species": species
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
