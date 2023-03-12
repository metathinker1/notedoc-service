import re
from datetime import datetime

from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.note import Note, JournalNote
from notesrvc.model.notedoc_parse_state import NoteDocParseState
from notesrvc.model.tag import TextTag

from notesrvc.constants import BEGIN_NOTE_PATTERN, BEGIN_JOURNAL_NOTE_PATTERN, BEGIN_TEXT_TAG, END_MULTILINE_TAG, \
    END_SINGLELINE_TAG, DATE_TIME_FORMAT


class NoteDocParser:

    def __init__(self):
        pass

    def parse_text(self, raw_text: str, notedoc: NoteDocument):
        parse_state = NoteDocParseState(notedoc)
        parse = NoteDocParser._start
        lines = raw_text.split('\n')
        for line in lines:
            parse = parse(line, parse_state)
        return notedoc

    # TODO: what return type can I use ?
    @staticmethod
    def _start(line: str, parse_state: NoteDocParseState):
        note_match = re.search(BEGIN_NOTE_PATTERN, line)
        journal_note_match = re.search(BEGIN_JOURNAL_NOTE_PATTERN, line)
        if note_match:
            return NoteDocParser._new_note(line, parse_state)
        elif journal_note_match:
            return NoteDocParser._new_journal_note(line, parse_state)
        else:
            return NoteDocParser._start

    @staticmethod
    def _new_note(line: str, parse_state: NoteDocParseState):
        if parse_state.note:
            parse_state.note.body_text = '\n'.join(parse_state.body_text_lines)
        parse_state.note = Note()
        parse_state.note.note_id = 'N' + str(parse_state.notedoc.size())
        parse_state.body_text_lines = []
        parse_state.tags = []

        outline_level = int(line[6:-1])
        parent_loc = NoteDocParser._calc_parent_outline_location(outline_level, parse_state)
        parse_state.notedoc.append_note(parse_state.note, parent_loc)

        return NoteDocParser._summary_text

    @staticmethod
    def _new_journal_note(line: str, parse_state: NoteDocParseState):
        if parse_state.note:
            parse_state.note.body_text = '\n'.join(parse_state.body_text_lines)
        parse_state.note = JournalNote()
        parse_state.note.note_id = 'N' + str(parse_state.notedoc.size())
        print(line[1:-1])
        date_stamp = datetime.strptime(line[1:-1], DATE_TIME_FORMAT)
        parse_state.note.date_stamp = date_stamp
        parse_state.body_text_lines = []
        parse_state.tags = []
        parse_state.parse_state = []

        parse_state.notedoc.append_note(parse_state.note)

        return NoteDocParser._summary_text

    @staticmethod
    def _summary_text(line: str, parse_state: NoteDocParseState):
        parse_state.note.summary_text = line
        return NoteDocParser._body_text

    @staticmethod
    def _body_text(line: str, parse_state: NoteDocParseState):
        note_match = re.search(BEGIN_NOTE_PATTERN, line)
        journal_note_match = re.search(BEGIN_JOURNAL_NOTE_PATTERN, line)
        text_tag_match = re.search(BEGIN_TEXT_TAG, line)
        if note_match:
            return NoteDocParser._new_note(line, parse_state)
        elif journal_note_match:
            return NoteDocParser._new_journal_note(line, parse_state)
        elif text_tag_match:
            return NoteDocParser._new_text_tag(line, parse_state)
        else:
            parse_state.body_text_lines.append(line)
            return NoteDocParser._body_text

    @staticmethod
    def _new_text_tag(line: str, parse_state: NoteDocParseState):
        end_singleline_tag = re.search(END_SINGLELINE_TAG, line)
        if end_singleline_tag:
            text_tag = NoteDocParser._create_text_tag(line[:-1], parse_state)
            parse_state.note.tags.append(text_tag)
            if len(parse_state.tags) > 0:
                return NoteDocParser._tag_body_text
            else:
                return NoteDocParser._body_text
        else:
            text_tag = NoteDocParser._create_text_tag(line[:-1], parse_state)
            parse_state.note.tags.append(text_tag)
            parse_state.tags.append(text_tag)
            parse_state.current_tag = parse_state.tags[len(parse_state.tags)-1]
            return NoteDocParser._tag_body_text
    @staticmethod
    def _tag_body_text(line: str, parse_state: NoteDocParseState):
        text_tag_match = re.search(BEGIN_TEXT_TAG, line)
        end_multiline_tag = line == END_MULTILINE_TAG
        if end_multiline_tag:
            if len(parse_state.tags) == 0:
                print(f'ERROR: found unmatched END_MULTILINE_TAG')
            else:
                text_tag = parse_state.tags.pop()
                if len(parse_state.tags) > 0:
                    parse_state.current_tag = parse_state.tags[len(parse_state.tags)-1]
                else:
                    parse_state.current_tag = None
                return NoteDocParser._body_text
        elif text_tag_match:
            return NoteDocParser._new_text_tag(line, parse_state)
        else:
            parse_state.current_tag.body_text += '\n' + line
            return NoteDocParser._tag_body_text

    @staticmethod
    def _create_text_tag(line: str, parse_state: NoteDocParseState) -> TextTag:
        text_tag = TextTag()
        text_tag.tag_id = 'T' + str(len(parse_state.note.tags))
        text_tag.headline_text = line[len(BEGIN_TEXT_TAG):]
        text_tag.body_text = ''
        return text_tag


    # TODO: Consider moving to NoteDocOutlineParseState
    @staticmethod
    def _calc_parent_outline_location(outline_level: int, parse_state: NoteDocParseState):
        if outline_level > len(parse_state.outline_location):
            parse_state.outline_location.append(0)
        elif outline_level < len(parse_state.outline_location):
            num_levels = len(parse_state.outline_location) - outline_level
            for ix in range(num_levels):
                parse_state.outline_location.pop()
            val = parse_state.outline_location.pop()
            parse_state.outline_location.append(val + 1)
        else:
            val = parse_state.outline_location.pop()
            parse_state.outline_location.append(val + 1)

        if len(parse_state.outline_location) > 1:
            return parse_state.outline_location[:-1]
        else:
            return None


from notesrvc.model.notedoc_outline import NoteDocOutline

if __name__ == '__main__':
    # case01 = "}\\"
    # print(case01)
    # check01 = re.search(END_MULTILINE_TAG, case01)
    # print('stop here')

    with open('NoteDocCase01.nodoc', 'r') as file:
        notedoc_text = file.read()

    notedoc_metadata = {}
    notedoc = NoteDocOutline(notedoc_metadata, None)

    notedoc_parser = NoteDocParser()
    notedoc_parser.parse_text(notedoc_text, notedoc)

    notedoc_dict = notedoc.render_as_dict()
    print(f'notedoc_dict: {notedoc_dict}')
