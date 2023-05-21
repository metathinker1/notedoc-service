from datetime import datetime
import glob
import json
import os

from notesrvc.model.entity import Entity
from notesrvc.model.notedoc import NoteDocument
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
        self.workitem_repo = workitem_repo

        self.notedoc_parser = NoteDocParser(person_repo, workitem_repo)

        self.search_cache = dict()

        self.supported_notedoc_types = ['nwdoc', 'nodoc', 'ndsdoc']
        self.default_import_notedoc_types = ['ntlbox', 'nwdoc', 'njdoc']

        self.active_notedoc_filenames = list()
        self.active_entity_order = dict()
        self.active_entity_child_entities = dict()
        self.num_active_entities = 0
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
            self.active_entity_child_entities[grouping_entity] = child_entities.copy()
            for child_entity in child_entities:
                self.active_entity_order[child_entity] = loc
                loc += 1
        self.num_active_entities = loc

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

    def get_notedoc_entity(self, entity: Entity, aspect: EntityAspect):
        filename = NoteDocFileRepo._derive_file_name(entity, aspect)
        return self.get_notedoc(filename)

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
    def create_status_report(self, begin_date_str: str, end_date_str: str = None, entity: str = None,
                             incl_entity_children: bool = False, incl_work_items: bool = False,
                             response_format: str = 'text') -> str:
        search_results = self.search_journal_notes(begin_date=begin_date_str, end_date=end_date_str, entity=entity, incl_entity_children=incl_entity_children)
        begin_date = datetime.strptime(begin_date_str, DATE_DASH_FORMAT)
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, DATE_DASH_FORMAT)
        active_workitems = self.workitem_repo.get_active_workitems()

        recent_done_workitems = self.workitem_repo.get_done_workitems(begin_date, end_date)

        print(f'search_results: {search_results}')
        report_data = list()

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
                    'Date': date_stamp,
                    'TagHeadline': tag.headline_text,
                    'TagBody': tag.body_text
                }
                report_data.append(report_entry)

        report_data.sort(key=self.report_sorter)

        active_workitems_report_data = list()
        if incl_work_items:
            for workitem in active_workitems:
                report_entry = {
                    'Entity': f'{workitem.entity.entity_type}.{workitem.entity.entity_name}',
                    'EntityType': workitem.entity.entity_type,
                    'EntityName': workitem.entity.entity_name,
                    'Person': workitem.person.abbr,
                    'Date': workitem.date_defined_str,
                    'Summary': workitem.summary_text,
                }
                active_workitems_report_data.append(report_entry)
            active_workitems_report_data.sort(key=self.report_sorter)

        done_workitems_report_data = list()
        if incl_work_items:
            for workitem in recent_done_workitems:
                report_entry = {
                    'Entity': f'{workitem.entity.entity_type}.{workitem.entity.entity_name}',
                    'EntityType': workitem.entity.entity_type,
                    'EntityName': workitem.entity.entity_name,
                    'Person': workitem.person.abbr,
                    'Date': workitem.date_defined_str,
                    'Summary': workitem.summary_text,
                }
                done_workitems_report_data.append(report_entry)
            done_workitems_report_data.sort(key=self.report_sorter)

        if response_format == 'text':
            return NoteDocFileRepo._build_report(report_data, active_workitems_report_data, done_workitems_report_data, response_format)
        else:
            return NoteDocFileRepo._build_report(report_data, active_workitems_report_data, done_workitems_report_data, response_format)
            # return NoteDocFileRepo._build_report_as_html(report_data, active_workitems_report_data, done_workitems_report_data)

    @staticmethod
    def _build_report(report_data: list, active_workitems_report_data: list, done_workitems_report_data: list, response_format: str):
        if response_format == 'text':
            lb = '\n'
            le = '\n'
        else:
            lb = '<p>'
            le = '</p>'
        num_chars_section_break = 50
        report = ''
        unique_entity, unique_date = NoteDocFileRepo._derive_unique_entity_date_or_none(report_data)
        if unique_entity:
            section_entity_header = f"{unique_entity}"
            dashes = '-'*(num_chars_section_break - len(section_entity_header))
            report += f"{lb}--| {section_entity_header} |{dashes}{le}"
        if unique_date:
            date_section_header = f"{unique_date}"
            dashes = '-' * (num_chars_section_break - len(date_section_header))
            report += f"{lb}--| {date_section_header} |{dashes}{le}"

        prev_entity_section_header = None
        prev_date_section_header = None
        for report_entry in report_data:
            if not unique_entity:
                section_entity_header = f"{report_entry['EntityType']} {report_entry['EntityName']}"
                dashes = '-'*(num_chars_section_break - len(section_entity_header))
                if prev_entity_section_header:
                    if prev_entity_section_header != section_entity_header:
                        report += f"{lb}{le}"
                        report += f"{lb}--| {section_entity_header} |{dashes}{le}"
                else:
                    report += f"{lb}--| {section_entity_header} |{dashes}{le}"
            if not unique_date:
                date_section_header = f"{report_entry['Date']}"
                dashes = '-' * (num_chars_section_break - len(date_section_header) - 2)
                if prev_date_section_header:
                    if prev_date_section_header != date_section_header:
                        report += f"{lb}----| {date_section_header} |{dashes}{le}"
                else:
                    report += f"{lb}----| {date_section_header} |{dashes}{le}"
            if 'TagHeadline' in report_entry:
                report += f"{report_entry['TagHeadline']}{le}"
            if 'TagBody' in report_entry:
                report += f"{report_entry['TagBody']}{le}"
            report += f"{lb}{le}"
            if not prev_entity_section_header:
                prev_entity_section_header = section_entity_header
                prev_date_section_header = date_section_header
            elif prev_entity_section_header == section_entity_header:
                prev_date_section_header = date_section_header
            else:
                prev_entity_section_header = section_entity_header
                prev_date_section_header = None


        if len(active_workitems_report_data) > 0:
            section_entity_header = 'Active WorkItems'
            dashes = '='*(num_chars_section_break - len(section_entity_header))
            report += f"{lb}{section_entity_header} |{dashes}{le}"
            for report_entry in active_workitems_report_data:
                report += f"{lb}{report_entry['EntityType']} {report_entry['EntityName']}{le}"
                report += f"{lb}{report_entry['Date']}{le}"
                report += f"{lb}{report_entry['Person']}: {report_entry['Summary']}{le}"
            report += f"{lb}{le}"

        if len(done_workitems_report_data):
            section_entity_header = 'Done WorkItems'
            dashes = '='*(num_chars_section_break - len(section_entity_header))
            report += f"{lb}{section_entity_header} |{dashes}{le}"
            for report_entry in done_workitems_report_data:
                report += f"{lb}{report_entry['EntityType']} {report_entry['EntityName']}{le}"
                report += f"{lb}{report_entry['Date']}{le}"
                report += f"{lb}{report_entry['Person']}: {report_entry['Summary']}{le}"
            report += f"{lb}{le}"

        return report

    @staticmethod
    def _build_report_as_text(report_data: list, active_workitems_report_data: list, done_workitems_report_data: list):
        num_chars_section_break = 50
        report = ''
        unique_entity, unique_date = NoteDocFileRepo._derive_unique_entity_date_or_none(report_data)
        if unique_entity:
            section_entity_header = f"{unique_entity}"
            dashes = '-'*(num_chars_section_break - len(section_entity_header))
            report += f"\n--| {section_entity_header} |{dashes}\n"
        if unique_date:
            date_section_header = f"{unique_date}"
            dashes = '-' * (num_chars_section_break - len(date_section_header))
            report += f"\n--| {date_section_header} |{dashes}\n"

        prev_entity_section_header = None
        prev_date_section_header = None
        for report_entry in report_data:
            if not unique_entity:
                section_entity_header = f"{report_entry['EntityType']} {report_entry['EntityName']}"
                dashes = '-'*(num_chars_section_break - len(section_entity_header))
                if prev_entity_section_header:
                    if prev_entity_section_header != section_entity_header:
                        report += f"\n--| {section_entity_header} |{dashes}\n"
                else:
                    report += f"\n--| {section_entity_header} |{dashes}\n"
            if not unique_date:
                date_section_header = f"{report_entry['Date']}"
                dashes = '-' * (num_chars_section_break - len(date_section_header))
                if prev_date_section_header:
                    if prev_date_section_header != date_section_header:
                        report += f"\n--| {date_section_header} |{dashes}\n"
                else:
                    report += f"\n--| {date_section_header} |{dashes}\n"
            if 'TagHeadline' in report_entry:
                report += f"{report_entry['TagHeadline']}\n"
            if 'TagBody' in report_entry:
                report += f"{report_entry['TagBody']}\n"
            report += f"\n\n"
            prev_entity_section_header = section_entity_header

        if len(active_workitems_report_data) > 0:
            section_entity_header = 'Active WorkItems'
            dashes = '='*(num_chars_section_break - len(section_entity_header))
            report += f"\n{section_entity_header} |{dashes}\n"
            for report_entry in active_workitems_report_data:
                report += f"\n{report_entry['EntityType']} {report_entry['EntityName']}\n"
                report += f"\n{report_entry['Date']}\n"
                report += f"\n{report_entry['Person']}: {report_entry['Summary']}\n"
            report += f"\n\n"

        if len(done_workitems_report_data):
            section_entity_header = 'Done WorkItems'
            dashes = '='*(num_chars_section_break - len(section_entity_header))
            report += f"\n{section_entity_header} |{dashes}\n"
            for report_entry in done_workitems_report_data:
                report += f"\n{report_entry['EntityType']} {report_entry['EntityName']}\n"
                report += f"\n{report_entry['Date']}\n"
                report += f"\n{report_entry['Person']}: {report_entry['Summary']}\n"
            report += f"\n\n"

        return report

    @staticmethod
    def _derive_unique_entity_date_or_none(report_data: list):
        entities = [f"{e['EntityType']} {e['EntityName']}" for e in report_data]
        unique_entities = set(entities)
        unique_entity = unique_entities.pop() if len(unique_entities) == 1 else None
        dates = [e['Date'] for e in report_data]
        unique_dates = set(dates)
        unique_date = unique_dates.pop() if len(unique_dates) == 1 else None
        return unique_entity, unique_date

    @staticmethod
    def _build_report_as_html(report_data: list, active_workitems_report_data: list, done_workitems_report_data: list):
        report = ''
        for report_entry in report_data:
            report += f"<p>{report_entry['EntityType']} {report_entry['EntityName']}</p>"
            report += f"<p>{report_entry['Date']}</p>"
            if 'TagHeadline' in report_entry:
                report += f"{report_entry['TagHeadline']}</p>"
            if 'TagBody' in report_entry:
                report += f"{report_entry['TagBody']}</p>"
            report += f"<p></p><p></p>"

        if len(active_workitems_report_data) > 0:
            report += f"Active WorkItems<p><p></p></p>"
            for report_entry in active_workitems_report_data:
                report += f"<p>{report_entry['EntityType']} {report_entry['EntityName']}</p>"
                report += f"<p>{report_entry['Date']}</p>"
                report += f"<p>{report_entry['Person']}: {report_entry['Summary']}</p>"
            report += f"<p><p></p></p>"

        if len(done_workitems_report_data):
            report += f"Done WorkItems<p><p></p></p>"
            for report_entry in done_workitems_report_data:
                report += f"<p>{report_entry['EntityType']} {report_entry['EntityName']}</p>"
                report += f"<p>{report_entry['Date']}</p>"
                report += f"<p>{report_entry['Person']}: {report_entry['Summary']}</p>"
            report += f"<p><p></p></p>"

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
        if e['Entity'] in self.active_entity_order:
            return self.active_entity_order.get(e['Entity'])
        else:
            return self.num_active_entities + 1

    def create_search_report(self, search_dict: dict) -> str:
        search_results = self.search_notes(search_dict)
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

    # TODO: Generalize -- currently requires TextTag, so specific to Status Report !!
    def search_notes(self, search_dict: dict) -> list:
        entity_arg = search_dict.get('entity_arg')
        entity_aspect_arg = search_dict.get('entity_aspect_arg')
        entity_type = search_dict.get('entity_type')
        begin_date_str = search_dict.get('begin_date')
        end_date_str = search_dict.get('end_date')
        search_term = search_dict.get('search_term')
        if search_term:
            # Always case insensitive for now
            search_term = search_term.lower()

        entity_list = []
        if entity_arg:
            entity_list = entity_arg.split(',')

        entity_aspects = []
        if entity_aspect_arg:
            entity_aspect_strings = entity_aspect_arg.split(',')
            for entity_aspect_string in entity_aspect_strings:
                entity_aspects.append(EntityAspect.map_from(entity_aspect_string))

        begin_date = None
        if begin_date_str:
            begin_date = datetime.strptime(begin_date_str, DATE_DASH_FORMAT)
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, DATE_DASH_FORMAT)
        # print(begin_date)
        search_results = []
        for notedoc in self.notedoc_repo_cache.values():
            if NoteDocFileRepo._is_notedoc_file_in_search(notedoc, entity_list, entity_aspects, entity_type):
                if notedoc.structure == NoteDocStructure.JOURNAL:
                    # TODO: Implement filtering on search_term; Generalize beyond Status search
                    match_notes = notedoc.search_notes_text_tag(begin_date, end_date, 'Status')
                    if len(match_notes) > 0:
                        search_results.extend(match_notes)
                elif notedoc.structure == NoteDocStructure.OUTLINE:
                    match_notes = notedoc.search_notes(search_term)
                    if len(match_notes) > 0:
                        search_results.extend(match_notes)
        return search_results

    @staticmethod
    def _is_notedoc_file_in_search(notedoc: NoteDocument, entity_list: list, entity_aspects: list, entity_type: str) -> bool:
        match_name = True
        notedoc_entity = f'{notedoc.entity_type}.{notedoc.entity_name}'
        if len(entity_list) > 0 and notedoc_entity not in entity_list:
            match_name = False

        match_aspect = True
        if len(entity_aspects) > 0 and notedoc.entity_aspect not in entity_aspects:
            match_aspect = False

        return match_name & match_aspect

    def search_journal_notes(self, **kwargs):
        # for arg in kwargs:
        #     print(arg)
        begin_date_str = kwargs.get('begin_date')
        end_date_str = kwargs.get('end_date')
        entity = kwargs.get('entity')
        incl_entity_children = kwargs.get('incl_entity_children')

        # print(begin_date_str)
        begin_date = datetime.strptime(begin_date_str, DATE_DASH_FORMAT)
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, DATE_DASH_FORMAT)
        # print(begin_date)

        # TODO: populate search_dict and call search_notes() instead of below
        # search_dict['entity_name_arg'] = ... join entity_name with any children, if true
        #
        search_dict = dict()
        if entity:
            entity_list = [entity]
            if incl_entity_children and entity in self.active_entity_child_entities:
                entity_list.extend(self.active_entity_child_entities[entity])
            search_dict['entity_arg'] = ','.join(entity_list)

        search_dict['entity_aspect_arg'] = ','.join(EntityAspect.JOURNAL_ASPECTS)
        search_dict['begin_date'] = begin_date_str
        search_dict['end_date'] = end_date_str
        return self.search_notes(search_dict)

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

    @staticmethod
    def _map_aspect_to_file_suffix(aspect: EntityAspect):
        if aspect == EntityAspect.REFERENCE:
            return 'nodoc'
        elif aspect == EntityAspect.TOOLBOX:
            return 'ntlbox'
        elif aspect == EntityAspect.WORK_JOURNAL:
            return 'nwdoc'
        elif aspect == EntityAspect.DESIGN_JOURNAL:
            return 'ndsdoc'
        elif aspect == EntityAspect.MEETING_JOURNAL:
            return 'njdoc'
        elif aspect == EntityAspect.SUMMARIZER:
            return 'nzdoc'
        else:
            raise Exception(f'Not supported: {aspect}')

    @staticmethod
    def _derive_file_name(entity: Entity, aspect: EntityAspect):
        return f'{entity.entity_type}.{entity.entity_name}.{NoteDocFileRepo._map_aspect_to_file_suffix(aspect)}'


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

