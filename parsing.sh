#! /bin/sh.
luigid --background --logdir ./logs
python3 -m parsing_pipeline CreateNerDataset && rm -r data/temp