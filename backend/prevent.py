import math

CHOL_CONV = 38.67

_BASE = {
    "female": {
        "total_cvd": [
            0.793933, 0.030524, -0.160686, -0.239400, 0.360078,
            0.866760, 0.536074, 0.000000, 0.000000, 0.604592,
            0.043377, 0.315167, -0.147765, -0.066361, 0.119788,
            -0.081972, 0.030677, -0.094635, -0.270570, -0.078715,
            0.000000, -0.163781, -3.307728
        ],
        "ascvd": [
            0.719883, 0.117697, -0.151185, -0.083536, 0.359285,
            0.834858, 0.483108, 0.000000, 0.000000, 0.486462,
            0.039778, 0.226531, -0.059237, -0.039576, 0.084442,
            -0.056784, 0.032569, -0.103598, -0.241754, -0.079114,
            0.000000, -0.167149, -3.819975
        ],
        "heart_failure": [
            0.899823, 0.000000, 0.000000, -0.455977, 0.357650,
            1.038346, 0.583916, -0.007229, 0.299771, 0.745164,
            0.055709, 0.353444, 0.000000, -0.098151, 0.000000,
            0.000000, 0.000000, -0.094666, -0.358104, -0.115945,
            -0.003878, -0.188429, -4.310409
        ],
    },
    "male": {
        "total_cvd": [
            0.768853, 0.073617, -0.095443, -0.434735, 0.336266,
            0.769286, 0.438687, 0.000000, 0.000000, 0.537898,
            0.016483, 0.288879, -0.133735, -0.047592, 0.150273,
            -0.051787, 0.019117, -0.104948, -0.225195, -0.089507,
            0.000000, -0.154370, -3.031168
        ],
        "ascvd": [
            0.709985, 0.165866, -0.114429, -0.283721, 0.323998,
            0.718960, 0.395697, 0.000000, 0.000000, 0.369007,
            0.020362, 0.203652, -0.086558, -0.032292, 0.114563,
            -0.030000, 0.023275, -0.092702, -0.201852, -0.097053,
            0.000000, -0.121708, -3.500655
        ],
        "heart_failure": [
            0.897264, 0.000000, 0.000000, -0.681147, 0.363446,
            0.923776, 0.502374, -0.048584, 0.372693, 0.692692,
            0.025183, 0.298092, 0.000000, -0.049773, 0.000000,
            0.000000, 0.000000, -0.128920, -0.304092, -0.140169,
            0.006813, -0.179778, -3.946391
        ],
    },
}

_UACR = {
    "female": {
        "total_cvd": [
            0.796925, 0.025663, -0.158811, -0.225570, 0.339665,
            0.804751, 0.528534, 0.000000, 0.000000, 0.480351,
            0.043447, 0.298521, -0.149779, -0.074289, 0.106756,
            -0.077813, 0.030677, -0.090717, -0.270512, -0.083056,
            0.000000, -0.138925, 0.179304, 0.013207, -3.738341
        ],
        "ascvd": [
            0.720200, 0.113577, -0.149351, -0.072668, 0.343626,
            0.777309, 0.474666, 0.000000, 0.000000, 0.382465,
            0.039418, 0.212518, -0.060305, -0.046605, 0.073312,
            -0.053426, 0.032569, -0.099989, -0.241176, -0.082694,
            0.000000, -0.144474, 0.150122, 0.005026, -4.174614
        ],
        "heart_failure": [
            0.914597, 0.000000, 0.000000, -0.444135, 0.326032,
            0.961136, 0.575579, 0.000883, 0.298896, 0.591529,
            0.055682, 0.331410, 0.000000, -0.107860, 0.000000,
            0.000000, 0.000000, -0.087523, -0.356859, -0.122025,
            -0.005364, -0.161039, 0.219728, 0.032667, -4.841506
        ],
    },
    "male": {
        "total_cvd": [
            0.776865, 0.065995, -0.095111, -0.420667, 0.312015,
            0.698521, 0.431467, 0.000000, 0.000000, 0.384136,
            0.009384, 0.267649, -0.139097, -0.057931, 0.138372,
            -0.048833, 0.020041, -0.102454, -0.223635, -0.089485,
            0.000000, -0.132185, 0.188797, 0.091698, -3.510705
        ],
        "ascvd": [
            0.714172, 0.160219, -0.113909, -0.271946, 0.305872,
            0.660063, 0.388402, 0.000000, 0.000000, 0.246632,
            0.015185, 0.186167, -0.089440, -0.041188, 0.105821,
            -0.028089, 0.024043, -0.091232, -0.200489, -0.096936,
            0.000000, -0.102287, 0.151007, 0.055600, -3.851460
        ],
        "heart_failure": [
            0.911180, 0.000000, 0.000000, -0.669365, 0.329008,
            0.837766, 0.497892, -0.042749, 0.362416, 0.507580,
            0.013772, 0.273996, 0.000000, -0.064571, 0.000000,
            0.000000, 0.000000, -0.123004, -0.301330, -0.141032,
            0.002153, -0.154802, 0.230630, 0.147219, -4.556907
        ],
    },
}


