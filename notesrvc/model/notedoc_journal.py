
from notesrvc.model.notedoc import NoteDocument


class NoteDocJournal(NoteDocument):

    def __init__(self, notedoc_metadata: dict):
        super().__init__(notedoc_metadata)
        self._timeline = list()

    def append_note(self, note):
        super().add_note(note)

    def render_as_dict(self):
        notes_as_dict_list = [self._render_note_as_dict(n) for n in self.notecoll.notes]
        return {"NoteDocId": self.notedoc_id, "Notes": notes_as_dict_list}

    def _render_note_as_dict(self, journal_note):
        # TODO: sort - here ?
        note_dict = journal_note.render_as_dict()
        return note_dict

