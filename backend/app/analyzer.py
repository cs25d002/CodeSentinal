# app/analyzer.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = AutoModelForSequenceClassification.from_pretrained("microsoft/graphcodebert-base", num_labels=2)

def analyze_code(code: str):
    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.softmax(logits, dim=-1)
    pred = torch.argmax(probs, dim=-1).item()
    confidence = probs[0][pred].item()
    return pred, round(confidence, 4)
