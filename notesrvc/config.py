import os

from notesrvc.model.person import Person


class Config:

    def __init__(self):
        self.notedoc_repo_location = os.environ['NOTEDOC_FILE_REPO_PATH']
        self.notedoc_active_entities_file = os.environ['NOTEDOC_ACTIVE_ENTITIES_FILE']
        self.person_repo_file = os.environ['PERSON_REPO_FILE']
        self.default_person = Person('Rob', 'Wood', 'Rob W.')

# PERSON_REPO_FILE=/Users/robertwood/Project.ThoughtPal/NoteDocExtracts/PersonRepo.json