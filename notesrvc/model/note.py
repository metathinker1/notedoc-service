
from datetime import datetime

from notesrvc.constants import DATE_TIME_FORMAT


class Note:

    def __init__(self, note_id: str = None):
        self.note_id = note_id
        self.summary_text = None
        self.body_text = None
        self.tags = []

    def render_as_dict(self):
        note_as_dict = {"Id": self.note_id, "Summary": self.summary_text, "Body": self.body_text}
        if len(self.tags) > 0:
            note_as_dict['Tags'] = self.render_tag_as_array_of_strings()
        return note_as_dict


class JournalNote(Note):

    def __init__(self, note_id: str = None, date_stamp: datetime = None):
        super().__init__(note_id)
        self.date_stamp = date_stamp

    def render_as_dict(self):
        date_stamp_str = self.date_stamp.strftime(DATE_TIME_FORMAT)
        note_as_dict = {"DateStamp": date_stamp_str, "Summary": self.summary_text, "Body": self.body_text, "DateStamp": self.date_stamp}
        if len(self.tags) > 0:
            note_as_dict['Tags'] = self.render_tag_as_array_of_strings()
        return note_as_dict
