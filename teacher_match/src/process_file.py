import json

from teacher_match.src.core import match_teachers_to_principals
from teacher_match.src.utils import load_json


def process_file(input_file_path, output_file_path):
    data = load_json(input_file_path)
    results = match_teachers_to_principals(data)
    with open(output_file_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)
