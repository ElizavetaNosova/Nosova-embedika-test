from .tags import BOS_TAG, EOS_TAG, TITLE_TAG, TEXT_TAG, SELECTED_ENTITIES

from transformers import AutoTokenizer

TOKENIZER_NAME_OR_PATH = "sberbank-ai/rugpt3small_based_on_gpt2"


def init_kremlin_tokenizer(tokenizer_name_or_path=None):
    if not tokenizer_name_or_path:
        tokenizer_name_or_path = TOKENIZER_NAME_OR_PATH
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path)
    tokenizer.add_special_tokens(
        {
            "bos_token": BOS_TAG,
            "eos_token": EOS_TAG,
            "pad_token": "[PAD]",
            "additional_special_tokens": [TITLE_TAG, TEXT_TAG, *SELECTED_ENTITIES],
        }
    )
    return tokenizer
