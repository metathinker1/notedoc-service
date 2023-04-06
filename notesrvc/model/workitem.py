from datetime import datetime
from notesrvc.model.entity import Entity
from notesrvc.model.person import Person
from notesrvc.constants import DATE_TIME_FORMAT, DATE_FORMAT


class WorkItem:

    def __init__(self, entity: Entity, person: Person = None, workitem_id: str = None, date_defined: datetime = None):
        self.workitem_id = workitem_id
        self.entity = entity
        self.person = person

        self.summary_text = ''
        self.body_text = ''
        # TODO: Put into set_datestamp() ?
        if date_defined:
            self.date_defined = date_defined
            self.date_defined_str = self.date_defined.strftime(DATE_FORMAT)
        else:
            self.date_defined = None

        self.tags = list()
        self.attributes = list()
        self.state = WorkItemState.DEFINED

    def set_date_defined_str(self, date_defined_str: str):
        self.date_defined_str = date_defined_str
        self.date_defined = datetime.strptime(self.date_defined_str, DATE_FORMAT)

class WorkItemState:
    IDEATION = 'Ideation'
    DEFINED = 'Defined'
    IN_PROGRESS = 'InProgress'
    PAUSED = 'Paused'
    BLOCKED = 'Blacked'
    CANCELLED = 'Cancelled'
    DONE = 'Done'

    @staticmethod
    def derive_from_abbreviation(abbr: str):
        if abbr == 'E':
            return WorkItemState.IDEATION
        elif abbr == 'I':
            return WorkItemState.IN_PROGRESS
        elif abbr == 'P':
            return WorkItemState.PAUSED
        elif abbr == 'B':
            return WorkItemState.BLOCKED
        elif abbr == 'X':
            return WorkItemState.CANCELLED
        elif abbr == 'D':
            return WorkItemState.DONE
        else:
            return WorkItemState.DEFINED
