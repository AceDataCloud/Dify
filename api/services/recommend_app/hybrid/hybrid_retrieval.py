"""Hybrid retrieval: merge remote (or builtin) templates with local DB apps.

DB-registered apps (e.g. AceDataCloud workflow templates) are tagged with
``source`` and placed before the remote/builtin apps.  Duplicates by
``app_id`` are dropped so each app appears only once.
"""

import logging

from services.recommend_app.buildin.buildin_retrieval import BuildInRecommendAppRetrieval
from services.recommend_app.database.database_retrieval import DatabaseRecommendAppRetrieval
from services.recommend_app.recommend_app_base import RecommendAppRetrievalBase
from services.recommend_app.recommend_app_type import RecommendAppType
from services.recommend_app.remote.remote_retrieval import RemoteRecommendAppRetrieval

logger = logging.getLogger(__name__)

# Tag applied to every app coming from the local DB
DB_SOURCE_TAG = "acedatacloud"


class HybridRecommendAppRetrieval(RecommendAppRetrievalBase):
    """Merge remote/builtin recommended apps with locally-registered DB apps."""

    def get_type(self) -> str:
        return RecommendAppType.HYBRID

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def get_recommended_apps_and_categories(self, language: str):
        # 1. Fetch remote (with builtin fallback)
        remote_result = self._fetch_remote_or_builtin(language)

        # 2. Fetch DB
        db_result = DatabaseRecommendAppRetrieval.fetch_recommended_apps_from_db(language)

        # 3. Tag DB apps with source
        for app in db_result.get("recommended_apps") or []:
            app["source"] = DB_SOURCE_TAG

        # 4. Merge: DB first, then remote, dedup
        return self._merge(db_first=db_result, secondary=remote_result)

    # ------------------------------------------------------------------
    # Detail
    # ------------------------------------------------------------------

    def get_recommend_app_detail(self, app_id: str):
        # Try DB first (locally-registered apps take priority)
        db_detail = DatabaseRecommendAppRetrieval.fetch_recommended_app_detail_from_db(app_id)
        if db_detail:
            return db_detail

        # Fall back to remote / builtin
        try:
            return RemoteRecommendAppRetrieval.fetch_recommended_app_detail_from_dify_official(app_id)
        except Exception:
            logger.warning("hybrid: remote detail fetch failed for %s, trying builtin", app_id)
            return BuildInRecommendAppRetrieval.fetch_recommended_app_detail_from_builtin(app_id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fetch_remote_or_builtin(language: str) -> dict:
        try:
            result = RemoteRecommendAppRetrieval.fetch_recommended_apps_from_dify_official(language)
            if result.get("recommended_apps"):
                return result
        except Exception:
            logger.warning("hybrid: remote fetch failed, falling back to builtin")
        return BuildInRecommendAppRetrieval.fetch_recommended_apps_from_builtin("en-US") or {}

    @staticmethod
    def _merge(*, db_first: dict, secondary: dict) -> dict:
        db_apps: list = db_first.get("recommended_apps") or []
        secondary_apps: list = secondary.get("recommended_apps") or []

        seen_ids: set[str] = set()
        merged: list = []

        for app in db_apps:
            aid = app.get("app_id", "")
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                merged.append(app)

        for app in secondary_apps:
            aid = app.get("app_id", "")
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                merged.append(app)

        # Categories: DB first, then secondary, deduplicated, stable order
        seen_cats: set[str] = set()
        cats: list[str] = []
        for cat in (db_first.get("categories") or []) + (secondary.get("categories") or []):
            if cat not in seen_cats:
                seen_cats.add(cat)
                cats.append(cat)

        return {"categories": cats, "recommended_apps": merged}
