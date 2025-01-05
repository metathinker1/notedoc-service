from flask import Flask, request
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import json

from notesrvc.config import Config
from notesrvc.model.entity import Entity
from notesrvc.data_access.notedoc_filerepo import NoteDocFileRepo
from notesrvc.data_access.person_repo import PersonRepo
from notesrvc.data_access.workitem_filerepo import WorkItemFileRepo
from notesrvc.constants import EntityAspect, DATE_DASH_FORMAT, MONTH_DAY_DATE_FORMAT

app = Flask(__name__)
cors = CORS(app)

FLASK_PORT_NUMBER = 5100

config = Config()
person_repo = PersonRepo(config)
workitem_filerepo = WorkItemFileRepo(config)
notedoc_filerepo = NoteDocFileRepo(config, person_repo, workitem_filerepo)


@app.route('/notedocsvc/ping', methods=['GET'])
def ping():
    return 'pong'


@app.route('/notedocsvc/recent-entities', methods=['GET'])
def get_recent_entities():
    recent_active_entities_sorted = {k: v for k, v in sorted(notedoc_filerepo.recent_active_entities.items(), key=lambda item: item[0])}
    recent_active_entities_json = json.dumps(recent_active_entities_sorted)
    return recent_active_entities_json


@app.route('/notedocsvc/outline/summary', methods=['GET'])
def get_outline_text():
    entity_name = request.args.get('name')
    entity_type = request.args.get('type')
    entity_aspect = request.args.get('aspect')
    response_format = request.args.get('format')
    if not response_format:
        response_format = 'Text'
    # TODO: Add assertion on entity_aspect: only outline types
    # file_name = _derive_file_name(entity_name, entity_type, entity_aspect)
    # notedoc = notedoc_filerepo.get_notedoc(file_name)
    entity = Entity(entity_type, entity_name)
    notedoc = notedoc_filerepo.get_notedoc_entity(entity, EntityAspect.map_from(entity_aspect))
    if response_format == 'text':
        outline_text = notedoc.render_as_outline_text()
        return outline_text
    elif response_format == 'html':
        html_snippet = notedoc.render_as_html_snippet()
        return html_snippet
    else:
        return f"Unsupport format: {response_format}"


@app.route('/notedocsvc/report/status', methods=['GET'])
def get_status_report_v2():
    days = request.args.get('days')
    begin_month_day_str = request.args.get('begin')
    end_month_day_str = request.args.get('end')
    begin_date_str, end_date_str = derive_begin_end_dates(days, begin_month_day_str, end_month_day_str)
    entity = request.args.get('entity')
    ancestry_domain = request.args.get('anc_domain')

    incl_summary_items = True
    text_tag_type_matches = ['Status']
    if incl_summary_items:
        text_tag_type_matches.extend(
            ['Summary', 'Work Summary', 'Support Summary', 'Discussion Summary', 'Meeting Summary'])

    entity_aspect_arg = ','.join(EntityAspect.JOURNAL_ASPECTS + EntityAspect.REFERENCE_ASPECTS)
    response_format = request.args.get('format')
    if not response_format:
        response_format = 'text'

    report = notedoc_filerepo.create_report(begin_date=begin_date_str, end_date=end_date_str, entity_aspect_arg=entity_aspect_arg,
                                   text_tag_type_matches=text_tag_type_matches, ancestry_domain=ancestry_domain,
                                   entity=entity, response_format=response_format)
    return report


@app.route('/notedocsvc/report/keyinfo', methods=['GET'])
def get_keyinfo_report():
    days = request.args.get('days')
    begin_month_day_str = request.args.get('begin')
    end_month_day_str = request.args.get('end')
    begin_date_str, end_date_str = derive_begin_end_dates(days, begin_month_day_str, end_month_day_str)
    ancestry_domain = request.args.get('anc_domain')

    text_tag_type_matches = ['KeyInfo']

    entity_aspect_arg = ','.join(EntityAspect.JOURNAL_ASPECTS + EntityAspect.REFERENCE_ASPECTS)
    response_format = request.args.get('format')
    if not response_format:
        response_format = 'text'

    report = notedoc_filerepo.create_report(begin_date=begin_date_str, end_date=end_date_str, entity_aspect_arg=entity_aspect_arg,
                                   text_tag_type_matches=text_tag_type_matches, ancestry_domain=ancestry_domain,
                                   response_format=response_format)
    return report


