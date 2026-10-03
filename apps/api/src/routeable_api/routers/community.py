"""Anonymous community answers — uncertain input kept apart from confirmed evidence."""

from fastapi import APIRouter, status

from routeable_model import (
    CommunityAnswer,
    CommunityContribution,
    CommunitySummary,
    NewCommunityContribution,
)

from ..dependencies import PlaceIdPath, ServiceDep

router = APIRouter(prefix="/api/places", tags=["community"])


@router.post(
    "/{place_id}/community",
    response_model=CommunityContribution,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_contribution(
    service: ServiceDep, place_id: PlaceIdPath, answer: CommunityAnswer
) -> CommunityContribution:
    return await service.submit_community_contribution(
        NewCommunityContribution(
            place_id=place_id, feature_key=answer.feature_key, value=answer.value
        )
    )


@router.get("/{place_id}/community", response_model=CommunitySummary)
async def community_summary(service: ServiceDep, place_id: PlaceIdPath) -> CommunitySummary:
    return await service.get_community_summary(place_id)
