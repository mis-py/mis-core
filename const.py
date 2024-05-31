import os
from pathlib import Path

MIS_TITLE = 'MIS Project API'
MIS_VERSION = '2.0.3'

# static config variables never changes
DEFAULT_ADMIN_USERNAME = 'admin'

MODULES_DIR_NAME = 'modules'
MODULES_DATA_DIR_NAME = 'modules_data'
LOGS_DIR_NAME = 'logs'
TASKS_DIR_NAME = 'tasks'
# root project dir where main.py exist
BASE_DIR = Path(__file__).parent
# modules sources dir
MODULES_DIR = BASE_DIR / MODULES_DIR_NAME
# modules data dir where they store some files
APPDATA_DIR = BASE_DIR / MODULES_DATA_DIR_NAME
# unused
# FRONTEND_DIR = BASE_DIR / 'frontend'
# unused
# MIGRATIONS_DIR = BASE_DIR / 'migrations'
LOGS_DIR = BASE_DIR / LOGS_DIR_NAME
TASK_LOGS_DIR = LOGS_DIR / TASKS_DIR_NAME
TIMEZONE: str = os.getenv('TIMEZONE', 'Europe/Kyiv')

MODULES_DIR.mkdir(exist_ok=True, mode=775)
APPDATA_DIR.mkdir(exist_ok=True, mode=775)
# FRONTEND_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True, mode=775)

DEV_ENVIRONMENT = 'dev'
LOCAL_ENVIRONMENT = 'local'
PROD_ENVIRONMENT = 'prod'

ENVIRONMENT: str = os.getenv('ENVIRONMENT', DEV_ENVIRONMENT)

ENV_FILE = BASE_DIR / 'env_override' / ENVIRONMENT
