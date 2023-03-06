import copy

class Outline:

    def __init__(self, root_node: str):
        self.root_node = root_node
        self.location_dict = None

    def get_node(self, node_loc):
        node = self.root_node['Children'][node_loc[0]]
        if len(node_loc) > 1:
            return self._get_node_recursive(node, node_loc[1:])
        else:
            return node

    def _get_node_recursive(self, node, node_loc):
        child_node = node['Children'][node_loc[0]]
        if len(node_loc) > 1:
            return self._get_node_recursive(child_node, node_loc[1:])
        else:
            return child_node

    # TODO: Review this function: probably should deprecate now
    def append(self, note_id, parent_loc=None):
        self.location_dict = None
        if parent_loc:
            try:
                node = self.get_node(parent_loc)
                node['Children'].append({'NoteId': note_id, 'Children': []})
            except Exception as ex:
                print(f'Error: {ex}')
        else:
            self.root_node['Children'].append({'NoteId': note_id, 'Children': []})

    def get_node_location(self, note_id):
        if not self.location_dict:
            self._populate_location_dict()
        return self.location_dict[note_id]

    def _populate_location_dict(self):
        self.location_dict = {'Root': ''}
        location = [0]
        for node in self.root_node['Children']:
            self._populate_location_dict_recursive(node, copy.deepcopy(location))
            location[-1] += 1

    def _populate_location_dict_recursive(self, node, location):
        self.location_dict[node['NoteId']] = copy.deepcopy(location)
        location.append(0)
        for child_node in node['Children']:
            self._populate_location_dict_recursive(child_node, copy.deepcopy(location))
            location[-1] += 1

    def get_outline_structure(self):
        ''' ALERT: Intentionally skip Root node '''
        # ?? outline_struct = [(self.root_node['NoteId'], self.location_dict[self.root_node[0]])]
        outline_struct = []
        self._get_outline_structure_recursive(self.root_node, outline_struct)
        return outline_struct

    def _get_outline_structure_recursive(self, node, outline_struct):
        for child_node in node['Children']:
            if not child_node['NoteId']:
                print('stop here')
            outline_struct.append((child_node['NoteId'], self.get_node_location(child_node['NoteId'])))
            self._get_outline_structure_recursive(child_node, outline_struct)
