
from notesrvc.model.notedoc_outline import NoteDocOutline
from notesrvc.model.notedoc_journal import NoteDocJournal
from notesrvc.constants import NoteDocStructure


def create_notedoc(notedoc_metadata: dict):
    if notedoc_metadata['NoteDocStructure'] == NoteDocStructure.OUTLINE:
        return NoteDocOutline(notedoc_metadata, None)
    elif notedoc_metadata['NoteDocStructure'] == NoteDocStructure.JOURNAL:
        return NoteDocJournal(notedoc_metadata)
    else:
        error_message = f'Unsupported NoteDoc structure'
        raise Exception(error_message)
