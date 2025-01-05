
from datetime import datetime

from notesrvc.model.notecoll import NoteCollection
from notesrvc.model.note import Note
from notesrvc.constants import EntityAspect

class NoteDocument:

    def __init__(self, notedoc_metadata: dict):
        self.notedoc_id = notedoc_metadata.get('NoteDocId')
        self.entity_type = notedoc_metadata.get('EntityType')
        self.entity_name = notedoc_metadata.get('EntityName')
        self.entity_aspect = notedoc_metadata.get('EntityAspect')
        # TODO: Research: best practice: field with type, or check instance type; or antipattern because polymorphic
        self.structure = notedoc_metadata.get('NoteDocStructure')
        self.notecoll = NoteCollection(self.notedoc_id)

    def size(self):
        return self.notecoll.size()

    def add_note(self, note: Note):
        self.notecoll.add_note(note)

    def search_notes(self, search_term: str) -> list:
        match_notes = list()
        # Always case insensitive for now
        for note in self.notecoll.notes:
            search_term_parts = search_term.split('|')
            num_match = 0
            for search_term_part in search_term_parts:
                if search_term_part in note.summary_text.lower() or search_term in note.body_text.lower():
                    num_match += 1
            if num_match == len(search_term_parts):
                match_notes.append({'NoteDoc': self, 'Note': note, 'Tags': []})
        return match_notes

    def search_notes_text_tag(self, begin_date: datetime, end_date: datetime, text_tag_type_matches: list) -> list:
        match_notes = list()
        for note in self.notecoll.notes:
            if note.is_in_date_range(begin_date, end_date):
                if len(text_tag_type_matches) > 0:
                    tags = note.get_tags(text_tag_type_matches)
                    if len(tags) > 0:
                        match_notes.append({'NoteDoc': self, 'Note': note, 'Tags': tags})
                else:
                    match_notes.append({'NoteDoc': self, 'Note': note, 'Tags': []})

        return match_notes

    def is_entity_pattern_match(self, entity_matches: list) -> bool:
        # entity_match = {'EntityTypes': [entity_pattern_parts[0]], 'EntityNames': [entity_pattern_parts[1]], 'EntityAspects': [entity_aspect]}
        # notedoc_entity = f'{self.entity_type}.{self.entity_name}.{entity_aspect_abbr}'
        # pattern_match_parts = entity_pattern.split('.')

        for entity_match in entity_matches:
            entity_type_match = (len(entity_match['EntityTypes']) == 1 and entity_match['EntityTypes'][0] == '*') or self.entity_type in entity_match['EntityTypes']
            # entity_type_match = (pattern_match_parts[0] == "*") | (pattern_match_parts[0] == self.entity_type)
            entity_aspect_match = (len(entity_match['EntityAspects']) == 1 and entity_match['EntityAspects'][0] == '*') or self.entity_aspect in entity_match['EntityAspects']
            # entity_aspect_match = (pattern_match_parts[2] == "*") | (pattern_match_parts[2] == self.entity_aspect)
            #TODO: Implement regex rules for supporting * wildcard
            entity_name_match = (len(entity_match['EntityNames']) == 1 and entity_match['EntityNames'][0] == '*') or self.entity_name in entity_match['EntityNames']
            if entity_type_match & entity_name_match & entity_aspect_match:
                return True

        return False

    def render_as_text(self, fields: dict = None):
        return self.notecoll.render_as_text()

    #TODO: add remaining cases
    # @staticmethod
    # def derive_entity_aspect_abbr(entity_aspect):
    #     if entity_aspect == EntityAspect.WORK_JOURNAL:
    #         return "nwdoc"
    #     elif entity_aspect == EntityAspect.REFERENCE:
    #         return "nodoc"
    #     elif entity_aspect == EntityAspect.MEETING_JOURNAL:
    #         return "njdoc"
    #     elif entity_aspect == EntityAspect.DESIGN_JOURNAL:
    #         return "ndsdoc"
    #     elif entity_aspect == EntityAspect.TOOLBOX:
    #         return "ntlbox"
    #     else:
    #         return ''

    #TODO: add remaining cases
    @staticmethod
    def derive_entity_aspect_from_abbr(entity_aspect_abbr):
        if entity_aspect_abbr == 'nwdoc':
            return EntityAspect.WORK_JOURNAL
        elif entity_aspect_abbr == 'nodoc':
            return EntityAspect.REFERENCE
        elif entity_aspect_abbr == 'njdoc':
            return EntityAspect.MEETING_JOURNAL
        elif entity_aspect_abbr == 'ndsdoc':
            return EntityAspect.DESIGN_JOURNAL
        elif entity_aspect_abbr == 'ntlbox':
            return EntityAspect.TOOLBOX
        else:
            return ''
