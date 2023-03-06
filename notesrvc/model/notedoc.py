
from notesrvc.model.notecoll import NoteCollection


class NoteDocument:

    def __init__(self, notedoc_metadata: dict):
        self.notedoc_id = notedoc_metadata.get('NoteDocId')
        self.entity_type = notedoc_metadata.get('EntityType')
        self.entity_name = notedoc_metadata.get('EntityName')
        self.aspect = notedoc_metadata.get('EntityAspect')
        # TODO: Research: best practice: field with type, or check instance type; or antipattern because polymorphic
        self.structure = notedoc_metadata.get('NoteDocStructure')
        self.notecoll = NoteCollection(self.notedoc_id)

    def size(self):
        return self.notecoll.size()
