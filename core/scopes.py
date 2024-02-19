
class SCOPE:
    USERS: str = 'users'
    TEAMS: str = 'teams'
    ACCESS_GROUPS: str = 'access_groups'
    NOTIFICATIONS: str = 'notifications'
    TASKS: str = 'tasks'
    JOBS: str = 'jobs'
    CONSUMERS: str = 'consumers'
    LOGS: str = 'logs'
    MODULES: str = 'modules'

    @classmethod
    def __getattr__(cls, prop):
        if prop not in cls.__dict__:
            raise AttributeError(f"Property '{prop}' is unknown!")

        return f"core:{cls.__dict__[prop]}"

    @classmethod
    def __setattr__(cls, key, value):
        raise AttributeError("Setting values is forbidden!")
