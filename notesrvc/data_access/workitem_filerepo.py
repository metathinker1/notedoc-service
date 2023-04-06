from notesrvc.config import Config
from notesrvc.model.workitem import WorkItem

config = Config()


class WorkItemFileRepo:

    def __init__(self, config: Config):
        self.config = config
        self.workitem_repo_cache = list()

    def add_workitem(self, workitem: WorkItem):
        self.workitem_repo_cache.append(workitem)

    def get_workitems(self, **kwargs):
        pass
