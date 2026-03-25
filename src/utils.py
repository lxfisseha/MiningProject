def nest_dotted_form_data(form: dict):
    nested = {}

    for key, value in form.items():
        keys = key.split(".")
        current = nested

        for k in keys[:-1]:
            current = current.setdefault(k, {})

        current[keys[-1]] = value

    return nested
