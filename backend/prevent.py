_RANGES = {
    "total_cholesterol": (20,   1200, "mg/dL"),
    "hdl_cholesterol":   (2,    200,  "mg/dL"),
    "systolic_bp":       (40,   320,  "mmHg"),
    "egfr":              (1,    150,  "mL/min/1.73m²"),
    "urine_acr":         (0,    15000, "mg/g"),
}


def _to_float(value, name):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid value for {name}")


def _to_bool(value):
    return bool(value)


def _check_range(value, name):
    low, high, unit = _RANGES[name]
    if not (low <= value <= high):
        raise ValueError(
            f"{name.replace('_', ' ').title()} must be between {low} and {high} {unit} "
            f"(received {value})"
        )


def calculate_prevent_score(inputs: dict) -> dict:
    age = _to_float(inputs.get("age"), "age")
    sex = (inputs.get("sex") or "").lower()
    total_chol = _to_float(inputs.get("total_cholesterol"), "total_cholesterol")
    hdl = _to_float(inputs.get("hdl_cholesterol"), "hdl_cholesterol")
    sbp = _to_float(inputs.get("systolic_bp"), "systolic_bp")
    egfr = inputs.get("egfr")
    urine_acr = inputs.get("urine_acr")
    diabetes = _to_bool(inputs.get("diabetes"))
    smoker = _to_bool(inputs.get("smoker"))
    bp_treatment = _to_bool(inputs.get("bp_treatment"))

    if sex not in {"male", "female"}:
        raise ValueError("Sex must be 'male' or 'female'")

    if not (30 <= age <= 79):
        raise ValueError("Age must be between 30 and 79")

    _check_range(total_chol, "total_cholesterol")
    _check_range(hdl, "hdl_cholesterol")
    _check_range(sbp, "systolic_bp")

    if hdl >= total_chol:
        raise ValueError(
            f"HDL cholesterol ({hdl}) cannot be greater than or equal to "
            f"total cholesterol ({total_chol})"
        )

    risk_points = 0.0

    risk_points += max(0, age - 30) * 0.18
    risk_points += max(0, sbp - 110) * (0.12 if bp_treatment else 0.10)
    risk_points += max(0, total_chol - 160) * 0.03
    risk_points += max(0, 55 - hdl) * 0.12

    if diabetes:
        risk_points += 7.0
    if smoker:
        risk_points += 6.0

    if egfr not in (None, ""):
        egfr = _to_float(egfr, "egfr")
        _check_range(egfr, "egfr")
        if egfr < 60:
            risk_points += min(6.0, (60 - egfr) * 0.15)

    if urine_acr not in (None, ""):
        urine_acr = _to_float(urine_acr, "urine_acr")
        _check_range(urine_acr, "urine_acr")
        if urine_acr > 30:
            risk_points += min(5.0, (urine_acr - 30) * 0.03)

    if sex == "male":
        risk_points += 1.5

    risk = max(1.0, min(30.0, round(risk_points, 1)))

    if risk < 5:
        category = "Low"
    elif risk < 10:
        category = "Borderline"
    elif risk < 20:
        category = "Intermediate"
    else:
        category = "High"

    key_factors = []
    if sbp >= 130:
        key_factors.append({
            "factor": "Elevated systolic blood pressure",
            "advice": "Blood pressure is a major driver of risk. Improving BP control may lower long-term cardiovascular risk."
        })
    if total_chol >= 200:
        key_factors.append({
            "factor": "Elevated total cholesterol",
            "advice": "Higher cholesterol contributes to cardiovascular risk. Consider discussing lipid management and lifestyle changes."
        })
    if hdl < 40:
        key_factors.append({
            "factor": "Low HDL cholesterol",
            "advice": "Low HDL is associated with higher risk. Regular physical activity and overall metabolic health may help."
        })
    if smoker:
        key_factors.append({
            "factor": "Current smoking",
            "advice": "Smoking substantially increases cardiovascular risk. Smoking cessation is one of the highest-impact changes."
        })
    if diabetes:
        key_factors.append({
            "factor": "Diabetes",
            "advice": "Diabetes increases cardiovascular risk and should be part of ongoing preventive care discussions."
        })

    return {
        "riskScore10yr": risk,
        "riskCategory": category,
        "keyFactors": key_factors[:4],
        "model": "prototype-prevent-style"
    }