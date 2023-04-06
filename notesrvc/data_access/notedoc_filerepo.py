from datetime import datetime
import glob
import json
import os

from notesrvc.constants import EntityAspect, NoteDocStructure
import notesrvc.service.notedoc_factory as notedoc_factory
from notesrvc.service.nodedoc_parser import NoteDocParser
from notesrvc.config import Config
from notesrvc.data_access.person_repo import PersonRepo
from notesrvc.data_access.workitem_filerepo import WorkItemFileRepo
from notesrvc.constants import DATE_DASH_FORMAT

# NOTEDOC_FILE_REPO_PATH = '/Users/robertwood/Google Drive/My Drive/AncNoteDocRepo/_Ancestry'
# NOTEDOC_FILE_REPO_PATH = '/Users/robertwood/Project.ThoughtPal/AncNoteDocRepo'

config = Config()


class NoteDocFileRepo:

    def __init__(self, config: Config, person_repo: PersonRepo, workitem_repo: WorkItemFileRepo):
        self.config = config
        self.notedoc_repo_cache = dict()

        self.notedoc_parser = NoteDocParser(person_repo, workitem_repo)

        self.search_cache = dict()

        self.supported_notedoc_types = ['nwdoc', 'nodoc', 'ndsdoc']
        self.default_import_notedoc_types = ['ntlbox']

        self.active_notedoc_filenames = list()
        self.active_entity_order = dict()
        # self.manual_entity_type_map = dict()

    def initialize_active_entities(self):
        file_name = config.notedoc_active_entities_file
        with open(file_name, 'r') as active_entities_file:
            active_entities_json = active_entities_file.read()

        active_entities_dict = json.loads(active_entities_json)
        # ALERT: Don't start with 0, which evaluates to False
        loc = 1
        for grouping_entity, child_entities in active_entities_dict.items():
            self.active_entity_order[grouping_entity] = loc
            loc += 1
            for child_entity in child_entities:
                self.active_entity_order[child_entity] = loc
                loc += 1

        self._initialize_active_notedoc_filenames()

        # self.manual_entity_type_map = {
        #     'acom-oasis-api-client': 'AppDevLib',
        #     'APM_AlertRouter': 'Project',
        #     'apm-alert-router': 'AppLambda',
        #     'apm-hoodpatrol': 'AppLambda',
        #     'apm-rds-mtrc-harvest': 'App',
        #     'apm-rds-mtrc-harvest-cntr': 'AppLambda',
        #     'NewRelic': 'App',
        #     'Oasis': 'App',
        #     'RDS_MetricHarvestProcessing': 'Project',
        #     'Terraform': 'AppDevTool',
        # }

    def _initialize_active_notedoc_filenames(self):
        for entity in self.active_entity_order.keys():
            # For now, explicit rather than self.supported_notedoc_types, because each has special cases
            file_name = f'{entity}.nwdoc'
            if os.path.exists(f'{self.config.notedoc_repo_location}/{file_name}'):
                self.active_notedoc_filenames.append(file_name)
            # entity_name = entity.split('.')[1]
            # file_name = f'Design.{entity_name}.nwdoc'
            # if os.path.exists(f'{self.config.notedoc_repo_location}/{file_name}'):
            #     self.active_notedoc_filenames.append(file_name)
            file_name = f'{entity}.ndsdoc'
            if os.path.exists(f'{self.config.notedoc_repo_location}/{file_name}'):
                self.active_notedoc_filenames.append(file_name)

            file_name = f'{entity}.nodoc'
            if os.path.exists(f'{self.config.notedoc_repo_location}/{file_name}'):
                self.active_notedoc_filenames.append(file_name)
            # ALERT: No need for .ntlbox as long as all are read

            # entity_name = entity.split('.')[1]
            # file_name = f'Toolbox.{entity_name}.nodoc'
            # if os.path.exists(f"{self.config.notedoc_repo_location}/{file_name}"):
            #     self.active_notedoc_filenames.append(file_name)

    def import_active_notedocs(self):
        for file_name in self.active_notedoc_filenames:
            self.get_notedoc(file_name)

    def import_supported_notedocs(self):
        for notedoc_type in self.supported_notedoc_types:
            dir_path = f'{self.config.notedoc_repo_location}/*.{notedoc_type}'
            for file in glob.glob(dir_path, recursive=False):
                self.get_notedoc(file, is_full_path=True)

    def import_default_supported_notedocs(self):
        for notedoc_type in self.default_import_notedoc_types:
            dir_path = f'{self.config.notedoc_repo_location}/*.{notedoc_type}'
            for file in glob.glob(dir_path, recursive=False):
                file_path_parts = file.split('/')
                file_name = file_path_parts[-1]
                self.get_notedoc(file_name, is_full_path=False)

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
        notedoc_metadata['EntityName'] = file_name_parts[1]
        # if file_name_parts[0] in ['Design', 'Toolbox']:
        #     notedoc_metadata['EntityType'] = self._manually_map_entity_type(notedoc_metadata['EntityName'])
        # else:
        #     notedoc_metadata['EntityType'] = file_name_parts[0]
        notedoc_metadata['EntityType'] = file_name_parts[0]
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
    def create_status_report(self, begin_date: str, end_date: str = None) -> str:
        search_results = self.search_journal_notes(begin_date=begin_date, end_date=end_date)
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

    def create_tool_search_report(self, search_dict: dict) -> str:
        search_results = self.search_for_tool(search_term=search_dict.get('search_term'))
        report_data = list()
        report = ''
        for result in search_results:
            notedoc = result.get('NoteDoc')
            note = result.get('Note')
            tags = result.get('Tags')
            report += f'{notedoc.entity_type}.{notedoc.entity_name}\n'
            report += f'{note.summary_text}\n'
            report += f'{note.body_text}\n'
        return report

    def report_sorter(self, e):
        if not self.active_entity_order.get(e['Entity']):
            print('stop here')
        return self.active_entity_order.get(e['Entity'])

    def search_journal_notes(self, **kwargs):
        # for arg in kwargs:
        #     print(arg)
        begin_date_str = kwargs.get('begin_date')
        end_date_str = kwargs.get('end_date')
        # print(begin_date_str)
        begin_date = datetime.strptime(begin_date_str, DATE_DASH_FORMAT)
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, DATE_DASH_FORMAT)
        # print(begin_date)
        search_result = []
        for notedoc in self.notedoc_repo_cache.values():
            if notedoc.structure == NoteDocStructure.JOURNAL:
                match_notes = notedoc.search_notes_text_tag(begin_date, end_date, 'Status')
                if len(match_notes) > 0:
                    search_result.extend(match_notes)
        return search_result

    def search_for_tool(self, **kwargs):
        search_term = kwargs.get('search_term')
        # Always case insensitive for now
        search_term = search_term.lower()

        search_result = list()
        for notedoc in self.notedoc_repo_cache.values():
            if notedoc.entity_aspect == EntityAspect.TOOLBOX:
                match_notes = notedoc.search_notes(search_term)
                if len(match_notes) > 0:
                    search_result.extend(match_notes)
        return search_result

    # def _manually_map_entity_type(self, entity_name: str) -> str:
    #     entity_type = self.manual_entity_type_map.get(entity_name)
    #     if entity_type:
    #         return entity_type
    #     else:
    #         raise Exception(f'No mapping of entity_name: {entity_name} to entity_type')

    @staticmethod
    def _derive_aspect_structure(file_name_parts):
        if file_name_parts[2] == 'nodoc':
            return EntityAspect.REFERENCE, NoteDocStructure.OUTLINE
        elif file_name_parts[2] == 'ntlbox':
            return EntityAspect.TOOLBOX, NoteDocStructure.OUTLINE
        elif file_name_parts[2] == 'nwdoc':
            return EntityAspect.WORK_JOURNAL, NoteDocStructure.JOURNAL
        elif file_name_parts[2] == 'ndsdoc':
            return EntityAspect.DESIGN_JOURNAL, NoteDocStructure.JOURNAL
        elif file_name_parts[2] == 'njdoc':
            return EntityAspect.MEETING_JOURNAL, NoteDocStructure.JOURNAL
        elif file_name_parts[2] == 'nzdoc':
            return EntityAspect.SUMMARIZER, NoteDocStructure.OUTLINE
        else:
            raise Exception(f'Not supported: {file_name_parts[2]}')


if __name__ == '__main__':
    config = Config()
    notedoc_filerepo = NoteDocFileRepo(config)

    notedoc_filerepo.initialize_active_entities()

    # notedoc_filerepo.initialize_active_notedocs_tbd()

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

