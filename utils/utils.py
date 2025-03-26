import json
import os
from datetime import datetime
from typing import Optional, Dict, Union

from bson import ObjectId


def get_prompt_file(script_dir, file_name):
    file_path = os.path.join(script_dir, "prompts", file_name)

    with open(file_path, "r") as file:
        return file.read()


def escape_curly_braces(query):
    return query.replace("{", "{{").replace("}", "}}")


def prepare_mongo_query_from_str(llm_response):
    cleaned_response = llm_response.strip('```json').strip('```')
    cleaned_response = preprocess_query(cleaned_response)
    return prepare_query_with_types(cleaned_response)


def preprocess_query(query):
    query = json.loads(query)

    # Locate and replace `$date`
    def replace_date_fields(obj):
        # If obj is a `$date` field, convert it to a Python datetime
        if isinstance(obj, dict) and "$date" in obj:
            return datetime.fromisoformat(obj["$date"].replace("Z", "+00:00"))  # ISO 8601 to datetime
        # If obj is a dict, process its key-value pairs
        elif isinstance(obj, dict):
            return {key: replace_date_fields(value) for key, value in obj.items()}
        # If obj is a list, process each element
        elif isinstance(obj, list):
            return [replace_date_fields(item) for item in obj]

        # If obj is any other type, return it as is
        else:
            return obj

    return replace_date_fields(query)


def wrap_with_objectid(id_list):
    return [ObjectId(id_str) for id_str in id_list]


def format_results_to_text(results):
    text = ""
    for idx, result in enumerate(results, 1):
        text += f"Result {idx}:\n"
        for key, value in result.items():
            text += f"  - {key}: {value}\n"
        text += "\n"
    if not text.strip():
        return ""
    return ''.join(("Here are the results:\n\n", text))


def dict_to_string(input_dict: Optional[Dict[str, Union[str, bool, int]]]) -> str:
    """
    Convert an optional dictionary to a readable string representation.
    Handles both dictionaries with string-only values and mixed-type values.

    Args:
        input_dict (Optional[Dict[str, Union[str, bool, int]]]): The dictionary to convert.

    Returns:
        str: A string representation of the dictionary, or an empty string if None.
    """
    if not input_dict:
        return ""  # Return an empty string if the dictionary is None or empty

    # Convert each value to string and join the key-value pairs
    return ", ".join(f"{key}: {str(value)}" for key, value in input_dict.items())


def prepare_query_with_types(query):
    if isinstance(query, list):  # Check if the query itself is a list
        # Process each item in the list
        return [ObjectId(item) if isinstance(item, str) and len(item) == 24 and item.isalnum() else prepare_query_with_types(item) for item in query]

    if isinstance(query, dict):  # Process dictionaries
        for key, value in query.items():
            if isinstance(value, dict):  # Recursive call for nested dictionaries
                query[key] = prepare_query_with_types(value)
            elif isinstance(value, list):  # Recursive call for lists
                query[key] = [ObjectId(item) if isinstance(item, str) and len(item) == 24 and item.isalnum() else prepare_query_with_types(item) for item in value]
            elif isinstance(value, str):
                # Convert string dates to datetime objects
                if value.endswith("Z"):
                    try:
                        query[key] = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except ValueError:
                        pass
                # Convert ObjectId strings to ObjectId objects
                if len(value) == 24 and value.isalnum():
                    try:
                        query[key] = ObjectId(value)
                    except Exception:
                        pass
    return query