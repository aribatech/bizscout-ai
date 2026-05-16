import csv
import io

CSV_FIELDS = [
    "campaign", "name", "category", "location", "website",
    "phone", "email", "problems", "high_severity_problems",
    "opportunity_score", "fit_level", "priority",
    "recommended_service", "reason", "next_action", "status",
    "source_urls", "created_at"
]


def businesses_to_csv(campaign: dict, businesses: list) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()

    campaign_label = f"{campaign.get('business_niche', '')} {campaign.get('location', '')}"

    for b in businesses:
        problems = b.get("problems", [])
        problem_texts = "; ".join(p.get("problem", "") for p in problems)
        high_count = sum(1 for p in problems if p.get("severity") == "high")

        contact = b.get("contact", {})
        phones = contact.get("phones", [])
        emails = contact.get("emails", [])

        row = {
            "campaign": campaign_label,
            "name": b.get("name", ""),
            "category": b.get("category", ""),
            "location": b.get("location", ""),
            "website": b.get("website", ""),
            "phone": phones[0] if phones else "",
            "email": emails[0] if emails else "",
            "problems": problem_texts,
            "high_severity_problems": high_count,
            "opportunity_score": b.get("opportunity_score", ""),
            "fit_level": b.get("fit_level", ""),
            "priority": b.get("priority", ""),
            "recommended_service": b.get("recommended_service", ""),
            "reason": b.get("score_reason", ""),
            "next_action": b.get("next_action", ""),
            "status": b.get("status", ""),
            "source_urls": "; ".join(b.get("source_urls", [])),
            "created_at": str(b.get("created_at", ""))
        }
        writer.writerow(row)

    return output.getvalue()
