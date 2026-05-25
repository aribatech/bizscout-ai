import uuid
from datetime import datetime, timezone

from app.db.repositories import (
    update_campaign_status, create_business, get_campaign
)
from app.services.websocket_service import manager
from app.agents.search_planning_agent import run_search_planning_agent
from app.agents.business_discovery_agent import run_business_discovery_agent
from app.agents.website_collection_agent import run_website_collection_agent
from app.agents.business_profile_agent import run_business_profile_agent
from app.agents.problem_detection_agent import run_problem_detection_agent
from app.agents.opportunity_scoring_agent import run_opportunity_scoring_agent
from app.agents.service_recommendation_agent import run_service_recommendation_agent
from app.agents.action_planning_agent import run_action_planning_agent


def now():
    return datetime.now(timezone.utc)


async def emit(campaign_id: str, event_type: str, message: str, extra: dict = None):
    payload = {"type": event_type, "message": message}
    if extra:
        payload.update(extra)
    await manager.broadcast(campaign_id, payload)


async def run_campaign_workflow(campaign_id: str):
    campaign = await get_campaign(campaign_id)
    if not campaign:
        return

    niche = campaign["business_niche"]
    location = campaign["location"]
    service = campaign["service_offered"]
    target = campaign.get("target_count", 10)

    try:
        await update_campaign_status(campaign_id, "RUNNING")
        await emit(campaign_id, "AGENT_STARTED", "Search Planning Agent: creating search queries...")

        queries = await run_search_planning_agent(niche, location, service)
        print(f"[worker] generated {len(queries)} queries")

        await emit(campaign_id, "AGENT_COMPLETED", f"Search Planning Agent: {len(queries)} queries created.", {"queries": queries})

        await emit(campaign_id, "AGENT_STARTED", "Business Discovery Agent: searching for businesses...")

        raw_businesses = await run_business_discovery_agent(queries, target)
        print(f"[worker] found {len(raw_businesses)} businesses")

        await emit(campaign_id, "AGENT_COMPLETED", f"Business Discovery Agent: {len(raw_businesses)} businesses found.")
        if not raw_businesses:
            await update_campaign_status(campaign_id, "PARTIAL")
            await emit(campaign_id, "CAMPAIGN_COMPLETED", "No businesses found. Try a different niche or location.")
            return

        for i, raw in enumerate(raw_businesses):
            website = raw.get("website", "")
            biz_name = raw.get("name", website)

            await emit(campaign_id, "BUSINESS_STARTED", f"Analyzing {biz_name} ({i+1}/{len(raw_businesses)})...")

            try:
                collected = await run_website_collection_agent(website)
                profile = await run_business_profile_agent(website, collected.get("full_text", ""))

                problem_result = await run_problem_detection_agent(
                    service, profile, collected.get("full_text", "")
                )
                problems = problem_result.get("problems", [])

                score_result = await run_opportunity_scoring_agent(
                    niche, location, service, profile, problems
                )

                recommendation = await run_service_recommendation_agent(
                    service, profile, problems
                )

                action = await run_action_planning_agent(
                    score_result.get("opportunity_score", 0),
                    score_result.get("fit_level", "Low"),
                    problems,
                    recommendation.get("recommended_service", service)
                )

                business_id = str(uuid.uuid4())
                business_record = {
                    "id": business_id,
                    "campaign_id": campaign_id,
                    "name": profile.get("business_name") or biz_name,
                    "category": profile.get("category"),
                    "location": profile.get("location") or location,
                    "website": website,
                    "summary": profile.get("summary"),
                    "contact": {
                        "emails": collected.get("detected_emails", []),
                        "phones": collected.get("detected_phones", []),
                        "whatsapp_available": collected.get("has_whatsapp_link", False)
                    },
                    "problems": problems,
                    "opportunity_score": score_result.get("opportunity_score"),
                    "fit_level": score_result.get("fit_level"),
                    "priority": score_result.get("priority"),
                    "score_reason": score_result.get("reason"),
                    "recommended_service": recommendation.get("recommended_service"),
                    "service_reason": recommendation.get("why_this_service"),
                    "expected_business_value": recommendation.get("expected_business_value", []),
                    "next_action": action.get("next_action"),
                    "status": action.get("suggested_status", "New"),
                    "notes": [],
                    "created_at": now(),
                    "updated_at": now()
                }

                await create_business(business_record)
                print(f"[worker] saved {biz_name} — score: {score_result.get('opportunity_score')}")

                await emit(campaign_id, "BUSINESS_ANALYZED", f"Done: {biz_name}", {
                    "business_name": business_record["name"],
                    "score": score_result.get("opportunity_score"),
                    "fit_level": score_result.get("fit_level"),
                    "priority": score_result.get("priority"),
                    "business_id": business_id
                })

            except Exception as e:
                msg = f"Failed to analyze {biz_name}: {e}"
                print(f"[worker] {msg}")
                await emit(campaign_id, "BUSINESS_FAILED", msg)

        await update_campaign_status(campaign_id, "COMPLETED", {"completed_at": now()})
        print(f"[worker] campaign {campaign_id} completed")
        await emit(campaign_id, "CAMPAIGN_COMPLETED", f"Campaign finished. {len(raw_businesses)} businesses analyzed.", {
            "campaign_id": campaign_id
        })

    except Exception as e:
        msg = f"Campaign failed: {e}"
        print(f"[worker] {msg}")
        await update_campaign_status(campaign_id, "FAILED")
        await emit(campaign_id, "CAMPAIGN_FAILED", msg)
