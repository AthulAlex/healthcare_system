import requests
from django.conf import settings

def generate_health_report(resident, vitals, lab_reports):
    vitals_text = ""
    if vitals:
        for v in vitals:
            vitals_text += f"""
- Date: {v.recorded_at.strftime('%d %b %Y')}
  Blood Pressure: {v.blood_pressure}
  Pulse Rate: {v.pulse_rate} bpm
  Oxygen Level: {v.oxygen_level}%
  Temperature: {v.temperature}°C
  Blood Sugar: {v.blood_sugar} mg/dL
  Status: {'Abnormal' if v.is_abnormal else 'Normal'}
"""
    else:
        vitals_text = "No vitals recorded."

    labs_text = ""
    if lab_reports:
        for lab in lab_reports:
            labs_text += f"""
- Test: {lab.test_name}
  Result: {lab.result_value} {lab.unit}
  Normal Range: {lab.normal_range}
  Status: {'Critical' if lab.is_critical else 'Normal'}
"""
    else:
        labs_text = "No lab reports recorded."

    prompt = f"""
You are a medical AI assistant for an old age home.
Analyze the health data and return ONLY a JSON object, nothing else.

RESIDENT: {resident.full_name}
DOB: {resident.date_of_birth}
Gender: {resident.gender}
Blood Group: {resident.blood_group}
Medical History: {resident.medical_history or 'None'}

VITALS:
{vitals_text}

LAB REPORTS:
{labs_text}

Return ONLY this JSON format:
{{
    "risk_score": <integer 0-100>,
    "risk_level": "<Low|Medium|High>",
    "factors": "<comma separated key factors>",
    "summary": "<3-4 sentence health summary>"
}}
"""

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data    = response.json()
    content = data["choices"][0]["message"]["content"]

    # Parse JSON response
    import json
    try:
        clean = content.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except:
        return {
            "risk_score": 0,
            "risk_level": "Low",
            "factors":    "Unable to parse",
            "summary":    content
        }