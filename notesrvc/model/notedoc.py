
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

    def render_as_text(self, fields: dict = None):
        return self.notecoll.render_as_text()
