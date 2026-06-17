from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:

    def __init__(self, disease_info):

        self.sections = {}

        for key, value in disease_info.items():

            if isinstance(value, list):
                text = " ".join(value)
            else:
                text = str(value)

            self.sections[key] = text

        self.keys = list(self.sections.keys())

        self.documents = list(self.sections.values())

        self.vectorizer = TfidfVectorizer()

        self.matrix = self.vectorizer.fit_transform(
            self.documents
        )

    def search(self, question):

        q = self.vectorizer.transform([question])

        scores = cosine_similarity(
            q,
            self.matrix
        )

        best_index = scores.argmax()

        return self.keys[best_index]