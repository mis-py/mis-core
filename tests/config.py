import logging

from libs.tortoise_manager import TortoiseManager

log = logging.getLogger(__name__)

logging.getLogger('passlib').setLevel(logging.ERROR)

DB_URL_WITHOUT_NAME = TortoiseManager._db_url.rsplit('/', 1)[0]
UNITTEST_DB_URL = DB_URL_WITHOUT_NAME + '/unittest_db'
