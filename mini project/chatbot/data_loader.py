import json


class DiseaseDataLoader:

    def __init__(self, json_file):

        with open(json_file, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.data = {}
        diseases = raw.get("diseases", [])

        for entry in diseases:
            name = entry.get("name", "")
            if name:
                key = self._normalize_name(name)
                self.data[key] = entry

    def _normalize_name(self, name):

        return name.strip().lower().replace("_", " ")

    def get_disease(self, disease_name):

        key = self._normalize_name(disease_name)
        return self.data.get(key, {})
