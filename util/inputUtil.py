__author__ = 'jinkerjiang'

def raw_input_multi_line():
    global input_list, input_str
    input_list = []
    while True:
        input_str = raw_input(">")
        if input_str == "":
            break
        else:
            input_list.append(input_str)
    return input_list