from torchmetrics.text.bert import BERTScore
from transformers import AutoModel, AutoTokenizer
from statistics import mean
from typing import List


class BERTScoreWrapper:
    def __init__(self, model_name_or_path="cointegrated/rubert-tiny2"):
        self._bert_scorer = None
        self._model_name_or_path = model_name_or_path

    def _init_scorer(self):
        # Можно инициализировать через название модели, но тогда она будет скачиваться при каждом вызове
        bert = AutoModel.from_pretrained(self._model_name_or_path)
        tokenizer = AutoTokenizer.from_pretrained(self._model_name_or_path)

        def tokenizer_wrapper(text, max_length):
            return tokenizer(
                text,
                return_tensors="pt",
                max_length=max_length,
                padding=True,
                truncation=True,
            )

        self._bert_scorer = BERTScore(model=bert, user_tokenizer=tokenizer_wrapper)

    def __call__(self, generated_texts: List[str], gold_texts: List[str]) -> float:
        if not self._bert_scorer:
            self._init_scorer()
        return mean(self._bert_scorer(generated_texts, gold_texts)["f1"])
