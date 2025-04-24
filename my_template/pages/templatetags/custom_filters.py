from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary safely."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def sum_wbs_lot_turns(table_data, wbs):
    """Sum the lot turns for a specific WBS across all years in the table_data."""
    total = 0
    for year, data in table_data.items():
        total += float(data.get(wbs, 0))
    return total


@register.filter
def add(value, arg):
    """Adds the arg to the value."""
    return value + arg

@register.filter
def sum_values(dictionary):
    """Returns the sum of values in a dictionary."""
    return sum(dictionary.values())

@register.filter
def sum_values(nested_dict):
    """Recursively sums the values in a nested dictionary."""
    total = 0
    for value in nested_dict.values():
        if isinstance(value, dict):  # If the value is another dictionary, sum its values
            total += sum_values(value)
        else:
            total += value
    return total

@register.filter
def get_dict_value(dictionary, key):
    """Returns the value from a dictionary safely"""
    return dictionary.get(key, "0.00") if dictionary else "0.00"  

@register.filter(name="get_dict_value")
def get_dict_value(dictionary, key):
    """Returns dictionary value for the given key, or 0 if key doesn't exist."""
    return dictionary.get(key, 0.00)
