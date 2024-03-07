import re

pascal_to_snake_case = lambda s: re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
