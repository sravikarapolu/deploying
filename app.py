from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import random
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from collections import Counter

app = Flask(__name__)
CORS(app)

def load_model():
    return pickle.load(open("model.pkl", "rb"))

# ---------------- LIVE MONITOR ----------------
def fake_input():
    return [random.randint(0, 1) for _ in range(41)]

@app.route('/live')
def live():
    model = load_model()
    data = fake_input()
    pred = model.predict([data])[0]

    return jsonify({
        "time": datetime.now().strftime("%H:%M:%S"),
        "activity": "Suspicious Packet" if pred != "normal" else "User Activity",
        "status": pred,
        "confidence": str(round(random.uniform(90, 100), 2)) + "%",
        "action": "Quarantine" if pred != "normal" else "None"
    })


# ---------------- UPLOAD + ANALYSIS ----------------
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    df = pd.read_csv(file, header=None)
    print("DATA SHAPE:", df.shape)

    X = df.iloc[:, :-2]

    # Encode categorical columns
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = LabelEncoder().fit_transform(X[col])
    model = load_model()
    preds = model.predict(X)

    # Simulate attack types (for visual dashboard)
    attack_types = []
    for p in preds:
        if p == 'normal':
            attack_types.append('normal')
        else:
            attack_types.append(random.choice([
                'neptune', 'smurf', 'portsweep', 'satan'
            ]))

    counts = Counter(attack_types)

    return jsonify({
        "counts": dict(counts)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)