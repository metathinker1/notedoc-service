
from notesrvc.model.notecoll import NoteCollection
from notesrvc.model.note import Note


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

    def is_entity_pattern_match(self, entity_pattern: str) -> bool:
        entity_aspect_abbr = NoteDocument.derive_entity_aspect_abbr(self.entity_aspect)
        # notedoc_entity = f'{self.entity_type}.{self.entity_name}.{entity_aspect_abbr}'
        pattern_match_parts = entity_pattern.split('.')
        entity_type_match = (pattern_match_parts[0] == "*") | (pattern_match_parts[0] == self.entity_type)
        entity_aspect_match = (pattern_match_parts[2] == "*") | (pattern_match_parts[2] == entity_aspect_abbr)
        #TODO: Implement regex rules for supporting * wildcard
        entity_name_match = pattern_match_parts[1] == self.entity_name
        return entity_type_match & entity_name_match & entity_aspect_match

    def render_as_text(self, fields: dict = None):
        return self.notecoll.render_as_text()

    #TODO: add remaining cases
    @staticmethod
    def derive_entity_aspect_abbr(entity_aspect_arg):
        if entity_aspect_arg == 'Toolbox':
            return "ntlbox"
        else:
            return "nwdoc"
