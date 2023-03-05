
from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.notedoc_parse_state import NoteDocOutlineParseState


class NoteDocParser:

    def __init__(self):
        pass

    # TODO: Make abstract
    def parse_text(self, raw_text: str):
        pass


class NoteDocOutlineParser(NoteDocParser):

    def __init__(self):
        pass

    def parse_text(self, raw_text: str, notedoc: NoteDocument):
        parse_state = NoteDocOutlineParseState(notedoc)

    def _parse_empty_space(self, parse_state: NoteDocOutlineParseState):
        pass

