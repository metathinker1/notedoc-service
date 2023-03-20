from datetime import datetime

from notesrvc.constants import EntityAspect, NoteDocStructure
import notesrvc.service.notedoc_factory as notedoc_factory
from notesrvc.service.nodedoc_parser import NoteDocParser
from notesrvc.config import Config
from notesrvc.constants import DATE_DASH_FORMAT

# NOTEDOC_FILE_REPO_PATH = '/Users/robertwood/Google Drive/My Drive/AncNoteDocRepo/_Ancestry'


class NoteDocFileRepo:

    def __init__(self, config: Config):
        self.config = config
        self.notedoc_repo_cache = dict()
        self.notedoc_parser = NoteDocParser()

        self.search_cache = dict()

    def initialize_active_notedocs(self):
        self.active_notedoc_filenames = [
        'Project.RDS_MetricHarvestProcessing.nwdoc',
        'Design.RDS_MetricHarvestProcessing.nwdoc',
        'AppLambda.apm-rds-mtrc-harvest-cntr.nwdoc',
        'Design.apm-rds-mtrc-harvest-cntr.nwdoc',
        'Project.APM_AlertRouter.nwdoc',
        'Design.APM_AlertRouter.nwdoc',
        'AppLambda.apm-alert-router.nwdoc',
        'Design.apm-alert-router.nwdoc',
        'AppLambda.apm-hoodpatrol.nwdoc'
        ]

    def import_active_notedocs(self):
        for file_name in self.active_notedoc_filenames:
            self.get_notedoc(file_name)

    def get_notedoc(self, file_name: str):
        if file_name in self.notedoc_repo_cache:
            return self.notedoc_repo_cache.get(file_name)

        file_path = f'{self.config.notedoc_repo_location}/{file_name}'
        with open(file_path, 'rt', encoding='utf-8') as file:
            notedoc_text = file.read()

        # TODO: Consider: use class instead
        notedoc_metadata = dict()
        notedoc_metadata['NoteDocId'] = file_name
        file_name_parts = file_name.split('.')
        # TODO: Consider: Entity class
        notedoc_metadata['EntityType'] = file_name_parts[0]
        notedoc_metadata['EntityName'] = file_name_parts[1]
        notedoc_metadata['EntityAspect'], notedoc_metadata['NoteDocStructure'] = \
            NoteDocFileRepo._derive_aspect_structure(file_name_parts)

        notedoc = notedoc_factory.create_notedoc(notedoc_metadata)

        # TODO: do parsing
        self.notedoc_parser.parse_text(notedoc_text, notedoc)

        self.notedoc_repo_cache[file_name] = notedoc

        # notedoc_search_dict = notedoc.render_as_search_dict()
        # self.search_cache

        return notedoc

    def create_status_report(self, begin_date: datetime):
        search_results = self.search_notes(begin_date=begin_date)
        print(f'search_results: {search_results}')
        report = ''
        
        # TODO: suppress repeat Entity, Journal Date headings in report
        last_notedoc_id = None
        last_date_stamp = None
        for result in search_results:
            notedoc = result.get('NoteDoc')
            note = result.get('Note')
            tags = result.get('Tags')
            date_stamp = note.date_str
            report += f'\n{notedoc.entity_type} {notedoc.entity_name}\n'
            report += f'\n{date_stamp}\n'
            for tag in tags:
                report += f'{tag.headline_text}\n'
            report += f'\n\n'
        return report

    def search_notes(self, **kwargs):
        for arg in kwargs:
            print(arg)
        date_str = kwargs.get('begin_date')
        print(date_str)
        begin_date = datetime.strptime(date_str, DATE_DASH_FORMAT)
        print(begin_date)
        search_result = []
        for notedoc in self.notedoc_repo_cache.values():
            if notedoc.entity_aspect == EntityAspect.WORK_JOURNAL:
                match_notes = notedoc.search_notes(begin_date, 'Status')
                if len(match_notes) > 0:
                    search_result.extend(match_notes)
        return search_result

    @staticmethod
    def _derive_aspect_structure(file_name_parts):
        if file_name_parts[2] == 'nodoc':
            if file_name_parts[0] == 'Toolbox':
                return EntityAspect.TOOLBOX, NoteDocStructure.OUTLINE
            else:
                return EntityAspect.REFERENCE, NoteDocStructure.OUTLINE
        elif file_name_parts[2] == 'nwdoc':
            return EntityAspect.WORK_JOURNAL, NoteDocStructure.JOURNAL
        elif file_name_parts[2] == 'njdoc':
            return EntityAspect.MEETING_JOURNAL, NoteDocStructure.JOURNAL
        elif file_name_parts[2] == 'nzdoc':
            return EntityAspect.SUMMARIZER, NoteDocStructure.OUTLINE
        else:
            raise Exception(f'Not supported: {file_name_parts[2]}')


if __name__ == '__main__':
    config = Config()
    notedoc_filerepo = NoteDocFileRepo(config)

    notedoc_filerepo.initialize_active_notedocs()
    notedoc_filerepo.import_active_notedocs()

    report = notedoc_filerepo.create_status_report('2023-02-17')
    print(f'search_results: {report}')

    # file_name = 'Project.APM_AlertRouter.nodoc'
    file_name = 'Project.APMGovernanceTool.nodoc'
    notedoc = notedoc_filerepo.get_notedoc(file_name)
    notedoc_dict = notedoc.render_as_dict()
    print(f'notedoc_dict: {notedoc_dict}')
    notedoc_search_dict = notedoc.render_as_search_dict()
    print(f'notedoc_search_dict: {notedoc_search_dict}')

    notedoc_outline_text = notedoc.render_as_outline_text()
    print(f'notedoc_outline_text: {notedoc_outline_text}')

    file_name = 'Project.APMGovernanceTool.nwdoc'
    notedoc = notedoc_filerepo.get_notedoc(file_name)
    notedoc_dict = notedoc.render_as_dict()
    print(f'notedoc_dict: {notedoc_dict}')