@app.route('/notedocsvc/report/summz', methods=['GET'])
def get_summrizer_report():
    days = request.args.get('days')
    begin_month_day_str = request.args.get('begin')
    end_month_day_str = request.args.get('end')
    begin_date_str, end_date_str = derive_begin_end_dates(days, begin_month_day_str, end_month_day_str)
    ancestry_domain = request.args.get('anc_domain')

    text_tag_type_matches = ['Summarizer']

    entity_aspect_arg = ','.join(EntityAspect.JOURNAL_ASPECTS + EntityAspect.REFERENCE_ASPECTS)
    response_format = request.args.get('format')
    if not response_format:
        response_format = 'text'

    report = notedoc_filerepo.create_report(begin_date=begin_date_str, end_date=end_date_str, entity_aspect_arg=entity_aspect_arg,
                                   text_tag_type_matches=text_tag_type_matches, ancestry_domain=ancestry_domain,
                                   response_format=response_format)
    return report


@app.route('/notedocsvc/report/srvcflows', methods=['GET'])
def get_service_flows_report():
    days = request.args.get('days')
    begin_month_day_str = request.args.get('begin')
    end_month_day_str = request.args.get('end')
    begin_date_str, end_date_str = derive_begin_end_dates(days, begin_month_day_str, end_month_day_str)
    ancestry_domain = request.args.get('anc_domain')

    text_tag_type_matches = ['SrvcFlows']

    entity_aspect_arg = ','.join(EntityAspect.JOURNAL_ASPECTS + EntityAspect.REFERENCE_ASPECTS)
    response_format = request.args.get('format')
    if not response_format:
        response_format = 'text'

    report = notedoc_filerepo.create_report(begin_date=begin_date_str, end_date=end_date_str, entity_aspect_arg=entity_aspect_arg,
                                   text_tag_type_matches=text_tag_type_matches, ancestry_domain=ancestry_domain,
                                   response_format=response_format)
    return report


@app.route('/notedocsvc/report/deploychain', methods=['GET'])
def get_deploychain_report():
    days = request.args.get('days')
    begin_month_day_str = request.args.get('begin')
    end_month_day_str = request.args.get('end')
    begin_date_str, end_date_str = derive_begin_end_dates(days, begin_month_day_str, end_month_day_str)
    ancestry_domain = request.args.get('anc_domain')

    text_tag_type_matches = ['DeployChain']

    entity_aspect_arg = ','.join(EntityAspect.JOURNAL_ASPECTS + EntityAspect.REFERENCE_ASPECTS)
    response_format = request.args.get('format')
    if not response_format:
        response_format = 'text'

    report = notedoc_filerepo.create_report(begin_date=begin_date_str, end_date=end_date_str, entity_aspect_arg=entity_aspect_arg,
                                   text_tag_type_matches=text_tag_type_matches, ancestry_domain=ancestry_domain,
                                   response_format=response_format)
    return report


def derive_begin_end_dates(days, begin_month_day_str, end_month_day_str):
    if days:
        num_days_before = int(days)
        begin_date = datetime.now() - timedelta(days=num_days_before)
        begin_date_str = begin_date.strftime(DATE_DASH_FORMAT)
        end_date_str = None
    else:
        if begin_month_day_str:
            if len(begin_month_day_str) == 5:
                begin_date_str = f'2024-{begin_month_day_str}'
            else:
                begin_date_str = begin_month_day_str
        else:
            begin_date = datetime.now() - timedelta(days=1)
            begin_date_str = begin_date.strftime(DATE_DASH_FORMAT)
        end_date_str = None
        if end_month_day_str:
            if len(end_month_day_str) == 5:
                end_date_str = f'2024-{end_month_day_str}'
            else:
                end_date_str = end_month_day_str
    return begin_date_str, end_date_str

