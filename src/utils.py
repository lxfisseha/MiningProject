from typing import Dict, Any

def nest_dotted_form_data(form: Dict[str, Any]) -> Dict[str, Any]:
    nested = {}

    for key, value in form.items():
        keys = key.split(".")
        current = nested

        for k in keys[:-1]:
            current = current.setdefault(k, {})

        current[keys[-1]] = value

    return nested
