
from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.outline import Outline


class NoteDocOutline(NoteDocument):

    def __init__(self, notedoc_metadata: dict, root_node: str):
        super().__init__(notedoc_metadata)
        if not root_node:
            root_node = {'NoteId': 'Root', 'Children': []}
        self.outline = Outline(root_node)


