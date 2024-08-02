from enum import Enum

from tortoise import timezone


class JobStatus(str, Enum):
    WAITING = "waiting"
    EXECUTING = "executing"
    FAILED = "failed"
    DONE = "done"


class JobExecutionStorage:
    storage: dict = {}

    @classmethod
    def insert(cls, job_id: int):
        if job_id not in cls.storage:
            cls.storage[job_id] = {
                'status': JobStatus.EXECUTING.value,
                'count': 0,
                'items': [],
            }

        cls.storage[job_id]['items'].append({
            'status': JobStatus.EXECUTING.value,
            'run_at': timezone.now(),
            'yield': [],
            'return': None,
            'exception': None,
            'end_at': None,
            'time': None,
        })
        cls.storage[job_id]['count'] += 1

        # remove first item if count more 100
        if len(cls.storage[job_id]) > 100:
            cls.storage[job_id].pop(0)

    @classmethod
    def insert_yield(cls, job_id: int, value):
        """Insert yield value for last execution item"""
        force_str_value = str(value)
        cls.storage[job_id]['items'][-1]['yield'].append(force_str_value)

    @classmethod
    def set_return(cls, job_id: int, value):
        """Set return value for last execution item"""
        force_str_value = str(value)
        cls.storage[job_id]['items'][-1]['return'] = force_str_value

    @classmethod
    def set_exception(cls, job_id: int, value):
        """Set exception value for last execution item"""
        force_str_value = str(value)
        cls.storage[job_id]['items'][-1]['exception'] = force_str_value
        cls.storage[job_id]['items'][-1]['status'] = JobStatus.FAILED.value

    @classmethod
    def set_end(cls, job_id: int):
        """Set end info for last execution item"""
        cls.storage[job_id]['items'][-1]['end_at'] = timezone.now()
        cls.storage[job_id]['items'][-1]['status'] = JobStatus.DONE.value

    @classmethod
    def set_time_execution(cls, job_id: int, seconds: float):
        """Set execution seconds for last execution item"""
        cls.storage[job_id]['items'][-1]['time'] = seconds

    @classmethod
    def get(cls, job_id: int):
        execute_info = cls.storage.get(job_id)
        if not execute_info:
            return {
                'status': JobStatus.WAITING.value,
                'last_run_at': None,
                'avg_time': None,
                'count': 0,
                'items': [],
            }
        executions = execute_info['items']
        time_executions = [item['time'] for item in executions if item['time']]
        avg_execution_time = sum(time_executions) / len(time_executions) if len(time_executions) > 0 else None
        return {
            'status': 'waiting' if executions[-1]['status'] == 'done' else 'running',
            'avg_time': avg_execution_time,
            'last_run_at': executions[-1]['run_at'],
            'count': len(executions),
            'items': executions,
        }
