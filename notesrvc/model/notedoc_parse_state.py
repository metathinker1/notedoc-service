
from notesrvc.model.notedoc import NoteDocument


class NoteDocParseState:

    def __init__(self, notedoc: NoteDocument):
        self.notedoc = notedoc
        self.current_note = None
        self.body_text_lines = None


class NoteDocOutlineParseState(NoteDocParseState):

    def __init__(self, notedoc: NoteDocument):
        super().__init__(notedoc)
        self.outline_location = []
