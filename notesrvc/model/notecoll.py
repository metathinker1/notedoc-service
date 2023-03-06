from notesrvc.model.note import Note


class NoteCollection:

    def __init__(self, notedoc_id: str):
        self.notedoc_id = notedoc_id
        self.notes_dict = {}
        self.notes = []

    def size(self):
        return len(self.notes)

    def add_note(self, note: Note):
        self.notes.append(note)
        self.notes_dict[note.note_id] = note

    def get_note_by_id(self, note_id):
        if note_id in self.notes_dict:
            return self.notes_dict[note_id]
        else:
            raise KeyError('note_id: {} not in NoteDocument')
