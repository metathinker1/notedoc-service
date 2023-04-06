import re
from datetime import datetime

from notesrvc.model.entity import Entity
from notesrvc.model.person import Person
from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.note import Note, JournalNote
from notesrvc.model.workitem import WorkItem, WorkItemState
from notesrvc.model.notedoc_parse_state import NoteDocParseState
from notesrvc.model.tag import TextTag
from notesrvc.config import Config
from notesrvc.data_access.person_repo import PersonRepo
from notesrvc.data_access.workitem_filerepo import WorkItemFileRepo
from notesrvc.constants import BEGIN_NOTE_PATTERN, BEGIN_JOURNAL_NOTE_PATTERN, BEGIN_TEXT_TAG, END_MULTILINE_TAG, \
    END_SINGLELINE_TAG, DATE_TIME_FORMAT, BEGIN_WORKITEMS_SECTION, END_WORKITEMS_SECTION, BEGIN_WORKITEM

config = Config()


class NoteDocParser:

    def __init__(self, person_repo: PersonRepo, workitem_repo: WorkItemFileRepo):
        self.person_repo = person_repo
        self.workitem_repo = workitem_repo

    def parse_text(self, raw_text: str, notedoc: NoteDocument):
        parse_state = NoteDocParseState(notedoc, self.workitem_repo, self.person_repo)
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
        # print(line[1:-1])
        try:
            date_stamp = datetime.strptime(line.strip()[1:-1], DATE_TIME_FORMAT)
            note_id = 'N' + str(parse_state.notedoc.size())
            parse_state.note = JournalNote(note_id, date_stamp)
            parse_state.body_text_lines = []
            parse_state.tags = []
            parse_state.parse_state = []

            parse_state.notedoc.append_note(parse_state.note)

            return NoteDocParser._summary_text
        except Exception as ex:
            print(f'ERROR: {ex}')
            raise ex

    @staticmethod
    def _summary_text(line: str, parse_state: NoteDocParseState):
        parse_state.note.summary_text = line
        return NoteDocParser._body_text

    @staticmethod
    def _body_text(line: str, parse_state: NoteDocParseState):
        note_match = re.search(BEGIN_NOTE_PATTERN, line)
        journal_note_match = re.search(BEGIN_JOURNAL_NOTE_PATTERN, line)
        text_tag_match = re.search(BEGIN_TEXT_TAG, line)
        workitems_match = re.search(BEGIN_WORKITEMS_SECTION, line)
        if note_match:
            return NoteDocParser._new_note(line, parse_state)
        elif journal_note_match:
            return NoteDocParser._new_journal_note(line, parse_state)
        elif text_tag_match:
            return NoteDocParser._new_text_tag(line, parse_state)
        elif workitems_match:
            return NoteDocParser._workitems_section

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
    def _workitems_section(line: str, parse_state: NoteDocParseState):
        # TODO: Implement
        # Create WorkItem; Populate WorkItem; Return to _body_text
        workitem_match = re.search(BEGIN_WORKITEM, line)
        if workitem_match:
            return NoteDocParser._new_workitem(line, parse_state)
        elif line == END_WORKITEMS_SECTION:
            # TODO: set text on current workitem
            return NoteDocParser._body_text
        elif line.strip().startswith('{') and line.strip().endswith('}'):
            return NoteDocParser._workitem_attributes(line, parse_state)
        else:
            if parse_state.workitem:
                parse_state.workitem_body_text_lines.append(line)
            return NoteDocParser._workitems_section

    @staticmethod
    def _new_workitem(line: str, parse_state: NoteDocParseState):
        if parse_state.workitem:
            parse_state.workitem.body_text = '\n'.join(parse_state.workitem_body_text_lines)

        line_part = line[:line.find(' ')]
        state = NoteDocParser._derive_workitem_state(line_part)
        line_part = line[line.find(' '):]
        line_parts = line_part.split(':')
        if len(line_parts) > 1:
            person = parse_state.person_repo.get_person(line_parts[0].strip())
            summary = line_parts[1]
        else:
            person = parse_state.default_person  # TODO: hard code for now: "Rob Wood"
            summary = line_part
        entity = Entity(parse_state.notedoc.entity_type, parse_state.notedoc.entity_name)
        parse_state.workitem = WorkItem(entity, person)
        parse_state.workitem.state = state
        parse_state.workitem.summary_text = summary
        parse_state.workitem_body_text_lines = []

        parse_state.workitem_repo.add_workitem(parse_state.workitem)

        return NoteDocParser._workitems_section

    @staticmethod
    def _derive_workitem_state(status_text):
        if len(status_text) == 2:
            return WorkItemState.derive_from_abbreviation('')
        else:
            return WorkItemState.derive_from_abbreviation(status_text[-1])

    @staticmethod
    def _workitem_attributes(line: str, parse_state: NoteDocParseState):
        # parse_state.workitem.summary_text = line
        attributes = line.strip()[1:-1].split('|')
        for attribute in attributes:
            if '=' in attribute:
                name_value = attribute.strip().split('=')
                if name_value[0].strip() == 'Date':
                    parse_state.workitem.set_date_defined_str(name_value[1].strip())
                else:
                    name = name_value[0].strip()
                    value = name_value[1].strip()
                    d = {name: value}  # No idea why Python crashes if don't use d
                    parse_state.workitem.attributes.append(d)
        return NoteDocParser._workitems_section

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
        parts = text_tag.headline_text.split(":")
        if parts and len(parts) > 0:
            # TODO: validate with TEXT_TAG_TYPES
            text_tag.text_tag_type = parts[0]
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