# TODO: Deprecate
@app.route('/notedocsvc/statusreport', methods=['GET'])
def get_status_report():
    days = request.args.get('days')
    begin_month_day_str = request.args.get('begin')
    end_month_day_str = request.args.get('end')
    # entity: <entity_type>.<entity_name>
    ancestry_domain = request.args.get('anc_domain')
    entity = request.args.get('entity')
    incl_entity_children_str = request.args.get('children')
    incl_work_items_str = request.args.get('work')
    incl_entity_children = False
    if incl_entity_children_str:
        incl_entity_children = True if incl_entity_children_str.lower() == 'true' else False
    incl_work_items = False
    if incl_work_items_str:
        incl_work_items = True if incl_work_items_str.lower() == 'true' else False
    response_format = request.args.get('format')
    if not response_format:
        response_format = 'text'
    incl_summary_items = True

    if days:
        num_days_before = int(days)
        begin_date = datetime.now() - timedelta(days=num_days_before)
        begin_date_str = begin_date.strftime(DATE_DASH_FORMAT)
        end_date_str = None
    else:
        if begin_month_day_str:
            if len(begin_month_day_str) == 5:
                begin_date_str = f'2024-{begin_month_day_str}'
            else:
                begin_date_str = begin_month_day_str
        else:
            begin_date = datetime.now() - timedelta(days=1)
            begin_date_str = begin_date.strftime(DATE_DASH_FORMAT)
        end_date_str = None
        if end_month_day_str:
            if len(end_month_day_str) == 5:
                end_date_str = f'2024-{end_month_day_str}'
            else:
                end_date_str = end_month_day_str

    if ancestry_domain:
        report = notedoc_filerepo.create_ancestry_domain_status_report(begin_date_str, end_date_str, ancestry_domain, incl_summary_items, response_format)
    else:
        report = notedoc_filerepo.create_status_report(begin_date_str, end_date_str, entity, incl_entity_children, incl_work_items, incl_summary_items, response_format)
    return report


@app.route('/notedocsvc/search/tool', methods=['POST'])
def handle_tool_search():
    search_dict = json.loads(request.data)
    if search_dict.get('aspect') == EntityAspect.TOOLBOX:
        # search_result = notedoc_filerepo.search_for_tool(search_term=search_dict.get('search_term'))
        search_report = notedoc_filerepo.create_tool_search_report(search_dict)
        return search_report
    else:
        return f"aspect: {search_dict.get('aspect')} not yet supported"


@app.route('/notedocsvc/search', methods=['POST'])
def handle_search():
    search_dict = json.loads(request.data)
    search_report = notedoc_filerepo.create_search_report(search_dict)
    return search_report


# def _derive_file_name(entity_name: str, entity_type: str, entity_aspect: str) -> str:
#     if entity_aspect == EntityAspect.TOOLBOX:
#         return f'{entity_type}.{entity_name}.ntlbox'
#     elif entity_aspect == EntityAspect.REFERENCE:
#         return f'{entity_type}.{entity_name}.nodoc'
#     else:
#         raise Exception(
#             f'Combination not support: entity_name: {entity_name}, entity_type: {entity_type}, entity_aspect: {entity_aspect}')


if __name__ == '__main__':
    logging.info('Starting Flask')

    notedoc_filerepo.initialize_active_entities()
    notedoc_filerepo.initialize_domain_entities()
    person_repo.import_person_repo()
    # 2024.12.31 - not needed with import_supported_notedocs()
    # notedoc_filerepo.import_active_notedocs()

    # 2024.12.31
    # notedoc_filerepo.import_default_supported_notedocs()
    notedoc_filerepo.import_supported_notedocs()

    # TODO: Use configuration: by include_list or by_file_type ['nwdoc', 'nodoc', ...]

    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT_NUMBER)
