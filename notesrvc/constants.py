

class NoteDocStructure:
    OUTLINE = 'Outline'
    JOURNAL = 'Journal'


# TODO: Refactor as enum
class EntityAspect:
    REFERENCE = 'Reference'
    TOOLBOX = 'Toolbox'
    WORK_JOURNAL = 'WorkJournal'
    MEETING_JOURNAL = 'MeetingJournal'
    DESIGN_JOURNAL = 'DesignJournal'
    SUMMARIZER = 'Summarizer'
    LEARNING_JOURNAL = 'LearningJournal'
    TRAINING_JOURNAL = 'TrainingJournal'
    SERVICE_FLOWS = 'ServiceFlows'
    SUPPORT_REFERENCE = 'SupportReference'
    SUPPORT_JOURNAL = 'SupportJournal'

    JOURNAL_ASPECTS = [MEETING_JOURNAL, WORK_JOURNAL, DESIGN_JOURNAL, SUPPORT_JOURNAL, LEARNING_JOURNAL, TRAINING_JOURNAL]
    REFERENCE_ASPECTS = [REFERENCE, TOOLBOX, SUPPORT_REFERENCE, SERVICE_FLOWS, SUMMARIZER]

    # TODO: Confirm not required;  Or maybe use for abbreviations; Or simple validation
    @staticmethod
    def map_from(entity_aspect: str):
        if entity_aspect == 'Reference':
            return EntityAspect.REFERENCE
        elif entity_aspect == 'Toolbox':
            return EntityAspect.TOOLBOX
        elif entity_aspect == 'WorkJournal':
            return EntityAspect.WORK_JOURNAL
        elif entity_aspect == 'MeetingJournal':
            return EntityAspect.MEETING_JOURNAL
        elif entity_aspect == 'DesignJournal':
            return EntityAspect.DESIGN_JOURNAL
        elif entity_aspect == 'Summarizer':
            return EntityAspect.SUMMARIZER
        elif entity_aspect == 'LearningJournal':
            return EntityAspect.LEARNING_JOURNAL
        elif entity_aspect == 'TrainingJournal':
            return EntityAspect.TRAINING_JOURNAL
        elif entity_aspect == 'ServiceFlows':
            return EntityAspect.SERVICE_FLOWS
        elif entity_aspect == 'SupportReference':
            return EntityAspect.SUPPORT_REFERENCE
        elif entity_aspect == 'SupportJournal':
            return EntityAspect.SUPPORT_JOURNAL

        else:
            raise Exception(f'Not supported: {entity_aspect}')


BEGIN_NOTE_PATTERN = '<Note [0-9]*>'
BEGIN_JOURNAL_NOTE_PATTERN = r'<\d{4}.\d{2}.\d{2}[ ]\d{2}:\d{2}>'
BEGIN_TEXT_TAG = '{TextTag:'
END_MULTILINE_TAG = '}\\'
END_MULTILINE_TAG_REGEX = '}\\\\'
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