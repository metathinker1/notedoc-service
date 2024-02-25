#!/bin/zsh
source ../venv/bin/activate
export PYTHONPATH="/Users/rwood/Tools/notedoc-service"
export NOTEDOC_ACTIVE_ENTITIES_FILE="/Users/rwood/Tools/NoteDocOrganizer/ActiveEntities.json"
export NOTEDOC_FILE_REPO_PATH="/Users/rwood/NoteDocRepo"
export PERSON_REPO_FILE="/Users/rwood/Tools/NoteDocOrganizer/PersonRepo.json"
python3 ../notesrvc/app.py
