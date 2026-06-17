import json


class DiseaseDataLoader:

    def __init__(self, json_file):

        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get_disease(self, disease_name):

        return self.data.get(disease_name, {})