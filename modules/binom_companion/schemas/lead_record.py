# from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from modules.binom_companion.db.models import LeadRecord

# Tortoise.init_models(["modules.binom_companion.db.models"], 'binom_companion')

LeadRecordModel = pydantic_model_creator(LeadRecord, name='LeadRecordModel')
