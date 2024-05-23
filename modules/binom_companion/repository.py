
from tortoise.query_utils import Prefetch
from core.repositories.base.repository import TortoiseORMRepository
from modules.binom_companion.db.models import ReplacementHistory



class TrackerInstanceRepository(TortoiseORMRepository):
    pass


class ReplacementGroupRepository(TortoiseORMRepository):
    pass


        return self.model.filter(**filters).prefetch_related(
            Prefetch("replacement_history", queryset=history_queryset),
            'tracker_instance'
        )

    async def get_with_history(self, history_limit: int, **filters):
        history_queryset = ReplacementHistory.all().prefetch_related(
            'to_domain', 'replaced_by', 'from_domains'
        ).limit(history_limit)
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
