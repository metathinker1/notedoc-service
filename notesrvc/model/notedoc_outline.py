
from notesrvc.model.notedoc import NoteDocument
from notesrvc.model.outline import Outline


class NoteDocOutline(NoteDocument):

    def __init__(self, notedoc_metadata: dict, root_node: str):
        super().__init__(notedoc_metadata)
        if not root_node:
            root_node = {'NoteId': 'Root', 'Children': []}
        self.outline = Outline(root_node)

    def append_note(self, note, parent_loc=None):
        super().add_note(note)
        self.outline.append(note.note_id, parent_loc)

    def render_as_dict(self, fields: dict = None):
        outline_struct = self.outline.get_outline_structure()
        notes_as_dict_list = [self._render_note_as_dict(i, fields) for i in outline_struct]
        return {"NoteDocId": self.notedoc_id, "Notes": notes_as_dict_list}

    def render_as_search_dict(self):
        outline_struct = self.outline.get_outline_structure()
        notes_as_dict_list = [self._render_note_as_search_dict(i) for i in outline_struct]
        return {"NoteDocId": self.notedoc_id, "Notes": notes_as_dict_list}

    def _render_note_as_dict(self, outline_struct_node, fields: dict = None):
        note = self.notecoll.get_note_by_id(outline_struct_node[0])
        note_dict = note.render_as_dict(fields)
        note_dict['Label'] = self._calc_note_label(outline_struct_node[1])
        return note_dict

    def _render_note_as_search_dict(self, outline_struct_node):
        note = self.notecoll.get_note_by_id(outline_struct_node[0])
        note_dict = note.render_as_search_dict()
        note_dict['Label'] = self._calc_note_label(outline_struct_node[1])
        return note_dict

    def _calc_note_label(self, outline_location):
        return '.'.join([str(i + 1) for i in outline_location])

