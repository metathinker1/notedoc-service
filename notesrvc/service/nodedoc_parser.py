import re

from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.note import Note
from notesrvc.model.notedoc_parse_state import NoteDocOutlineParseState

from notesrvc.constants import BEGIN_NOTE_PATTERN


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
        parse = NoteDocOutlineParser._start
        lines = raw_text.split('\n')
        for line in lines:
            parse = parse(line, parse_state)
        return notedoc

    # TODO: what return type can I use ?
    @staticmethod
    def _start(line: str, parse_state: NoteDocOutlineParseState):
        match = re.search(BEGIN_NOTE_PATTERN, line)
        if match:
            return NoteDocOutlineParser._new_note(line, parse_state)
        else:
            return NoteDocOutlineParser._start

    @staticmethod
    def _new_note(line: str, parse_state: NoteDocOutlineParseState):
        if parse_state.note:
            parse_state.note.body_text = '\n'.join(parse_state.body_text_lines)
        parse_state.note = Note()
        parse_state.note.note_id = 'N' + str(parse_state.notedoc.size())
        parse_state.body_text_lines = []
        return NoteDocOutlineParser._summary_text

    @staticmethod
    def _summary_text(line: str, parse_state: NoteDocument):
        parse_state.note.summary_text = line
        return NoteDocOutlineParser._body_text

    @staticmethod
    def _body_text(line: str, parse_state: NoteDocument):
        match = re.search(BEGIN_NOTE_PATTERN, line)
        if match:
            return NoteDocOutlineParser._new_note(line, parse_state)
        else:
            parse_state.body_text_lines.append(line)
            return NoteDocOutlineParser._body_text



