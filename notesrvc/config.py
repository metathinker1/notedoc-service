import os


class Config:

    def __init__(self):
        self.notedoc_repo_location = os.environ['NOTEDOC_FILE_REPO_PATH']
        self.notedoc_active_entities_file = os.environ['NOTEDOC_ACTIVE_ENTITIES_FILE']
