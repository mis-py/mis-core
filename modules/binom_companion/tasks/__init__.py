from core.utils.module.components import ScheduledTasks
from modules.binom_companion.tasks import domain_checker, maintenance, proxy_change

scheduled_tasks = ScheduledTasks()
scheduled_tasks.extend(domain_checker.scheduled_tasks._tasks)
scheduled_tasks.extend(maintenance.scheduled_tasks._tasks)
scheduled_tasks.extend(proxy_change.scheduled_tasks._tasks)

