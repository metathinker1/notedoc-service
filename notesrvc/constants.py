

class NoteDocStructure:
    OUTLINE = 'Outline'
    JOURNAL = 'Journal'


class EntityAspect:
    REFERENCE = 'Reference'
    TOOLBOX = 'Toolbox'
    WORK_JOURNAL = 'WorkJournal'
    MEETING_JOURNAL = 'MeetingJournal'
    DESIGN_JOURNAL = 'DesignJournal'
    SUMMARIZER = 'Summarizer'


BEGIN_NOTE_PATTERN = '<Note [0-9]*>'
BEGIN_JOURNAL_NOTE_PATTERN = r'<\d{4}.\d{2}.\d{2}[ ]\d{2}:\d{2}>'
BEGIN_TEXT_TAG = '{TextTag:'
END_MULTILINE_TAG = '}\\'
END_SINGLELINE_TAG = '}'

BEGIN_WORKITEMS_SECTION = '{WorkItems:'
END_WORKITEMS_SECTION = '}\\'
BEGIN_WORKITEM = '=>'

DATE_TIME_FORMAT = '%Y.%m.%d %H:%M'
DATE_FORMAT = '%Y.%m.%d'
DATE_DASH_FORMAT = '%Y-%m-%d'
MONTH_DAY_DATE_FORMAT = '%m-%d'

import re

if __name__ == '__main__':
    outline01 = '<Note 1>'
    check01 = re.search(BEGIN_NOTE_PATTERN, outline01)
    print(check01)

    date01 = '2023.03.10 09:15'
    check02 = re.search(BEGIN_JOURNAL_NOTE_PATTERN, date01)
    print(check02)