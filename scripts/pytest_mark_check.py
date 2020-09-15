import ast
import json
import os
import sys


def check_for_decorator(filename, m):
    with open(filename, "r") as source:
        tree = ast.parse(source.read())
        fails = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                valid_decorator = False
                for d in node.decorator_list:
                    if has_valid_pytest_mark_decorator(d):
                        valid_decorator = True
                        if isinstance(d, ast.Attribute):
                            m.add(d.attr)
                        break

                if not valid_decorator:
                    fails.append('{0} {1}:{2} missing @pytest.mark decorator'.format(filename, node.name, node.lineno))

        if len(fails) > 0:
            return fails


def flatten_list(in_list):
    flat_list = []
    for element in in_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


# the decorator is nested and we need to unpack it to see if the origin is pytest
# The format is <ast.Name.id>.<ast.Attribute.attr>.<ast.Attribute.attr>
#                      pytest.                mark.             example
# we start from the right side and move on 2
def has_valid_pytest_mark_decorator(d):
    return (isinstance(d, ast.Attribute) and isinstance(d.value,
                                                        ast.Attribute) and d.value.attr == 'mark' and isinstance(
        d.value.value, ast.Name)) or (isinstance(d, ast.Call) and d.func.attr == 'skip')


if __name__ == "__main__":
    errs = []
    matrix = set()
    for (root, dirs, files) in os.walk('{0}/test'.format(sys.argv[1]), topdown=True):
        path = root.split(os.sep)

        if os.path.basename(root) not in {'__pycache__'}:
            for file in files:
                if file.startswith('test_'):
                    res = check_for_decorator(root + os.sep + file, matrix)
                    if res is not None:
                        errs.append(res)

    out = {}
    if len(errs) > 0:
        out['status'] = "failed"
        out['errors'] = flatten_list(errs)
    else:
        out['status'] = "success"
        out['module'] = list(matrix)

    print(json.dumps(out))
