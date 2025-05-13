
# analyzer.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from lime.lime_text import LimeTextExplainer

class CodeAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "microsoft/codebert-base", num_labels=2
        )
        self.explainer = LimeTextExplainer(class_names=["Human", "AI"])

    def analyze(self, code: str, ast=None):

        # Step 0: Temporal analysis (typing speed check)
        temporal_is_human = None
        if ast and 'typing_time' in ast:
            total_chars = len(code)
            typing_time = ast['typing_time']  # in seconds
            if typing_time > 0:
                cps = total_chars / typing_time  # characters per second
                if cps < 4:  # arbitrary threshold: slow typing = human
                    temporal_is_human = True
                else:
                    temporal_is_human = False

        # Step 1: Tokenize
        inputs = self.tokenizer(
            code,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding="max_length"
        )

        # Step 2: Predict using the classification model
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
            ai_prob = probs[1].item()
            is_ai = ai_prob > 0.55  # slightly raised threshold for precision

        # Step 3: Optional AST signal (if provided by parser)
        if ast:
            if len(ast.get("comments", [])) == 0 and ast.get("num_nodes", 0) < 10:
                ai_prob += 0.05  # slight bias
                is_ai = ai_prob > 0.5

        # Step 4: Short input — skip LIME
        if len(code.split()) < 10:

        # Combine semantic and temporal judgments (if temporal available)
            if temporal_is_human is not None:
                if temporal_is_human and not is_ai:
                    ai_prob -= 0.05  # reinforce human judgment
                elif not temporal_is_human and is_ai:
                    ai_prob += 0.05  # reinforce AI suspicion
                is_ai = ai_prob > 0.5
            
                return {
                    "isAI": is_ai,
                    "probability": round(ai_prob, 4),
                    "explanation": []
                }

        # Step 5: Token diversity (simple entropy logic)
        unique_tokens = set(code.split())
        token_entropy = len(unique_tokens) / max(len(code.split()), 1)
        if token_entropy < 0.3:
            ai_prob += 0.03  # repetitive tokens => likely AI

        # Step 6: LIME for longer inputs
        def predict_proba(texts):
            results = []
            for text in texts:
                toks = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding="max_length"
                )
                with torch.no_grad():
                    outs = self.model(**toks)
                    prob = torch.nn.functional.softmax(outs.logits, dim=1).cpu().numpy()
                    results.append(prob[0])
            return results

        try:
            exp = self.explainer.explain_instance(
                code,
                predict_proba,
                num_features=5,
                labels=(1,),
                num_samples=50
            )
            explanation = exp.as_list(label=1)
        except Exception:
            explanation = []

        return {
            "isAI": is_ai,
            "probability": round(ai_prob, 4),
            "explanation": explanation
        }