from datetime import datetime
import glob

from notesrvc.constants import EntityAspect, NoteDocStructure
import notesrvc.service.notedoc_factory as notedoc_factory
from notesrvc.service.nodedoc_parser import NoteDocParser
from notesrvc.config import Config
from notesrvc.constants import DATE_DASH_FORMAT

# NOTEDOC_FILE_REPO_PATH = '/Users/robertwood/Google Drive/My Drive/AncNoteDocRepo/_Ancestry'
# NOTEDOC_FILE_REPO_PATH = '/Users/robertwood/Project.ThoughtPal/AncNoteDocRepo'

class NoteDocFileRepo:

    def __init__(self, config: Config):
        self.config = config
        self.notedoc_repo_cache = dict()
        self.notedoc_parser = NoteDocParser()

        self.search_cache = dict()

        self.supported_notedoc_types = ['nwdoc', 'nodoc']

        self.active_notedoc_filenames = list()
        self.active_entity_order = dict()

    def initialize_active_notedocs(self):
        self.active_notedoc_filenames.extend([
            'Project.ZabbixMonitoringMigration.nwdoc',

            'Project.APM_AlertRouter.nwdoc',
            'Design.APM_AlertRouter.nwdoc',
            'AppLambda.apm-alert-router.nwdoc',
            'Design.apm-alert-router.nwdoc',
            'AppDevLib.acom-oasis-api-client.nwdoc',

            'Project.RDS_MetricHarvestProcessing.nwdoc',
            'Design.RDS_MetricHarvestProcessing.nwdoc',
            'AppLambda.apm-rds-mtrc-harvest-cntr.nwdoc',

            'App.Oasis',
            'AppDevLib.acom-oasis-api-client',

            'AppLambda.apm-hoodpatrol.nwdoc',

            'AppDevTool.Terraform.nwdoc'
        ])

#            'AppLambda.apm-rds-mtrc-harvest.nwdoc',
#            'Design.apm-rds-mtrc-harvest-cntr.nwdoc',
#            'Design.apm-rds-mtrc-harvest.nwdoc',

        active_entities = [
            'Project.ZabbixMonitoringMigration',

            'Project.APM_AlertRouter',
            'AppLambda.apm-alert-router',
            'AppDevLib.acom-oasis-api-client',

            'Project.RDS_MetricHarvestProcessing',
            'AppLambda.apm-rds-mtrc-harvest-cntr',
            'AppLambda.apm-rds-mtrc-harvest',

            'AppLambda.apm-hoodpatrol',

            'AppDevTool.Terraform'
        ]

        loc = 0
        for entity in active_entities:
            self.active_entity_order[entity] = loc
            loc += 1

    def import_active_notedocs(self):
        for file_name in self.active_notedoc_filenames:
            self.get_notedoc(file_name)

    def import_supported_notedocs(self):
        for notedoc_type in self.supported_notedoc_types:
            dir_path = f'{self.config.notedoc_repo_location}/*.{notedoc_type}'
            for file in glob.glob(dir_path, recursive=False):
                self.get_notedoc(file, is_full_path=True)

    # TECH_DEBT: replace is_full_path
    def get_notedoc(self, file_name: str, is_full_path: bool = False):
        if file_name in self.notedoc_repo_cache:
            return self.notedoc_repo_cache.get(file_name)

        if is_full_path:
            file_path = file_name
        else:
            file_path = f'{self.config.notedoc_repo_location}/{file_name}'
        with open(file_path, 'rt', encoding='utf-8') as file:
            notedoc_text = file.read()

        print(f'Parsing file_name: {file_name}')
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

    # TODO: Add sort: https://www.w3schools.com/python/ref_list_sort.asp
    # Entity: entity_type & entity_name: specific ordering; then alphabetical
    # NoteJournal.date_stamp
    def create_status_report(self, begin_date: datetime):
        search_results = self.search_notes(begin_date=begin_date)
        print(f'search_results: {search_results}')
        report_data = list()
        report = ''

        # TODO: suppress repeat Entity, Journal Date headings in report
        last_notedoc_id = None
        last_date_stamp = None
        for result in search_results:
            notedoc = result.get('NoteDoc')
            note = result.get('Note')
            tags = result.get('Tags')
            date_stamp = note.date_str
            for tag in tags:
                report_entry = {
                    'Entity': f'{notedoc.entity_type}.{notedoc.entity_name}',
                    'EntityType': notedoc.entity_type,
                    'EntityName': notedoc.entity_name,
                    'EntityAspect': notedoc.entity_aspect,
                    'DateStamp': date_stamp,
                    'TagHeadline': tag.headline_text,
                    'TagBody': tag.body_text
                }
                report_data.append(report_entry)

        report_data.sort(key=self.report_sorter)
        for report_entry in report_data:
            report += f"\n{report_entry['EntityType']} {report_entry['EntityName']}\n"
            report += f"\n{report_entry['DateStamp']}\n"
            report += f"{report_entry['TagHeadline']}\n"
            report += f"{report_entry['TagBody']}\n"
            report += f"\n\n"
        return report

    def report_sorter(self, e):
        return self.active_entity_order.get(e['Entity'])

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
    # notedoc_filerepo.import_supported_notedocs()

    report = notedoc_filerepo.create_status_report('2023-02-17')
    print(f'Status Report:\n{report}')

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

