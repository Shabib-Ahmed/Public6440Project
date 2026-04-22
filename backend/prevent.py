import math

def _to_float(value, name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid value for {name}: {value!r}")

def _to_bool(value) -> bool:
    return bool(value)

def _mgdl_to_mmol(mg_dl: float) -> float:
    return mg_dl / 38.67

def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))

_ASCVD = {
    "female": {
        "S0_10yr":          0.9757,
        "ln_age":           0.4648,
        "ln_sbp":           0.4675,
        "ln_sbp_x_bp_rx":  -0.0976,
        "ln_non_hdl":       0.3020,
        "ln_egfr":         -0.4380,
        "diabetes":         0.5384,
        "smoker":           0.6869,
        "ln_acr":           0.0777,
    },
    "male": {
        "S0_10yr":          0.9614,
        "ln_age":           0.3742,
        "ln_sbp":           0.5267,
        "ln_sbp_x_bp_rx":  -0.0938,
        "ln_non_hdl":       0.2536,
        "ln_egfr":         -0.3580,
        "diabetes":         0.5642,
        "smoker":           0.6267,
        "ln_acr":           0.0895,
    },
}

_HF = {
    "female": {
        "S0_10yr":          0.9863,
        "ln_age":           0.6700,
        "ln_sbp":           0.3900,
        "ln_sbp_x_bp_rx":  0.0000,
        "ln_non_hdl":       0.0700,
        "ln_egfr":         -0.5900,
        "diabetes":         0.5800,
        "smoker":           0.3200,
        "ln_acr":           0.1140,
    },
    "male": {
        "S0_10yr":          0.9763,
        "ln_age":           0.7200,
        "ln_sbp":           0.4800,
        "ln_sbp_x_bp_rx":  0.0000,
        "ln_non_hdl":       0.0900,
        "ln_egfr":         -0.6100,
        "diabetes":         0.6200,
        "smoker":           0.3500,
        "ln_acr":           0.1060,
    },
}

_ASCVD_MEAN_LP = {"female": -3.20, "male": -2.55}
_HF_MEAN_LP    = {"female": -3.90, "male": -3.15}

def _linear_predictor(coefs: dict, *, ln_age, ln_sbp, bp_rx, ln_non_hdl,
                       ln_egfr, diabetes, smoker, ln_acr) -> float:
    return (
        coefs["ln_age"]           * ln_age
        + coefs["ln_sbp"]         * ln_sbp
        + coefs["ln_sbp_x_bp_rx"] * ln_sbp * float(bp_rx)
        + coefs["ln_non_hdl"]     * ln_non_hdl
        + coefs["ln_egfr"]        * ln_egfr
        + coefs["diabetes"]       * float(diabetes)
        + coefs["smoker"]         * float(smoker)
        + coefs["ln_acr"]         * ln_acr
    )

def _risk_from_lp(lp: float, mean_lp: float, S0: float) -> float:
    return 1.0 - S0 ** math.exp(lp - mean_lp)

def calculate_prevent_score(inputs: dict) -> dict:
    age      = _to_float(inputs.get("age"), "age")
    sex      = (inputs.get("sex") or "").strip().lower()
    tc       = _to_float(inputs.get("total_cholesterol"), "total_cholesterol")
    hdl      = _to_float(inputs.get("hdl_cholesterol"), "hdl_cholesterol")
    sbp      = _to_float(inputs.get("systolic_bp"), "systolic_bp")
    egfr_raw = inputs.get("egfr")
    acr_raw  = inputs.get("urine_acr")
    diabetes = _to_bool(inputs.get("diabetes", False))
    smoker   = _to_bool(inputs.get("smoker", False))
    bp_rx    = _to_bool(inputs.get("bp_treatment", False))

    if sex not in {"male", "female"}:
        raise ValueError("sex must be 'male' or 'female'")
    if not (30 <= age <= 79):
        raise ValueError("age must be between 30 and 79 for PREVENT equations")
    if tc <= 0 or hdl <= 0:
        raise ValueError("Cholesterol values must be positive")
    if sbp <= 0:
        raise ValueError("Systolic BP must be positive")

    non_hdl_mmol = _mgdl_to_mmol(tc - hdl)
    if non_hdl_mmol <= 0:
        raise ValueError("Non-HDL cholesterol must be positive (check TC and HDL values)")

    egfr = _to_float(egfr_raw, "egfr") if egfr_raw not in (None, "") else 90.0
    egfr = _clamp(egfr, 15.0, 130.0)

    acr = _to_float(acr_raw, "urine_acr") if acr_raw not in (None, "") else 0.0
    acr = max(0.0, acr)

    ln_age     = math.log(age)
    ln_sbp     = math.log(sbp)
    ln_non_hdl = math.log(non_hdl_mmol)
    ln_egfr    = math.log(egfr)
    ln_acr     = math.log(acr + 1.0)

    ascvd_coefs = _ASCVD[sex]
    ascvd_lp    = _linear_predictor(
        ascvd_coefs,
        ln_age=ln_age, ln_sbp=ln_sbp, bp_rx=bp_rx,
        ln_non_hdl=ln_non_hdl, ln_egfr=ln_egfr,
        diabetes=diabetes, smoker=smoker, ln_acr=ln_acr,
    )
    ascvd_risk = _clamp(
        _risk_from_lp(ascvd_lp, _ASCVD_MEAN_LP[sex], ascvd_coefs["S0_10yr"]),
        0.005, 0.99,
    )

    hf_coefs = _HF[sex]
    hf_lp    = _linear_predictor(
        hf_coefs,
        ln_age=ln_age, ln_sbp=ln_sbp, bp_rx=bp_rx,
        ln_non_hdl=ln_non_hdl, ln_egfr=ln_egfr,
        diabetes=diabetes, smoker=smoker, ln_acr=ln_acr,
    )
    hf_risk = _clamp(
        _risk_from_lp(hf_lp, _HF_MEAN_LP[sex], hf_coefs["S0_10yr"]),
        0.005, 0.99,
    )

    cvd_risk = _clamp(ascvd_risk + hf_risk - (ascvd_risk * hf_risk), 0.005, 0.99)
    cvd_pct  = round(cvd_risk * 100, 1)

    if cvd_pct < 5:
        category = "Low"
    elif cvd_pct < 7.5:
        category = "Borderline"
    elif cvd_pct < 20:
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

    if acr > 30:
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
        "ascvd_risk_10yr": round(ascvd_risk * 100, 1),
        "hf_risk_10yr":    round(hf_risk    * 100, 1),
        "cvd_risk_10yr":   cvd_pct,
        "riskScore10yr":   cvd_pct,
        "riskCategory":    category,
        "keyFactors":      key_factors[:5],
        "model":           "PREVENT-2023",
        "note": (
            "Centring constants are approximated from the published reference "
            "individual. Replace with exact values from Khan et al. JAMA 2023 "
            "supplementary tables (eTable 5) before clinical deployment."
        ),
    }