def _to_float(value, name):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid value for {name}: {value!r}")


def _to_bool(value):
    return bool(value)


def _logistic(lp):
    return math.exp(lp) / (1 + math.exp(lp))


def _build_terms_base(age, non_hdl, hdl_term, sbp_lt, sbp_gte,
                      dm, smoking, bmi_lt, bmi_ge, egfr_lt, egfr_ge,
                      bp_tx, statin, age10):
    return [
        age10,
        non_hdl,
        hdl_term,
        sbp_lt,
        sbp_gte,
        float(dm),
        float(smoking),
        bmi_lt,
        bmi_ge,
        egfr_lt,
        egfr_ge,
        float(bp_tx),
        float(statin),
        float(bp_tx) * sbp_gte,
        float(statin) * non_hdl,
        age10 * non_hdl,
        age10 * hdl_term,
        age10 * sbp_gte,
        age10 * float(dm),
        age10 * float(smoking),
        age10 * bmi_ge,
        age10 * egfr_lt,
        1.0,
    ]


def calculate_prevent_score(inputs):
    age     = _to_float(inputs.get("age"), "age")
    sex     = (inputs.get("sex") or "").strip().lower()
    tc      = _to_float(inputs.get("total_cholesterol"), "total_cholesterol")
    hdl     = _to_float(inputs.get("hdl_cholesterol"), "hdl_cholesterol")
    sbp     = _to_float(inputs.get("systolic_bp"), "systolic_bp")
    egfr_raw = inputs.get("egfr")
    acr_raw  = inputs.get("urine_acr")
    bmi_raw  = inputs.get("bmi")
    diabetes = _to_bool(inputs.get("diabetes", False))
    smoker   = _to_bool(inputs.get("smoker", False))
    bp_rx    = _to_bool(inputs.get("bp_treatment", False))
    statin   = _to_bool(inputs.get("statin", False))

    if sex not in {"male", "female"}:
        raise ValueError("sex must be 'male' or 'female'")
    if not (30 <= age <= 79):
        raise ValueError("age must be between 30 and 79")
    if tc <= 0 or hdl <= 0:
        raise ValueError("Cholesterol values must be positive")
    if sbp <= 0:
        raise ValueError("Systolic BP must be positive")

    egfr = _to_float(egfr_raw, "egfr") if egfr_raw not in (None, "") else 90.0
    egfr = max(15.0, min(140.0, egfr))

    acr = _to_float(acr_raw, "urine_acr") if acr_raw not in (None, "") else None

    bmi = _to_float(bmi_raw, "bmi") if bmi_raw not in (None, "") else 25.0
    bmi = max(18.5, min(39.9, bmi))

    age10    = (age - 55) / 10
    non_hdl  = (tc - hdl) / CHOL_CONV - 3.5
    hdl_term = (hdl / CHOL_CONV - 1.3) / 0.3
    sbp_lt   = (min(sbp, 110) - 110) / 20
    sbp_gte  = (max(sbp, 110) - 130) / 20
    egfr_lt  = (min(egfr, 60) - 60) / -15
    egfr_ge  = (max(egfr, 60) - 90) / -15
    bmi_lt   = (min(bmi, 30) - 25) / 5
    bmi_ge   = (max(bmi, 30) - 30) / 5

    use_uacr = acr is not None
    coef_table = _UACR if use_uacr else _BASE

    base_terms = _build_terms_base(
        age, non_hdl, hdl_term, sbp_lt, sbp_gte,
        diabetes, smoker, bmi_lt, bmi_ge, egfr_lt, egfr_ge,
        bp_rx, statin, age10
    )

    if use_uacr:
        ln_acr = math.log(acr) if acr > 0 else 0.0
        terms = base_terms[:-1] + [ln_acr, 0.0, 1.0]
    else:
        terms = base_terms

    def score(outcome):
        coefs = coef_table[sex][outcome]
        lp = sum(c * t for c, t in zip(coefs, terms))
        return round(_logistic(lp) * 100, 1)

    cvd   = score("total_cvd")
    ascvd = score("ascvd")
    hf    = score("heart_failure")

    if cvd < 5:
        category = "Low"
    elif cvd < 7.5:
        category = "Borderline"
    elif cvd < 20:
        category = "Intermediate"
    else:
        category = "High"

    key_factors = []

    if sbp >= 130:
        key_factors.append({
            "factor": "Elevated systolic blood pressure",
            "value": f"{sbp:.0f} mmHg",
            "advice": (
                "Systolic BP ≥130 mmHg is a major ASCVD risk driver. "
                "Each 10 mmHg reduction in SBP is associated with ~20% lower "
                "relative cardiovascular risk. Review lifestyle modifications "
                "and pharmacotherapy targets."
            ),
        })

    non_hdl_mgdl = tc - hdl
    if non_hdl_mgdl >= 130:
        key_factors.append({
            "factor": "Elevated non-HDL cholesterol",
            "value": f"{non_hdl_mgdl:.0f} mg/dL",
            "advice": (
                "Non-HDL ≥130 mg/dL (3.4 mmol/L) reflects excess atherogenic "
                "lipoprotein burden. Statin therapy, dietary modification, and "
                "weight management are first-line interventions."
            ),
        })

    if smoker:
        key_factors.append({
            "factor": "Current smoking",
            "value": "Yes",
            "advice": (
                "Smoking is one of the highest-impact modifiable CVD risk factors. "
                "Cessation reduces cardiovascular risk within 1–2 years and should "
                "be prioritised in every clinical encounter."
            ),
        })

    if diabetes:
        key_factors.append({
            "factor": "Diabetes mellitus",
            "value": "Yes",
            "advice": (
                "Diabetes approximately doubles cardiovascular risk. "
                "Glycaemic control, blood pressure management, and statin therapy "
                "are core components of preventive care in this population."
            ),
        })

    if egfr < 60:
        key_factors.append({
            "factor": "Reduced eGFR (CKD)",
            "value": f"{egfr:.0f} mL/min/1.73 m²",
            "advice": (
                "eGFR <60 mL/min/1.73 m² (CKD stage G3+) independently elevates "
                "both ASCVD and heart failure risk. Referral to nephrology and "
                "aggressive risk factor management are recommended."
            ),
        })

    if acr is not None and acr > 30:
        key_factors.append({
            "factor": "Elevated urine albumin-creatinine ratio",
            "value": f"{acr:.0f} mg/g",
            "advice": (
                "Albuminuria (ACR >30 mg/g) is a marker of subclinical vascular "
                "and renal injury and independently increases CVD risk. "
                "RAAS blockade and BP optimisation may slow progression."
            ),
        })

    return {
        "ascvd_risk_10yr": ascvd,
        "hf_risk_10yr":    hf,
        "cvd_risk_10yr":   cvd,
        "riskScore10yr":   cvd,
        "riskCategory":    category,
        "keyFactors":      key_factors[:5],
        "model":           "PREVENT-2023-base" if not use_uacr else "PREVENT-2023-uacr",
    }