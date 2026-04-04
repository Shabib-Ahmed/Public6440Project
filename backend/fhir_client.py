import os
import requests
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
}

def _latest_observation(patient_id: str, loinc_code: str):
    resp = requests.get(
        f"{FHIR_BASE}/Observation",
        params={
            "patient": patient_id,
            "code": loinc_code,
            "_count": "50",
            "_sort": "-date",
        },
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()

    entries = resp.json().get("entry", [])
    if not entries:
        return None

    for entry in entries:
        resource = entry.get("resource", {})
        vq = resource.get("valueQuantity")
        if vq and "value" in vq:
            try:
                return float(vq["value"])
            except (TypeError, ValueError):
                continue
    return None


def _get_age(birth_date_str: str) -> int:
    bd = date.fromisoformat(birth_date_str)
    today = date.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def _get_sex(patient_resource: dict) -> str:
    gender = patient_resource.get("gender", "").lower()
    return gender if gender in ("male", "female") else "unknown"


def _has_condition(patient_id: str, snomed_code: str) -> bool:
    resp = requests.get(
        f"{FHIR_BASE}/Condition",
        params={
            "patient": patient_id,
            "code": snomed_code,
            "clinical-status": "active",
            "_count": "1",
        },
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return bool(resp.json().get("entry"))


def _has_medication(patient_id: str, rxnorm_codes: list[str]) -> bool:
    for code in rxnorm_codes:
        resp = requests.get(
            f"{FHIR_BASE}/MedicationRequest",
            params={
                "patient": patient_id,
                "code": code,
                "status": "active",
                "_count": "1",
            },
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        if resp.json().get("entry"):
            return True
    return False


def get_patient_data(patient_id: str) -> dict:
    pt_resp = requests.get(
        f"{FHIR_BASE}/Patient/{patient_id}",
        headers=HEADERS,
        timeout=10,
    )
    pt_resp.raise_for_status()
    pt = pt_resp.json()

    age = _get_age(pt["birthDate"]) if "birthDate" in pt else None
    sex = _get_sex(pt)

    name_parts = pt.get("name", [{}])[0]
    given = " ".join(name_parts.get("given", []))
    family = name_parts.get("family", "")
    full_name = f"{given} {family}".strip()

    total_chol = _latest_observation(patient_id, LOINC["total_cholesterol"])
    hdl_chol = _latest_observation(patient_id, LOINC["hdl_cholesterol"])
    systolic = _latest_observation(patient_id, LOINC["systolic_bp"])
    hba1c = _latest_observation(patient_id, LOINC["hba1c"])
    egfr = _latest_observation(patient_id, LOINC["egfr"])
    urine_acr = _latest_observation(patient_id, LOINC["urine_acr"])

    diabetes = True if hba1c is not None and hba1c >= 6.5 else _has_condition(patient_id, "73211009")
    smoker = _has_condition(patient_id, "77176002")
    bp_treatment = _has_medication(patient_id, ["29046", "17767", "203160"])

    return {
        "patient_id": patient_id,
        "name": full_name,
        "age": age,
        "sex": sex,
        "total_cholesterol": total_chol,
        "hdl_cholesterol": hdl_chol,
        "systolic_bp": systolic,
        "hba1c": hba1c,
        "egfr": egfr,
        "urine_acr": urine_acr,
        "diabetes": diabetes,
        "smoker": smoker,
        "bp_treatment": bp_treatment,
    }