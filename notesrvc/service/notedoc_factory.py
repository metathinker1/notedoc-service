
from notesrvc.model.notedoc_outline import NoteDocOutline
from notesrvc.constants import NoteDocStructure


def create_notedoc(notedoc_metadata: dict):
    if notedoc_metadata['NoteDocStructure'] == NoteDocStructure.OUTLINE:
        notedoc = NoteDocOutline(notedoc_metadata, None)
        return notedoc

