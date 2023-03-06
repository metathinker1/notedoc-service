

class Note(object):

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
