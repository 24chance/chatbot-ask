from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import threading

_model = None
_tokenizer = None
_lock = threading.Lock()

def load_model():
    global _model, _tokenizer

    # double-check locking so it loads only once
    if _model is None or _tokenizer is None:
        with _lock:
            if _model is None or _tokenizer is None:
                model_name = "facebook/m2m100_418M"
                _tokenizer = M2M100Tokenizer.from_pretrained(model_name)
                _model = M2M100ForConditionalGeneration.from_pretrained(model_name)

def translate_text(text, source_lang, target_lang):
    load_model()  # loads ONLY the first time this runs

    _tokenizer.src_lang = source_lang
    encoded = _tokenizer(text, return_tensors="pt")
    generated_tokens = _model.generate(
        **encoded,
        forced_bos_token_id=_tokenizer.get_lang_id(target_lang)
    )
    return _tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
