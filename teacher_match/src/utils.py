import json
import os


def load_json(file_path):
    if not os.path.exists(file_path):
        raise Exception(f"Input file {file_path} does not exist")
    with open(file_path, 'r') as input_file:
        return json.load(input_file)