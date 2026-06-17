from chatbot.retriever import Retriever


class OfflineHealthChatbot:

    def __init__(self, disease_data):

        self.disease_data = disease_data

        self.retriever = Retriever(
            disease_data
        )

    def answer(self, question):
        """Answer a question about the disease by showing the full details from the JSON backend."""
        return self._format_full()

    def _format_full(self):
        """Format and return all disease information."""
        print(f"[DEBUG] _format_full() called. Disease data keys: {self.disease_data.keys()}")
        
        parts = []
        
        # NAME (always show)
        name = self.disease_data.get("name")
        if name:
            parts.append(f"📌 NAME\n\n{name}\n")
            print(f"[DEBUG] Added NAME: {name}")

        # BRIEF
        brief = self.disease_data.get("brief")
        if brief:
            parts.append(f"📖 BRIEF\n\n{brief}\n")
            print(f"[DEBUG] Added BRIEF")

        # CAUSES
        causes = self.disease_data.get("causes")
        if causes and isinstance(causes, list) and len(causes) > 0:
            cause_text = "\n".join([f"• {c}" for c in causes])
            parts.append(f"⚠️ CAUSES\n\n{cause_text}\n")
            print(f"[DEBUG] Added CAUSES with {len(causes)} items")

        # PRECAUTIONS  
        precautions = self.disease_data.get("precautions")
        if precautions and isinstance(precautions, list) and len(precautions) > 0:
            precaution_text = "\n".join([f"• {p}" for p in precautions])
            parts.append(f"🛡️ PRECAUTIONS\n\n{precaution_text}\n")
            print(f"[DEBUG] Added PRECAUTIONS with {len(precautions)} items")

        # ASSOCIATED SYMPTOMS
        symptoms = self.disease_data.get("associated_symptoms") or self.disease_data.get("associated symptoms")
        if symptoms and isinstance(symptoms, list) and len(symptoms) > 0:
            symptom_text = "\n".join([f"• {s}" for s in symptoms])
            parts.append(f"🩺 ASSOCIATED SYMPTOMS\n\n{symptom_text}\n")
            print(f"[DEBUG] Added ASSOCIATED SYMPTOMS with {len(symptoms)} items")

        # DISCLAIMER
        disclaimer = self.disease_data.get("disclaimer")
        if disclaimer:
            parts.append(f"⚠️ DISCLAIMER\n\n{disclaimer}\n")
            print(f"[DEBUG] Added DISCLAIMER")

        # Final message
        parts.append("⚠️ Consult a doctor.")
        
        result = "\n".join(parts)
        print(f"[DEBUG] _format_full() returning {len(result)} characters")
        return result