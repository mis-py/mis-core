from tortoise.query_utils import Prefetch

from core.repositories.base.repository import TortoiseORMRepository
from modules.binom_companion.db.models import ReplacementHistory


class TrackerInstanceRepository(TortoiseORMRepository):
    pass


class ReplacementGroupRepository(TortoiseORMRepository):

    async def filter_queryable_with_history(self, **filters):
        history_queryset = ReplacementHistory.all().prefetch_related(
            'to_domain', 'replaced_by', 'from_domains'
        ).order_by('-date_changed')

        return self.model.filter(**filters).prefetch_related(
            Prefetch("replacement_history", queryset=history_queryset),
            'tracker_instance'
        )

    async def get_with_history(self, history_limit: int, replacement_group_id:int,  **filters):
        history_queryset = ReplacementHistory.filter(replacement_group_id=replacement_group_id).prefetch_related(
            'to_domain', 'replaced_by', 'from_domains'
        ).limit(history_limit).order_by('-date_changed')
        return await self.model.get(**filters).prefetch_related(
            Prefetch("replacement_history", queryset=history_queryset),
            'tracker_instance'
        )


class ProxyDomainRepository(TortoiseORMRepository):
    async def update_bulk(self, data_items: list[dict], update_fields: list[str]):
        ids = [item['id'] for item in data_items]
        objects = await self.model.filter(id__in=ids)

        id_to_obj = {obj.pk: obj for obj in objects}
        for item in data_items:
            id_obj = item.pop('id')
            obj = id_to_obj.get(id_obj)
            if not obj:
                continue
            await obj.update_from_dict(item)

        await self.model.bulk_update(objects=objects, fields=update_fields)


class ReplacementHistoryRepository(TortoiseORMRepository):
    pass


class LeadRecordRepository(TortoiseORMRepository):
    pass
