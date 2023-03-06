
from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.notedoc_outline import NoteDocOutline

class NoteDocParseState:

    def __init__(self, notedoc: NoteDocument):
        self.notedoc = notedoc
        self.note = None
        self.body_text_lines = None


class NoteDocOutlineParseState(NoteDocParseState):

    def __init__(self, notedoc: NoteDocOutline):
        super().__init__(notedoc)
        self.outline_location = []
