import json
import os

"""
Load the file path as json, or raise a nicer exception if the file doesn't exist.
"""


def load_json(file_path):
    if not os.path.exists(file_path):
        raise Exception(f"Input file {file_path} does not exist")
    with open(file_path, "r") as input_file:
        return json.load(input_file)
