
from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.person import Person
from notesrvc.data_access.workitem_filerepo import WorkItemFileRepo
from notesrvc.data_access.person_repo import PersonRepo


class NoteDocParseState:

    def __init__(self, notedoc: NoteDocument, workitem_repo: WorkItemFileRepo, person_repo: PersonRepo):
        self.notedoc = notedoc
        self.workitem_repo = workitem_repo
        self.person_repo = person_repo
        self.default_person = person_repo.default_person

        self.note = None
        self.body_text_lines = None
        self.outline_location = []
        self.workitem = None
        self.workitem_body_text_lines = None
