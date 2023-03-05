

class Note(object):

    def __init__(self, note_id: str):
        self.note_id = note_id
        self.summary_text = None
        self.body_text = None
        self.tags = []
