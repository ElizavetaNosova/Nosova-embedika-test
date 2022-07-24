import os
from transformers import GPT2LMHeadModel
import torch

current_file_dir = os.path.dirname(os.path.realpath(__file__))
GPT_DIRECTORY = os.path.join(os.path.dirname(current_file_dir), "models", "kremlin_gpt")


def load_kremlin_gpt(device=None):
    if not device:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    return GPT2LMHeadModel.from_pretrained(GPT_DIRECTORY).to(device)
