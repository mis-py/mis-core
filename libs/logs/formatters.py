class Formatter:

    def __init__(self, fmt: str, context_key: str):
        self.fmt = fmt + "\n{exception}"
        self.context_key = context_key

    def format(self, record):
        if not record['extra'].get('context_key'):
            record['extra']['context_key'] = self.context_key
        return self.fmt
