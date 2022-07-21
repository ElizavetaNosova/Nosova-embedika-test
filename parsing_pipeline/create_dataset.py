import pandas as pd
import json
import os
from .ner import extract_entities

def json_files_to_dataset(json_files_directory,
                          obligatory_keys,
                          columns_order):

    data = []
    for filename in os.listdir(json_files_directory):
        filepath = os.path.join(json_files_directory, filename)
        if os.path.isfile(filepath) and filename.endswith('.json'):
            with open(filepath) as f:
                sample = json.load(f)
            if isinstance(sample, dict) and all([sample.get(key) for key in obligatory_keys]):
                data.append([sample.get(key, '') for key in columns_order])
    return pd.DataFrame(columns=columns_order, data=data)


def create_ner_dataset(json_files_directory,
                    obligatory_keys=['text'],
                    columns_order=['url', 'tags', 'title', 'text'],
                    ner_columns=['title', 'text']):
    df = json_files_to_dataset(json_files_directory,  obligatory_keys, columns_order)
    for column_name in ner_columns:
        df[column_name+'_ner'] = df[column_name].apply(
            lambda x: json.dumps(extract_entities(x), ensure_ascii=False)
        )
    return df
