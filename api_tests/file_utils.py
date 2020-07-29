import os
import json

OUTPUT_FOLDER = './output'

def save_json_to_file(output, filename):
    create_folder_if_not_present(OUTPUT_FOLDER)

    filepath = f'{OUTPUT_FOLDER}/{filename}'

    with open(filepath, 'w+') as file:
        json.dump(output, file, indent=4)

    return filepath

def read_json_from_file(filename):
    with open(f'{OUTPUT_FOLDER}/{filename}', 'r') as file:
        return json.load(file)

def save_file(data, filename):
    filepath = f'{OUTPUT_FOLDER}/{filename}'

    with open(filepath, 'w+') as file:
        file.write(data)

    return filepath

def create_folder_if_not_present(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)