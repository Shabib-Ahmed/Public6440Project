from flask import Flask, request, jsonify
from flask_cors import CORS
from fhir_client import get_patient_data
from prevent import calculate_prevent_score

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

    def val(body_key, fhir_key):
        v = body.get(body_key)
        return v if v not in (None, "") else fhir_data.get(fhir_key)

    inputs = {
        "age": val("age", "age"),
        "sex": val("sex", "sex"),
        "total_cholesterol": val("totalCholesterol", "total_cholesterol"),
        "hdl_cholesterol": val("hdlCholesterol", "hdl_cholesterol"),
        "systolic_bp": val("systolicBP", "systolic_bp"),
        "diabetes": body.get("diabetes", fhir_data.get("diabetes", False)),
        "smoker": body.get("smoker", fhir_data.get("smoker", False)),
        "bp_treatment": body.get("bpTreatment", fhir_data.get("bp_treatment", False)),
        "egfr": val("egfr", "egfr"),
        "urine_acr": val("urineAcr", "urine_acr"),
    }

    required = ["age", "sex", "total_cholesterol", "hdl_cholesterol", "systolic_bp"]
    missing = [k for k in required if inputs.get(k) is None]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        result = calculate_prevent_score(inputs)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Risk calculation failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)