
from notesrvc.config import Config

config = Config()


class EntityFileRepo:

    def __init__(self, config: Config):
        self.config = config
        self.entity_repo_cache = dict()
