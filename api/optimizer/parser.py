from __future__ import annotations

import re

from optimizer.models import Program, Statement


ASSIGNMENT_RE = re.compile(r"^(?P<target>[A-Za-z_]\w*)\s*=\s*(?P<expr>.+);$")
FOR_HEADER_RE = re.compile(
    r"for\s*\(\s*(?P<init>[^;]+);\s*(?P<condition>[^;]+);\s*(?P<update>[^)]+)\s*\)\s*\{"
)


def parse_program(source: str) -> Program:
    statements: list[Statement] = []
    index = 0
    line_no = 1

    while index < len(source):
        while index < len(source) and source[index].isspace():
            if source[index] == "\n":
                line_no += 1
            index += 1

        if index >= len(source):
            break

        statement_line = line_no

        if starts_for_statement(source, index):
            end = find_for_loop_end(source, index)
            block_text = source[index:end].strip()
            line_no += source[index:end].count("\n")
            index = end

            metadata = parse_for_metadata(block_text)
            statements.append(
                Statement(
                    kind="for_loop",
                    text=block_text,
                    line=statement_line,
                    metadata=metadata,
                )
            )
            continue

        end = source.find(";", index)
        if end == -1:
            end = len(source) - 1

        raw = source[index : end + 1]
        text = raw.strip()
        line_no += raw.count("\n")
        index = end + 1

        assignment = ASSIGNMENT_RE.match(text)
        if assignment:
            statements.append(
                Statement(
                    kind="assignment",
                    text=text,
                    line=statement_line,
                    target=assignment.group("target"),
                    expression=assignment.group("expr").strip(),
                )
            )
        else:
            statements.append(Statement(kind="unknown", text=text, line=statement_line))

    return Program(source=source, statements=statements)


def starts_for_statement(source: str, index: int) -> bool:
    return (
        source.startswith("for", index)
        and (index == 0 or not is_identifier_char(source[index - 1]))
        and (index + 3 >= len(source) or not is_identifier_char(source[index + 3]))
    )


def is_identifier_char(char: str) -> bool:
    return char.isalnum() or char == "_"


def find_for_loop_end(source: str, start: int) -> int:
    open_brace = source.find("{", start)
    if open_brace == -1:
        semicolon = source.find(";", start)
        return len(source) if semicolon == -1 else semicolon + 1

    brace_balance = 0
    for index in range(open_brace, len(source)):
        if source[index] == "{":
            brace_balance += 1
        elif source[index] == "}":
            brace_balance -= 1
            if brace_balance == 0:
                return index + 1

    return len(source)


def parse_for_metadata(block_text: str) -> dict[str, str]:
    compact = " ".join(line.strip() for line in block_text.splitlines())
    header = FOR_HEADER_RE.search(compact)
    if not header:
        return {}

    body = compact[header.end() :].rsplit("}", 1)[0].strip()
    return {
        "init": header.group("init").strip(),
        "condition": header.group("condition").strip(),
        "update": header.group("update").strip(),
        "body": body,
    }