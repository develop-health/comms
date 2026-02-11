"""Ashby ATS API client — candidate search, feedback, stage changes."""

import requests
from requests.auth import HTTPBasicAuth

from ..config import AshbyConfig


def _get_config() -> AshbyConfig:
    config = AshbyConfig()
    if not config.api_key:
        raise ValueError("Missing ASHBY_API_KEY environment variable")
    return config


def _post(endpoint: str, payload: dict) -> dict:
    config = _get_config()
    resp = requests.post(
        f"{config.base_url}/{endpoint}",
        json=payload,
        auth=HTTPBasicAuth(config.api_key, ""),
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    return resp.json()


def search_candidates(name: str) -> list[dict]:
    """Search candidates by name."""
    data = _post("candidate.search", {"name": name})
    return data.get("results", [])


def get_application(application_id: str) -> dict:
    """Get application details including current stage."""
    data = _post("application.info", {"applicationId": application_id})
    return data.get("results", data)


def list_interview_stages(interview_plan_id: str) -> list[dict]:
    """List ordered stages for an interview plan."""
    data = _post("interviewStage.list", {"interviewPlanId": interview_plan_id})
    return data.get("results", [])


def list_archive_reasons() -> list[dict]:
    """List available archive/rejection reasons."""
    data = _post("archiveReason.list", {})
    return data.get("results", [])


def list_interview_schedules(application_id: str) -> list[dict]:
    """List interview schedules for an application."""
    data = _post(
        "interviewSchedule.list", {"applicationId": application_id}
    )
    return data.get("results", [])


def get_interview(interview_id: str) -> dict:
    """Get interview details including feedback form definition."""
    data = _post("interview.info", {"id": interview_id})
    return data.get("results", data)


def get_feedback_form_definition(form_definition_id: str) -> dict:
    """Get feedback form definition with field paths and types."""
    data = _post(
        "feedbackFormDefinition.info",
        {"feedbackFormDefinitionId": form_definition_id},
    )
    return data.get("results", data)


def submit_feedback(
    application_id: str,
    summary: str,
    score: int,
    recommendation: str,
) -> dict:
    """Submit interview scorecard feedback.

    Discovers the pending interview event and feedback form automatically,
    then submits the overall recommendation plus summary text in the
    Red Flag / Gold Flag or general Feedback fields.
    """
    # 1. Find the pending interview event
    schedules = list_interview_schedules(application_id)
    interview_event_id = None
    interview_id = None
    user_id = None
    for sched in schedules:
        for event in sched.get("interviewEvents", []):
            if not event.get("hasSubmittedFeedback", True):
                interview_event_id = event["id"]
                interview_id = event.get("interviewId")
                interviewer_ids = event.get("interviewerUserIds", [])
                if interviewer_ids:
                    user_id = interviewer_ids[0]
                break
        if interview_event_id:
            break

    if not interview_event_id or not interview_id:
        raise ValueError(
            "No pending interview event found for this application. "
            "Feedback may have already been submitted."
        )

    # 2. Get the feedback form definition from the interview
    interview_info = get_interview(interview_id)
    form_def_id = interview_info.get("feedbackFormDefinitionId")
    if not form_def_id:
        raise ValueError(
            f"No feedback form definition found for interview {interview_id}"
        )

    # 3. Get form fields to find the right paths
    form_def = get_feedback_form_definition(form_def_id)
    recommendation_path = None
    richtext_paths: list[str] = []
    for section in form_def.get("sections", []):
        for field in section.get("fields", []):
            if field.get("type") == "ValueSelect":
                recommendation_path = field.get("path", "overall_recommendation")
            elif field.get("type") == "RichText":
                richtext_paths.append(field.get("path"))

    if not recommendation_path:
        recommendation_path = "overall_recommendation"

    # 4. Build field submissions
    field_submissions = [
        {"path": recommendation_path, "value": str(score)},
    ]
    # Put summary in the first available RichText field
    if richtext_paths:
        field_submissions.append({
            "path": richtext_paths[0],
            "value": {"type": "PlainText", "value": summary},
        })

    # 5. Submit
    payload: dict = {
        "applicationId": application_id,
        "formDefinitionId": form_def_id,
        "interviewEventId": interview_event_id,
        "feedbackForm": {"fieldSubmissions": field_submissions},
    }
    if user_id:
        payload["userId"] = user_id

    data = _post("applicationFeedback.submit", payload)
    return data.get("results", data)


def progress_candidate(
    application_id: str, interview_stage_id: str
) -> dict:
    """Move candidate to the next interview stage."""
    data = _post(
        "application.changeStage",
        {
            "applicationId": application_id,
            "interviewStageId": interview_stage_id,
        },
    )
    return data.get("results", data)


def reject_candidate(
    application_id: str,
    archive_reason_id: str,
    rejection_template_id: str = "07e79d76-8a03-44ac-9c2d-76ad5d4e3ab7",
) -> dict:
    """Archive/reject candidate with rejection email."""
    data = _post(
        "application.changeStage",
        {
            "applicationId": application_id,
            "archiveReasonId": archive_reason_id,
            "sendRejectionEmail": True,
            "rejectionEmailTemplateId": rejection_template_id,
        },
    )
    return data.get("results", data)
