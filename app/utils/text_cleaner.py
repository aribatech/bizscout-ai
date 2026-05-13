import json
import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_json_safe(text: str) -> dict | list:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except Exception:
                continue
    return json.loads(text)


def extract_emails(text: str) -> list:
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(pattern, text)))
    junk = ["noreply", "example", ".png", ".jpg", "test@"]
    return [e for e in emails if not any(j in e for j in junk)]


def extract_phones(text: str) -> list:
    pattern = r'(\+?\d[\d\s\-().]{7,}\d)'
    return list(set(re.findall(pattern, text)))[:5]


def extract_whatsapp(text: str) -> bool:
    return "whatsapp" in text.lower() or "wa.me" in text.lower()
