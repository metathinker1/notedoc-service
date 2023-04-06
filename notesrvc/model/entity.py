

class Entity:

    def __init__(self, entity_type: str, entity_name: str):
        self.entity_type = entity_type
        self.entity_name = entity_name
        self.entity = f'{entity_type}.{entity_name}'
