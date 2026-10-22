# feature: version_specific
# summary: PEP 701 f-strings: reused quotes, backslashes and multi-line expressions inside replacement fields
# requires: >=3.12


def observe():
    items = ['a', 'b']
    data = {'key': 'value'}
    return [
        f"{"nested same quotes"}",
        f"{data["key"]}",
        f"{'\n'.join(items)}",
        f"{
            len(items)
            + 1
        }",
        f"{f"{f"{1 + 1}"}"}",
        f"{', '.join(f"<{x}>" for x in items)}",
    ]
