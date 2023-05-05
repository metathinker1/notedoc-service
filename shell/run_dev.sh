#!/bin/zsh
export PYTHONPATH=/Users/robertwood/Project.ThoughtPal/notedoc-service
export NOTEDOC_ACTIVE_ENTITIES_FILE=/Users/robertwood/Project.ThoughtPal/NoteDocExtracts/ActiveEntities.json
export NOTEDOC_FILE_REPO_PATH=/Users/robertwood/Project.ThoughtPal/AncNoteDocRepo
export PERSON_REPO_FILE=/Users/robertwood/Project.ThoughtPal/NoteDocExtracts/PersonRepo.json
python ../notesrvc/app.py