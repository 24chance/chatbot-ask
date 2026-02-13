import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = "chanceown/askchat"

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Loading QA model on", device)

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

def small_talk(question: str):
    q = question.lower().strip()

    greetings = ["hi", "hey", "hello", "hey there"]
    identity = ["who are you", "what are you", "what can you do"]
    thanks = ["thanks", "thank you", "thx"]

    if any(g in q for g in greetings):
        return "Hello I’m a Rwanda tax assistant. Ask me anything about taxes."

    if any(i in q for i in identity):
        return "I’m a chatbot trained to answer Rwanda tax questions."

    if any(t in q for t in thanks):
        return "You’re welcome"

    return None


ALLOWED_TOPICS = ["tax", "rra", "vat", "tin", "income", "declaration", "payment", ""]


def is_gibberish(text: str) -> bool:
    words = text.lower().split()
    unique_ratio = len(set(words)) / max(len(words), 1)

    # too repetitive
    if unique_ratio < 0.5:
        return True

    # repeated phrase like "tin number is tin number"
    for w in set(words):
        if words.count(w) > len(words) * 0.4:
            return True

    return False

def ask_model(question: str) -> str:

    reply = small_talk(question)
    if reply:
        return reply

    # topic guard
    if not any(word in question.lower() for word in ALLOWED_TOPICS):
        return "Sorry, I can only answer Rwanda tax related questions."

    text = "answer question: " + question
    inputs = tokenizer(text, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
        **inputs,
        max_length=200,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=2.5,
        no_repeat_ngram_size=3,
        return_dict_in_generate=True,
        output_scores=True
    )

    sequences = outputs.sequences
    scores = outputs.scores

    # confidence score
    probs = [F.softmax(score, dim=-1).max().item() for score in scores]
    confidence = sum(probs) / len(probs)
    print('confidence', confidence)

    answer = tokenizer.decode(sequences[0], skip_special_tokens=True)

    # confidence guard
    if confidence < 0.45 or is_gibberish(answer):
        return "Sorry, I can only answer Rwanda tax related questions."

    return answer
