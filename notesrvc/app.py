from flask import Flask, request
import logging
from datetime import datetime, timedelta

from notesrvc.config import Config
from notesrvc.data_access.notedoc_filerepo import NoteDocFileRepo
from notesrvc.constants import EntityAspect, DATE_DASH_FORMAT

app = Flask(__name__)

FLASK_PORT_NUMBER = 5100

config = Config()
notedoc_filerepo = NoteDocFileRepo(config)


@app.route('/notedocsvc/ping', methods=['GET'])
def ping():
    return 'pong'


@app.route('/notedocsvc/outlinetext', methods=['GET'])
def get_outline_text():
    entity_name = request.args.get('name')
    entity_type = request.args.get('type')
    entity_aspect = request.args.get('aspect')
    # TODO: Add assertion on entity_aspect: only outline types
    file_name = _derive_file_name(entity_name, entity_type, entity_aspect)
    notedoc = notedoc_filerepo.get_notedoc(file_name)
    outline_text = notedoc.render_as_outline_text()
    return outline_text


@app.route('/notedocsvc/statusreport', methods=['GET'])
def get_status_report():
    num_days_before = int(request.args.get('days'))
    if not num_days_before:
        num_days_before = 1
    begin_date = datetime.now() - timedelta(days=num_days_before)
    begin_date_str = begin_date.strftime(DATE_DASH_FORMAT)
    report = notedoc_filerepo.create_status_report(begin_date_str)
    return report


def _derive_file_name(entity_name: str, entity_type: str, entity_aspect: str) -> str:
    if entity_aspect == EntityAspect.TOOLBOX:
        return f'Toolbox.{entity_name}.nodoc'
    elif entity_aspect == EntityAspect.REFERENCE:
        return f'{entity_type}.{entity_name}.nodoc'
    else:
        raise Exception(
            f'Combination not support: entity_name: {entity_name}, entity_type: {entity_type}, entity_aspect: {entity_aspect}')


if __name__ == '__main__':
    logging.info('Starting Flask')

    notedoc_filerepo.initialize_active_notedocs()
    notedoc_filerepo.import_active_notedocs()

    app.run(host='0.0.0.0', debug=False, port=FLASK_PORT_NUMBER)
