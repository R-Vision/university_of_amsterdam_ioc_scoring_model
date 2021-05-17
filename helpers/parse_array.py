from typing import List, Any


def parse_array(arr_str: str) -> List[Any]:
    arr = arr_str.strip()[1:-1]

    state = 'wait_quote'
    new_name = ''
    names = []

    for c in arr:
        if c == "'" and state == 'wait_quote':
            state = 'read_name'
            new_name = ''
        elif c == "'" and state == 'read_name':
            names.append(new_name)
            state = 'wait_quote'
        elif state == 'read_name':
            new_name += c
        else:
            pass

    return names
