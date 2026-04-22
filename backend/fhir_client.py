import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

FHIR_BASE = os.getenv("FHIR_BASE", "https://r4.smarthealthit.org").rstrip("/")
HEADERS = {"Accept": "application/fhir+json"}

LOINC = {
    "total_cholesterol": "2093-3",
    "hdl_cholesterol":   "2085-9",
    "systolic_bp":       "8480-6",
    "hba1c":             "4548-4",
    "egfr":              "33914-3",
    "urine_acr":         "14959-1",
    "bmi":               "39156-5",
}

# RxNorm: antihypertensive drug classes (ingredient-level codes)
# ACE inhibitors, ARBs, CCBs, thiazides, beta-blockers (common agents)
ANTIHYPERTENSIVE_RXNORM = [
    "29046",   # lisinopril
    "214354",  # lisinopril/HCTZ
    "17767",   # amlodipine
    "83515",   # amlodipine (alt)
    "203160",  # atenolol
    "1091643", # metoprolol succinate
    "866511",  # metoprolol tartrate
    "41493",   # losartan
    "214354",  # valsartan
    "83818",   # hydrochlorothiazide
    "153665",  # chlorthalidone
    "321064",  # olmesartan
    "321827",  # irbesartan
    "35208",   # ramipril
    "18867",   # carvedilol
    "1998",    # enalapril
]

# RxNorm: statin ingredient-level codes
STATIN_RXNORM = [
    "301542",  # rosuvastatin
    "83367",   # atorvastatin
    "41127",   # fluvastatin
    "42463",   # pravastatin
    "36567",   # simvastatin
    "103919",  # cerivastatin
    "312961",  # lovastatin
    "monograph-pitavastatin",
    "861634",  # pitavastatin
]


def _get(path, params=None):
    resp = requests.get(
        f"{FHIR_BASE}{path}",
        params=params,
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _extract_value(resource: dict, target_loinc: str | None = None) -> float | None:
    vq = resource.get("valueQuantity")
    if vq and "value" in vq:
        try:
            return float(vq["value"])
        except (TypeError, ValueError):
            pass

    for component in resource.get("component", []):
        codings = component.get("code", {}).get("coding", [])
        codes = [c.get("code") for c in codings]
        if target_loinc is None or target_loinc in codes:
            cvq = component.get("valueQuantity")
            if cvq and "value" in cvq:
                try:
                    return float(cvq["value"])
                except (TypeError, ValueError):
                    pass
    return None


def _latest_observation(patient_id: str, loinc_code: str):
    query_code = "55284-4" if loinc_code == "8480-6" else loinc_code

    data = _get("/Observation", {
        "patient": patient_id,
        "code": query_code,
        "_count": "50",
        "_sort": "-date",
    })
    entries = data.get("entry", [])

    def _effective_date(entry):
        r = entry.get("resource", {})
        return r.get("effectiveDateTime") or r.get("effectivePeriod", {}).get("start") or ""

    entries = sorted(entries, key=_effective_date, reverse=True)

    for entry in entries:
        value = _extract_value(entry.get("resource", {}), target_loinc=loinc_code)
        if value is not None:
            return value
    return None


def _get_age(birth_date_str: str) -> int:
    bd = date.fromisoformat(birth_date_str)
    today = date.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def _get_sex(patient_resource: dict) -> str:
    gender = patient_resource.get("gender", "").lower()
    return gender if gender in ("male", "female") else "unknown"


def _has_condition(patient_id: str, snomed_code: str) -> bool:
    data = _get("/Condition", {
        "patient": patient_id,
        "code": snomed_code,
        "clinical-status": "active",
        "_count": "1",
    })
    return bool(data.get("entry"))


def _has_medication(patient_id: str, rxnorm_codes: list) -> bool:
    for code in rxnorm_codes:
        data = _get("/MedicationRequest", {
            "patient": patient_id,
            "code": code,
            "status": "active",
            "_count": "1",
        })
        if data.get("entry"):
            return True
    return False


def get_patient_data(patient_id: str) -> dict:
    pt = _get(f"/Patient/{patient_id}")

    age = _get_age(pt["birthDate"]) if "birthDate" in pt else None
    sex = _get_sex(pt)

    name_parts = pt.get("name", [{}])[0]
    given = " ".join(name_parts.get("given", []))
    family = name_parts.get("family", "")
    full_name = f"{given} {family}".strip()

    # Fetch all observations in parallel
    obs_keys = list(LOINC.keys())
    obs_results = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(_latest_observation, patient_id, LOINC[k]): k
            for k in obs_keys
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                obs_results[key] = future.result()
            except Exception:
                obs_results[key] = None

    total_chol = obs_results.get("total_cholesterol")
    hdl_chol   = obs_results.get("hdl_cholesterol")
    systolic   = obs_results.get("systolic_bp")
    hba1c      = obs_results.get("hba1c")
    egfr       = obs_results.get("egfr")
    urine_acr  = obs_results.get("urine_acr")
    bmi        = obs_results.get("bmi")

    # Fetch conditions and medications in parallel
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_diabetes   = pool.submit(_has_condition, patient_id, "73211009")   # SNOMED: DM
        f_smoker     = pool.submit(_has_condition, patient_id, "77176002")   # SNOMED: smoker
        f_bp_rx      = pool.submit(_has_medication, patient_id, ANTIHYPERTENSIVE_RXNORM)
        f_statin     = pool.submit(_has_medication, patient_id, STATIN_RXNORM)

    diabetes    = (hba1c is not None and hba1c >= 6.5) or f_diabetes.result()
    smoker      = f_smoker.result()
    bp_treatment = f_bp_rx.result()
    statin      = f_statin.result()

    return {
        "patient_id":      patient_id,
        "name":            full_name,
        "age":             age,
        "sex":             sex,
        "total_cholesterol": total_chol,
        "hdl_cholesterol":   hdl_chol,
        "systolic_bp":       systolic,
        "hba1c":             hba1c,
        "egfr":              egfr,
        "urine_acr":         urine_acr,
        "bmi":               bmi,
        "diabetes":          diabetes,
        "smoker":            smoker,
        "bp_treatment":      bp_treatment,
        "statin":            statin,
    }