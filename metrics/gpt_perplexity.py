from transformers import GPT2TokenizerFast, GPT2LMHeadModel
import torch
from typing import List
from statistics import mean
from tqdm import tqdm


class PerplexityScorer:
    def __init__(
        self,
        model_name_or_path="sberbank-ai/rugpt3small_based_on_gpt2",
        tokenizer_name_or_path=None,
        max_length=512,
    ):
        tokenizer_name_or_path = (
            tokenizer_name_or_path
            if tokenizer_name_or_path is not None
            else model_name_or_path
        )
        self.tokenizer = GPT2TokenizerFast.from_pretrained(tokenizer_name_or_path)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = GPT2LMHeadModel.from_pretrained(model_name_or_path).to(device)
        # toDo: проверять, что значение не превышает количество позиционных токенов модели
        self.max_length = max_length

    def _calc_text_loss(self, text: List[str]):
        # ToDo Реализовать подсчет для батча (с поправкой на размер)
        encoding = self.tokenizer(
            [text], return_tensors="pt", max_length=self.max_length, truncation=True
        ).to(self.model.device)
        with torch.no_grad():
            return (
                self.model(**encoding, labels=encoding["input_ids"]).loss.exp().item()
            )

    def __call__(self, texts: List[str]):
        batch_scores = [self._calc_text_loss(text) for text in tqdm(texts)]
        return mean(batch_scores)
