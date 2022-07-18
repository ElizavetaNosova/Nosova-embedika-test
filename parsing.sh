#! /bin/sh.
luigid --background --logdir ./logs
python3 parsing_pipeline/luigi_tasks.py ParsingTask