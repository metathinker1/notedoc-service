from datetime import datetime

from notesrvc.config import Config
from notesrvc.model.workitem import WorkItem, WorkItemState, ACTIVE_WORKITEM_STATES

config = Config()


class WorkItemFileRepo:

    def __init__(self, config: Config):
        self.config = config
        self.workitem_repo_cache = list()

    def add_workitem(self, workitem: WorkItem):
        self.workitem_repo_cache.append(workitem)

    def get_active_workitems(self):
        active_workitems = list()
        for workitem in self.workitem_repo_cache:
            if workitem.state in ACTIVE_WORKITEM_STATES:
                active_workitems.append(workitem)
        return active_workitems

    def get_done_workitems(self, earliest_done_date: datetime, latest_done_date: datetime = None):
        done_workitems = list()
        for workitem in self.workitem_repo_cache:
            if workitem.date_done:
                if workitem.state == WorkItemState.DONE and workitem.date_done >= earliest_done_date:
                    if latest_done_date:
                        if workitem.date_done <= latest_done_date:
                            done_workitems.append(workitem)
                    else:
                        done_workitems.append(workitem)
        return done_workitems
