
from datetime import datetime

from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.note import Note


class NoteDocJournal(NoteDocument):

    def __init__(self, notedoc_metadata: dict):
        super().__init__(notedoc_metadata)
        self._timeline = list()

    def append_note(self, note):
        super().add_note(note)

    def render_as_dict(self):
        notes_as_dict_list = [self._render_note_as_dict(n) for n in self.notecoll.notes]
        return {"NoteDocId": self.notedoc_id, "Notes": notes_as_dict_list}

    def search_notes(self, begin_date: datetime, end_date: datetime, text_tag_type: str) -> list:
        match_notes = list()
        for note in self.notecoll.notes:
            if note.is_in_date_range(begin_date, end_date):
                tags = note.get_tags(text_tag_type='Status')
                if len(tags) > 0:
                    match_notes.append({'NoteDoc': self, 'Note': note, 'Tags': tags})

        return match_notes

    def _render_note_as_dict(self, journal_note):
        # TODO: sort - here ?
        note_dict = journal_note.render_as_dict()
        return note_dict

