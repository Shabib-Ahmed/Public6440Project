from flask import Flask, request, jsonify
from flask_cors import CORS
from fhir_client import get_patient_data

app = Flask(__name__)
CORS(app)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/patient/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    try:
        data = get_patient_data(patient_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/risk", methods=["POST"])
def calculate_risk():
    body = request.json or {}
    patient_id = body.get("patientId")

    fhir_data = {}
    if patient_id:
        try:
            fhir_data = get_patient_data(patient_id)
        except Exception as e:
            print(f"FHIR fetch failed: {e}")

    inputs = {
        "age":               body.get("age")              or fhir_data.get("age"),
        "sex":               body.get("sex")              or fhir_data.get("sex"),
        "total_cholesterol": body.get("totalCholesterol") or fhir_data.get("total_cholesterol"),
        "hdl_cholesterol":   body.get("hdlCholesterol")   or fhir_data.get("hdl_cholesterol"),
        "systolic_bp":       body.get("systolicBP")       or fhir_data.get("systolic_bp"),
        "diabetes":          body.get("diabetes",         fhir_data.get("diabetes", False)),
        "smoker":            body.get("smoker",           fhir_data.get("smoker", False)),
        "bp_treatment":      body.get("bpTreatment",      fhir_data.get("bp_treatment", False)),
        "egfr":              body.get("egfr")             or fhir_data.get("egfr"),
        "urine_acr":         body.get("urineAcr")         or fhir_data.get("urine_acr"),
    }

    required = ["age", "sex", "total_cholesterol", "hdl_cholesterol", "systolic_bp"]
    missing = [k for k in required if inputs.get(k) is None]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    result = calculate_prevent_score(inputs)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5001)