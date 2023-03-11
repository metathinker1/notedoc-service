
from notesrvc.model.notedoc import NoteDocument


class NoteDocParseState:

    def __init__(self, notedoc: NoteDocument):
        self.notedoc = notedoc
        self.note = None
        self.body_text_lines = None
        self.outline_location = []
