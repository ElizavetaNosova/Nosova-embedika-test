from transformers import AutoTokenizer

def get_generation_parameters(tokenizer:AutoTokenizer):
    return {
    'min_length': 50,
    'max_length':250,
    'bad_words_ids':[[tokenizer.pad_token_id]],
    'eos_token_id':tokenizer.eos_token_id,
    'pad_token_id':tokenizer.eos_token_id,
    'do_sample':True,
    'top_p': 0.97,
    'top_k':10,
    'num_return_sequences':5
}