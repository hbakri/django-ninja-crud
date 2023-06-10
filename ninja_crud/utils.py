import re


# TODO: remove this file by putting the functions in the abstract view
def to_snake_case(name: str, separator: str = "_"):
    return re.sub(r"(?<!^)(?=[A-Z])", separator, name).lower()


def merge_decorators(decorators):
    def merged_decorator(func):
        for decorator in reversed(decorators):
            func = decorator(func)
        return func

    return merged_decorator
