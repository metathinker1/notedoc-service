
class Tag:

    def __init__(self, tag_id: str = None):
        self.tag_id = tag_id

    def is_tag_text_type(self, tag_text_type: str) -> bool:
        return False

    def is_tag_text_type_in(self, tag_text_types: list):
        return False


class TextTag(Tag):

    def __init__(self, tag_id: str = None):
        super().__init__(tag_id)
        self.headline_text = None
        self.body_text = None
        self.text_tag_type = None

    def is_tag_text_type(self, tag_text_type: str) -> bool:
        return self.text_tag_type == tag_text_type

    def is_tag_text_type_in(self, tag_text_types: list):
        return self.text_tag_type in tag_text_types
