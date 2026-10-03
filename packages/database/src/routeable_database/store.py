"""PostgreSQL implementation of the evidence store."""

from datetime import datetime
from typing import Any

from psycopg.types.json import Json
from psycopg_pool import AsyncConnectionPool
from routeable_model import (
    AccessibilityReport,
    CommunityContribution,
    CommunityFeatureKey,
    DataSource,
    Evidence,
    ExternalIds,
    FeatureKey,
    GeoLocation,
    Place,
)

Row = dict[str, Any]


def _to_place(row: Row) -> Place:
    return Place(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        address=row["address"],
        location=GeoLocation(lat=row["latitude"], lng=row["longitude"]),
        external_ids=ExternalIds.model_validate(row["external_ids"] or {}),
    )


def _to_evidence(row: Row) -> Evidence:
    return Evidence(
        id=str(row["id"]),
        place_id=row["place_id"],
        feature_key=row["feature_key"],
        source=DataSource(
            id=row["source_id"],
            type=row["source_type"],
            name=row["source_name"],
            url=row["source_url"] or row["source_base_url"],
            license=row["source_license"],
        ),
        value=row["value"],
        retrieved_at=row["retrieved_at"],
        observed_at=row["observed_at"],
        verification_status=row["verification_status"],
        raw_data=row["raw_data"],
    )


def _to_community_contribution(row: Row) -> CommunityContribution:
    return CommunityContribution(
        id=str(row["id"]),
        place_id=row["place_id"],
        feature_key=row["feature_key"],
        value=row["value"],
        submitted_at=row["submitted_at"],
    )


class PostgresEvidenceStore:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def save_place(self, place: Place) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO places
                    (id, name, category, address, latitude, longitude, external_ids)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                   SET name = EXCLUDED.name,
                       category = EXCLUDED.category,
                       address = EXCLUDED.address,
                       latitude = EXCLUDED.latitude,
                       longitude = EXCLUDED.longitude,
                       external_ids = EXCLUDED.external_ids,
                       updated_at = now()
                """,
                (
                    place.id,
                    place.name,
                    place.category.value,
                    place.address,
                    place.location.lat,
                    place.location.lng,
                    Json(place.external_ids.model_dump(exclude_none=True)),
                ),
            )

    async def get_place(self, place_id: str) -> Place | None:
        async with self._pool.connection() as conn:
            cursor = await conn.execute("SELECT * FROM places WHERE id = %s", (place_id,))
            row = await cursor.fetchone()
        return _to_place(row) if row else None

    async def search_places(self, query: str, limit: int) -> list[Place]:
        async with self._pool.connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM places WHERE name ILIKE %s ORDER BY name LIMIT %s",
                (f"%{query}%", limit),
            )
            rows = await cursor.fetchall()
        return [_to_place(row) for row in rows]

    async def replace_provider_evidence(
        self, place_id: str, provider_name: str, evidence: list[Evidence]
    ) -> None:
        async with self._pool.connection() as conn, conn.transaction():
            source = evidence[0].source if evidence else None
            if source is not None:
                await conn.execute(
                    """
                    INSERT INTO sources (id, type, name, url, license)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                       SET type = EXCLUDED.type,
                           name = EXCLUDED.name,
                           license = EXCLUDED.license
                    """,
                    (
                        provider_name,
                        source.type.value,
                        source.name,
                        source.url,
                        source.license,
                    ),
                )

            await conn.execute(
                "DELETE FROM evidence WHERE place_id = %s AND source_id = %s",
                (place_id, provider_name),
            )

            for item in evidence:
                await conn.execute(
                    """
                    INSERT INTO evidence
                        (id, place_id, source_id, feature_key, value, source_url,
                         verification_status, retrieved_at, observed_at, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.id,
                        place_id,
                        provider_name,
                        item.feature_key.value,
                        Json(item.value),
                        item.source.url,
                        item.verification_status.value,
                        item.retrieved_at,
                        item.observed_at,
                        Json(item.raw_data),
                    ),
                )

    async def get_evidence(
        self, place_id: str, feature_key: FeatureKey | None = None
    ) -> list[Evidence]:
        async with self._pool.connection() as conn:
            cursor = await conn.execute(
                """
                SELECT e.*,
                       s.type    AS source_type,
                       s.name    AS source_name,
                       s.license AS source_license,
                       s.url     AS source_base_url
                  FROM evidence e
                  JOIN sources s ON s.id = e.source_id
                 WHERE e.place_id = %s
                   AND (%s::text IS NULL OR e.feature_key = %s)
                 ORDER BY e.retrieved_at DESC
                """,
                (place_id, feature_key, feature_key),
            )
            rows = await cursor.fetchall()
        return [_to_evidence(row) for row in rows]

    async def get_last_fetched_at(self, place_id: str, provider_name: str) -> datetime | None:
        async with self._pool.connection() as conn:
            cursor = await conn.execute(
                """
                SELECT fetched_at
                  FROM place_provider_fetches
                 WHERE place_id = %s AND provider = %s
                """,
                (place_id, provider_name),
            )
            row = await cursor.fetchone()
        return row["fetched_at"] if row else None

    async def set_last_fetched_at(self, place_id: str, provider_name: str, at: datetime) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO place_provider_fetches (place_id, provider, fetched_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (place_id, provider)
                DO UPDATE SET fetched_at = EXCLUDED.fetched_at
                """,
                (place_id, provider_name, at),
            )

    async def save_report(self, report: AccessibilityReport) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO user_reports
                    (id, place_id, feature_key, issue_type, message,
                     claimed_value, moderation_status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    report.id,
                    report.place_id,
                    report.feature_key.value,
                    report.issue_type.value,
                    report.message,
                    Json(report.claimed_value),
                    report.moderation_status.value,
                    report.created_at,
                ),
            )

    async def list_reports(self, place_id: str | None = None) -> list[AccessibilityReport]:
        async with self._pool.connection() as conn:
            cursor = await conn.execute(
                """
                SELECT * FROM user_reports
                 WHERE (%s::text IS NULL OR place_id = %s)
                 ORDER BY created_at DESC
                """,
                (place_id, place_id),
            )
            rows = await cursor.fetchall()

        return [
            AccessibilityReport(
                id=str(row["id"]),
                place_id=row["place_id"],
                feature_key=row["feature_key"],
                issue_type=row["issue_type"],
                message=row["message"],
                claimed_value=row["claimed_value"],
                moderation_status=row["moderation_status"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    async def add_community_contribution(self, contribution: CommunityContribution) -> None:
        async with self._pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO community_contributions
                    (id, place_id, feature_key, value, submitted_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    contribution.id,
                    contribution.place_id,
                    contribution.feature_key.value,
                    Json(contribution.value),
                    contribution.submitted_at,
                ),
            )

    async def get_community_contributions(
        self,
        place_id: str,
        feature_key: CommunityFeatureKey | None = None,
        since: datetime | None = None,
    ) -> list[CommunityContribution]:
        async with self._pool.connection() as conn:
            cursor = await conn.execute(
                """
                SELECT * FROM community_contributions
                 WHERE place_id = %s
                   AND (%s::text IS NULL OR feature_key = %s)
                   AND (%s::timestamptz IS NULL OR submitted_at >= %s)
                 ORDER BY submitted_at DESC
                """,
                (place_id, feature_key, feature_key, since, since),
            )
            rows = await cursor.fetchall()
        return [_to_community_contribution(row) for row in rows]
