
from notesrvc.constants import DATE_FORMAT


class BaseStatusReport:

    def __init__(self):
        pass

    def _derive_unique_entity_date_or_none(self, report_data: list):
        entities = [f"{e['EntityType']}: {e['EntityName']}" for e in report_data]
        unique_entities = set(entities)
        unique_entity = unique_entities.pop() if len(unique_entities) == 1 else None
        dates = [e['Date'] for e in report_data]
        unique_dates = set(dates)
        unique_date = unique_dates.pop() if len(unique_dates) == 1 else None
        return unique_entity, unique_date


class HTMLStatusReport(BaseStatusReport):

    def __init__(self, active_entity_order):
        self.active_entity_order = active_entity_order
        self.num_active_entities = 0

    def create_report(self, structured_report_data: dict) -> str:
        report = ''
        unique_entity = True if len(structured_report_data) == 0 else False
        entity_keys = list(structured_report_data.keys())
        entity_keys.sort(key=self.entity_sorter)
        for section_entity in entity_keys:
            if not unique_entity:
                report += f"<h4>{section_entity}</h4>"
            entity_section = structured_report_data.get(section_entity)
            section_dates = list(entity_section.keys())
            section_dates = sorted(section_dates, reverse=True)
            for section_date in section_dates:
                section_date_str = section_date.strftime(DATE_FORMAT)
                report += f"<h4>{section_date_str}</h4>"
                report_entries = entity_section.get(section_date)
                for report_entry in report_entries:
                    if 'TagType' in report_entry:
                        report += f"<i>{report_entry['TagType']}</i>"
                    if 'TagHeadline' in report_entry:
                        report += f": {report_entry['TagHeadline']}<br>"
                    if 'TagBody' in report_entry:
                        tag_body = HTMLStatusReport._tag_body_as_html_snippet(report_entry['TagBody'])
                        report += f"{tag_body}<br><br>"
        return report

    def create_report_tbd(self, report_data: list) -> str:
        report = ''
        unique_entity, unique_date = super()._derive_unique_entity_date_or_none(report_data)
        section_header = "Section"
        if unique_entity:
            section_entity_header = f"<h3>{unique_entity}</h3>"
            report += section_header
        if unique_date:
            date_section_header = f"<h3>{unique_date}</h3>"
            report += section_header

        prev_entity_section_header = None
        prev_date_section_header = None
        for report_entry in report_data:
            if not unique_entity:
                section_entity_header = f"<h4>{report_entry['EntityType']}: {report_entry['EntityName']}</h4>"
                if prev_entity_section_header:
                    if prev_entity_section_header != section_entity_header:
                        # report += f"<br>"
                        report += section_entity_header
                else:
                    report += section_entity_header
            if not unique_date:
                date_section_header = f"<h4>{report_entry['Date']}</h4>"
                if prev_date_section_header:
                    if prev_date_section_header != date_section_header:
                        report += date_section_header
                else:
                    report += date_section_header
            if 'TagType' in report_entry:
                report += f"<i>{report_entry['TagType']}</i>"
            if 'TagHeadline' in report_entry:
                report += f": {report_entry['TagHeadline']}<br>"
            if 'TagBody' in report_entry:
                tag_body = HTMLStatusReport._tag_body_as_html_snippet(report_entry['TagBody'])
                report += f"{tag_body}<br>"
            # report += f"<br>"
            if not prev_entity_section_header:
                prev_entity_section_header = section_entity_header
                prev_date_section_header = date_section_header
            elif prev_entity_section_header == section_entity_header:
                prev_date_section_header = date_section_header
            else:
                prev_entity_section_header = section_entity_header
                prev_date_section_header = None

        return report

    def entity_sorter(self, e):
        if e in self.active_entity_order:
            return self.active_entity_order.get(e)
        else:
            return self.num_active_entities + 1



    @staticmethod
    def _tag_body_as_html_snippet(tag_body: str):
        return tag_body.replace('\n', '<br>')
