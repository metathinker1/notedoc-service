from notesrvc.constants import NoteDocAspect, NoteDocStructure
import notesrvc.service.notedoc_factory as notedoc_factory

NOTEDOC_FILE_REPO_PATH = '/Users/robertwood/Google Drive/My Drive/AncNoteDocRepo/_Ancestry'


class NoteDocFileRepo:

    def __init__(self):
        self.notedoc_repo_cache = {}

    def get_notedoc(self, file_name: str):
        if file_name in self.notedoc_repo_cache:
            return self.notedoc_repo_cache.get(file_name)

        file_path = f'{NOTEDOC_FILE_REPO_PATH}/{file_name}'
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

        self.notedoc_repo_cache[file_name] = notedoc

        return notedoc

    @staticmethod
    def _derive_aspect_structure(file_name_parts):
        if file_name_parts[2] == 'nodoc':
            if file_name_parts[0] == 'Toolbox':
                return NoteDocAspect.TOOLBOX, NoteDocStructure.OUTLINE
            else:
                return NoteDocAspect.REFERENCE, NoteDocStructure.OUTLINE
        elif file_name_parts[2] == 'nwdoc':
            return NoteDocAspect.WORK_JOURNAL, NoteDocStructure.JOURNAL
        elif file_name_parts[2] == 'njdoc':
            return NoteDocAspect.MEETING_JOURNAL, NoteDocStructure.JOURNAL
        elif file_name_parts[2] == 'nzdoc':
            return NoteDocAspect.SUMMARIZER, NoteDocStructure.OUTLINE
        else:
            raise Exception(f'Not supported: {file_name_parts[2]}')


if __name__ == '__main__':
    file_name = 'Project.APM_AlertRouter.nodoc'
    notedoc_filerepo = NoteDocFileRepo()
    notedoc_filerepo.get_notedoc(file_name)
