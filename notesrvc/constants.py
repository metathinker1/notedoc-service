

class NoteDocStructure:
    OUTLINE = 'Outline'
    JOURNAL = 'Journal'


class NoteDocAspect:
    REFERENCE = 'Reference'
    TOOLBOX = 'Toolbox'
    WORK_JOURNAL = 'WorkJournal'
    MEETING_JOURNAL = 'MeetingJournal'
    SUMMARIZER = 'Summarizer'


BEGIN_NOTE_PATTERN = '<Note [0-9]*>'
BEGIN_JOURNAL_NOTE_PATTERN = r'<\d{4}.\d{2}.\d{2}[ ]\d{2}:\d{2}>'
BEGIN_TEXT_TAG = '{TextTag:'

DATE_TIME_FORMAT = '%Y.%m.%d %H:%M'


import re

if __name__ == '__main__':
    outline01 = '<Note 1>'
    check01 = re.search(BEGIN_NOTE_PATTERN, outline01)
    print(check01)

    date01 = '2023.03.10 09:15'
    check02 = re.search(BEGIN_JOURNAL_NOTE_PATTERN, date01)
    print(check02)