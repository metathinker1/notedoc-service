
from datetime import datetime

from notesrvc.constants import DATE_TIME_FORMAT, DATE_FORMAT


class Note:

    def __init__(self, note_id: str = None):
        self.note_id = note_id
        # TODO: Consider moving summary_text to OutlineNote
        self.summary_text = ''
        self.body_text = ''
        self.tags = []

        self.standard_note_fields = ['Id', 'Summary', 'Body']
        self.default_fields = {'Fields': self.standard_note_fields, 'Tags': ['ALL']}
        # 2025.01.29: Add 'Body': optional, and controlled by expand_list
        #   ASSUME: only used for Outlines
        self.search_fields = {'Fields': ['Summary', 'Body']}

    def is_in_date_range(self, begin_date_range: datetime = None, end_date_range: datetime = None) -> bool:
        # Only JournalNote supports
        # return False
        # 2025.01.31: Only JournalNote supports date_stamp; others should return True instead - effectively no filter
        return True

    def get_tags(self, text_tag_type_matches: list):
        return_tags = list()
        for tag in self.tags:
            if tag.is_tag_text_type_in(text_tag_type_matches):
                return_tags.append(tag)
        return return_tags

    def render_as_dict(self, fields: dict = None):
        if not fields:
            fields = self.default_fields

        note_as_dict = dict()

        # switch to match / case with Python 3.10
        for field in fields['Fields']:
            if field == 'Id':
                note_as_dict['Id'] = self.note_id
            elif field == 'Summary':
                note_as_dict['Summary'] = self.summary_text
            elif field == 'Body':
                note_as_dict['Body'] = self.body_text
            else:
                pass

        # TODO: Add more fine grained selection ability
        if 'Tags' in fields and len(self.tags) > 0:
            note_as_dict['Tags'] = self.render_tag_as_array_of_strings()
        return note_as_dict

    def render_as_search_dict(self):
        return self.render_as_dict(fields=self.search_fields)

    # TODO: Consider: moving to Tag
    def render_tag_as_array_of_strings(self):
        try:
            result = [tag.headline_text for tag in self.tags]
            return result
        except Exception as ex:
            print('stop here')
            return ''

    def render_note_as_html_snippet(self):
        body_text_as_html = self.body_text.replace('\n', '<br>')
        return f'{self.summary_text}<br>{body_text_as_html}'


# TODO: NoteDocOutline requires outline_location -- has to be done in that class
#   So this base class would never be called ...
#   OR: OutlineNote where outline_location is only in-memory ??

class JournalNote(Note):

    def __init__(self, note_id: str = None, date_stamp: datetime = None):
        super().__init__(note_id)
        self.date_stamp = date_stamp
        self.date_stamp_str = self.date_stamp.strftime(DATE_TIME_FORMAT)
        self.date_str = self.date_stamp.strftime(DATE_FORMAT)

        self.standard_note_fields = ['Id', 'DateStamp', 'Summary', 'Body']
        self.default_fields = {'Fields': self.standard_note_fields, 'Tags': ['ALL']}
        self.search_fields = {'Fields': ['Date', 'Summary']}

    def is_in_date_range(self, begin_date_range: datetime = None, end_date_range: datetime = None) -> bool:
        if not self.date_stamp:
            # 2025.01.31: should return True instead - effectively no filter
            # return False
            return True

        if begin_date_range and end_date_range:
            return self.date_stamp >= begin_date_range and self.date_stamp <= end_date_range
        elif begin_date_range:
            return self.date_stamp >= begin_date_range
        elif end_date_range:
            return self.date_stamp <= end_date_range
        else:
            return False

    def render_as_dict(self, fields: dict = None):
        if not fields:
            fields = self.default_fields

        note_as_dict = dict()

        # switch to match / case with Python 3.10
        for field in fields['Fields']:
            if field == 'Id':
                note_as_dict['Id'] = self.note_id
            elif field == 'DateStamp':
                note_as_dict['DateStamp'] = self.date_stamp_str
            elif field == 'Date':
                note_as_dict['Date'] = self.date_str
            elif field == 'Summary':
                note_as_dict['Summary'] = self.summary_text
            elif field == 'Body':
                note_as_dict['Body'] = self.body_text
            else:
                pass

        # TODO: Add more fine grained selection ability
        if 'Tags' in fields and len(self.tags) > 0:
            note_as_dict['Tags'] = self.render_tag_as_array_of_strings()
        return note_as_dict
