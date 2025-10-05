import json


def read_file(file_path:str) -> str:
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    
    except FileNotFoundError:
        return "File not found" + file_path
    except Exception as e:
        return f"Error: {e}"


def write_jsonstr_to_file(file_path:str, content:str)->None:
    data_dict = json.loads(content)

    with open(file_path, 'w') as file:
        json.dump(data_dict, file, indent=4)
