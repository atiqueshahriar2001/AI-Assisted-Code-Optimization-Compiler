from __future__ import annotations

from .models import Program, Statement


def generate_c_from_ast(program: Program) -> str:
    lines = []
    indent = 0
    
    i = 0
    while i < len(program.statements):
        stmt = program.statements[i]
        
        if stmt.kind == 'function_definition' and stmt.metadata:
            meta = stmt.metadata
            name = meta.get('name', 'func')
            ret_type = meta.get('return_type', 'int')
            params = meta.get('params', '')
            body = meta.get('body', '')
            
            lines.append(f"{ret_type} {name}({params}) {{")
            
            body_statements = parse_body_statements(body, indent + 1)
            for bl in body_statements:
                lines.append(bl)
            
            lines.append("}")
            i += 1
        else:
            lines.extend(generate_statement(stmt, indent))
            i += 1
    
    return '\n'.join(lines)


def parse_body_statements(body: str, indent: int) -> list[str]:
    lines = []
    for line in body.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('//') and not stripped == '}':
            lines.append("    " * indent + stripped)
    return lines


def format_optimized_code(source: str) -> str:
    lines = []
    indent = 0
    
    for line in source.split('\n'):
        stripped = line.strip()
        
        if not stripped:
            continue
            
        if stripped.endswith('{'):
            lines.append("    " * indent + stripped)
            indent += 1
        elif stripped == '}':
            indent = max(0, indent - 1)
            lines.append("    " * indent + stripped)
        else:
            lines.append("    " * indent + stripped)
    
    return '\n'.join(lines)


def generate_statement(stmt: Statement, indent: int) -> list[str]:
    prefix = "    " * indent
    
    if stmt.kind == 'for_loop' and stmt.metadata:
        meta = stmt.metadata
        init = meta.get('init', '')
        cond = meta.get('condition', '')
        upd = meta.get('update', '')
        body = meta.get('body', '')
        lines = [f"{prefix}for ({init}; {cond}; {upd}) {{"]
        if body:
            lines.append(f"{prefix}    {body};")
        lines.append(f"{prefix}}}")
        return lines
    elif stmt.kind == 'assignment':
        return [f"{prefix}{stmt.text}"]
    elif stmt.kind == 'declaration':
        return [f"{prefix}{stmt.text}"]
    elif stmt.kind == 'function_call':
        return [f"{prefix}{stmt.text}"]
    elif stmt.kind == 'return':
        return [f"{prefix}{stmt.text}"]
    elif stmt.kind == 'if_statement':
        cond = stmt.metadata.get('condition', '') if stmt.metadata else ''
        return [f"{prefix}if ({cond}) {{", f"{prefix}}}"]
    elif stmt.kind == 'compound_block':
        return [f"{prefix}{{", f"{prefix}}}"]
    return [f"{prefix}{stmt.text}"]