"""User reports. They enter as unverified input and never overwrite confirmed evidence."""

from typing import Annotated

from fastapi import APIRouter, Query, status
from pydantic import BaseModel
from routeable_model import AccessibilityReport, NewAccessibilityReport

from ..dependencies import PLACE_ID_PATTERN, ServiceDep

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportListResponse(BaseModel):
    reports: list[AccessibilityReport]


@router.post("", response_model=AccessibilityReport, status_code=status.HTTP_202_ACCEPTED)
async def create_report(
    service: ServiceDep, report: NewAccessibilityReport
) -> AccessibilityReport:
    return await service.report_issue(report)


@router.get("", response_model=ReportListResponse)
async def list_reports(
    service: ServiceDep,
    place_id: Annotated[str | None, Query(pattern=PLACE_ID_PATTERN)] = None,
) -> ReportListResponse:
    return ReportListResponse(reports=await service.list_reports(place_id))
