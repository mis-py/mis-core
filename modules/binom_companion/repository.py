from tortoise.query_utils import Prefetch

from core.repositories.base.repository import TortoiseORMRepository
from modules.binom_companion.db.models import ReplacementHistory, TrackerInstance


class TrackerInstanceRepository(TortoiseORMRepository):
    model = TrackerInstance


class ReplacementGroupRepository(TortoiseORMRepository):
    async def filter_queryable_with_history(self, **filters):
        history_queryset = ReplacementHistory.all().prefetch_related(
            'to_domain', 'replaced_by', 'from_domains'
        ).order_by('-date_changed')

        return self.model.filter(**filters).prefetch_related(
            Prefetch("replacement_history", queryset=history_queryset),
            'tracker_instance'
        )

    async def get_with_history(self, history_limit: int, **filters):
        history_queryset = ReplacementHistory.all().prefetch_related(
            'to_domain', 'replaced_by', 'from_domains'
        ).limit(history_limit).order_by('-date_changed')
        return await self.model.get(**filters).prefetch_related(
            Prefetch("replacement_history", queryset=history_queryset),
            'tracker_instance'
        )


class ProxyDomainRepository(TortoiseORMRepository):
    pass


class ReplacementHistoryRepository(TortoiseORMRepository):
    pass


class LeadRecordRepository(TortoiseORMRepository):
    pass
