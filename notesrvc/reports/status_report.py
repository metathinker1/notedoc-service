
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

    def __init__(self):
        pass

    def create_report(self, report_data: list) -> str:
        report = ''
        unique_entity, unique_date = super()._derive_unique_entity_date_or_none(report_data)
        section_header = "Section"
        if unique_entity:
            section_entity_header = f"<h3>{unique_entity}</h3>"
            report += section_header
        elif unique_date:
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
                report += f"{report_entry['TagBody']}<br>"
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
