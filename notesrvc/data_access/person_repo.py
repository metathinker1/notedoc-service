import json
from notesrvc.config import Config
from notesrvc.model.person import Person


class PersonRepo:

    def __init__(self, config: Config):
        self.config = config
        self.person_full_name_cache = dict()
        self.person_abbr_cache = dict()
        self.default_person = config.default_person
        self.person_full_name_cache[f'{self.default_person.first_name} {self.default_person.last_name}'] = self.default_person
        self.person_abbr_cache[self.default_person.abbr] = self.default_person

    def get_person(self, name_to_match: str):
        if name_to_match in self.person_full_name_cache:
            return self.person_full_name_cache.get(name_to_match)
        elif name_to_match in self.person_abbr_cache:
            return self.person_abbr_cache.get(name_to_match)
        else:
            raise Exception(f'Person not found: {name_to_match}')

    def import_person_repo(self):
        file_name = self.config.person_repo_file
        with open(file_name, 'r') as person_repo_file:
            person_repo_json = person_repo_file.read()

        persons = json.loads(person_repo_json)
        for p in persons:
            person = Person(p.get('FirstName'), p.get('LastName'), p.get('Abbr'))
            self.person_full_name_cache[f'{person.first_name} {person.last_name}'] = person
            self.person_abbr_cache[person.abbr] = person
