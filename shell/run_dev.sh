#!/bin/zsh
source ../venv/bin/activate
# export PYTHONPATH="/Users/robertwood/Project.ThoughtPal/notedoc-service/venv/bin"
export PYTHONPATH="/Users/robertwood/Project.ThoughtPal/notedoc-service"
export NOTEDOC_ACTIVE_ENTITIES_FILE="/Users/robertwood/Project.ThoughtPal/NoteDocExtracts/ActiveEntities.json"
export ANCESTRY_DOMAIN_ENTITIES_FILE_NAME="/Users/robertwood/Project.ThoughtPal/NoteDocExtracts/Domain.Ancestry.json"
export NOTEDOC_FILE_REPO_PATH="/Users/robertwood/Project.ThoughtPal/AncNoteDocRepo"
export PERSON_REPO_FILE="/Users/robertwood/Project.ThoughtPal/NoteDocExtracts/PersonRepo.json"
python3 ../notesrvc/app.py
