from typing import Dict, List, Union


def ensure_list_of_dicts(data: Union[Dict, List[Dict]]) -> List[Dict]:
    """
    Ensures that the input data is converted to a list of dictionaries.

    If the input is a single dictionary, it is wrapped in a list. If the input is a list of dictionaries,
    it is returned as-is.

    Args:
        data (Union[Dict, List[Dict]]): The input data to be converted.

    Returns:
        List[Dict]: A list of dictionaries.
    """
    if isinstance(data, dict):
        return [data]
    elif not isinstance(data, list):
        raise TypeError(
            f"Input must be a non-empty list of dictionaries or a single dictionary. Received {type(data)}."
        )
    elif len(data) == 0:
        raise ValueError(
            "Input must be a non-empty list of dictionaries or a single dictionary. Received an empty list."
        )
    return data
