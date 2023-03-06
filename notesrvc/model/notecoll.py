import json


class NoteCollection:

    def __init__(self, notedoc_id: str):
        self.notedoc_id = notedoc_id
        self.notes_dict = {}
        self.notes = []

    def size(self):
        return len(self.notes)
