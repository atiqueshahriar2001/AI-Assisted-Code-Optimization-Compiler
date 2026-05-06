from __future__ import annotations

import re
from typing import Any

from .models import Program, Statement


class CParser:
    def __init__(self):
        self.statements: list[Statement] = []
        self.functions: dict[str, dict] = {}
        self.current_func: str = ""
        self.line_no: int = 1
    
    def parse(self, source: str) -> Program:
        self.statements = []
        self.functions = {}
        lines = source.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                i += 1
                self.line_no += 1
                continue
            
            if self.is_function_definition(stripped):
                block_end = self.find_block_end(lines, i)
                block_text = '\n'.join(lines[i:block_end + 1])
                metadata = self.parse_function_definition(block_text)
                self.statements.append(Statement(
                    kind='function_definition',
                    text=block_text,
                    line=self.line_no,
                    metadata=metadata
                ))
                if 'name' in metadata:
                    self.functions[metadata['name']] = metadata
                if metadata.get('body'):
                    body_lines = metadata['body'].split('\n')
                    self.parse_function_body(body_lines, self.line_no + 1)
                i = block_end + 1
                self.line_no += block_text.count('\n')
                continue
            
            for_match = re.search(r'\bfor\s*\(', stripped)
            while_match = re.search(r'\bwhile\s*\(', stripped)
            if_match = re.search(r'\bif\s*\(', stripped)
            
            if for_match or while_match or if_match:
                block_end = self.find_block_end(lines, i)
                block_text = '\n'.join(lines[i:block_end + 1])
                stmt_type, metadata = self.parse_c_block(stripped, block_text)
                self.statements.append(Statement(
                    kind=stmt_type,
                    text=block_text,
                    line=self.line_no,
                    metadata=metadata
                ))
                i = block_end + 1
                self.line_no += block_text.count('\n')
                continue
            
            if stripped.endswith(';') or self.is_declaration(stripped):
                parsed = self.parse_c_statement(stripped, self.line_no)
                self.statements.append(parsed)
                i += 1
                self.line_no += 1
                continue
            
            i += 1
            self.line_no += 1
        
        return Program(source=source, statements=self.statements)
    
    def is_function_definition(self, line: str) -> bool:
        return bool(re.match(r'^(?:int|void|float|double|char|long|short|unsigned|signed)\s+\w+\s*\([^)]*\)\s*\{', line))
    
    def is_declaration(self, line: str) -> bool:
        return bool(re.match(r'^(?:int|void|float|double|char|long|short|unsigned|signed)\s+\w+\s*(?:=\s*.*\s*)?;?$', line))
    
    def is_control_structure(self, line: str) -> bool:
        return (line.startswith('for(') or line.startswith('for ') or 
                line.startswith('while(') or line.startswith('while ') or
                line.startswith('if(') or line.startswith('if '))
    
    def find_block_end(self, lines: list[str], start: int) -> int:
        brace_count = 0
        started = False
        for i in range(start, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1
                    if started and brace_count == 0:
                        return i
        return start
    
    def parse_function_body(self, body_lines: list[str], start_line: int) -> None:
        i = 0
        line_no = start_line
        while i < len(body_lines):
            line = body_lines[i]
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                i += 1
                line_no += 1
                continue

            for_match = re.search(r'\bfor\s*\(', stripped)
            while_match = re.search(r'\bwhile\s*\(', stripped)
            if_match = re.search(r'\bif\s*\(', stripped)

            if for_match or while_match or if_match:
                block_end = self.find_block_end(body_lines, i)
                block_text = '\n'.join(body_lines[i:block_end + 1])
                stmt_type, metadata = self.parse_c_block(stripped, block_text)
                self.statements.append(Statement(
                    kind=stmt_type,
                    text=block_text,
                    line=line_no,
                    metadata=metadata
                ))
                i = block_end + 1
                line_no += block_text.count('\n') + 1
                continue

            if stripped.endswith(';') or self.is_declaration(stripped):
                parsed = self.parse_c_statement(stripped, line_no)
                self.statements.append(parsed)

            i += 1
            line_no += 1
    
    def parse_c_block(self, first_line: str, block_text: str) -> tuple[str, dict]:
        for_match = re.search(r'\bfor\s*\(', first_line)
        while_match = re.search(r'\bwhile\s*\(', first_line)
        if_match = re.search(r'\bif\s*\(', first_line)
        
        if for_match:
            return self.parse_for_loop(block_text)
        if while_match:
            return 'while_loop', {'condition': self.extract_condition(first_line)}
        if if_match:
            return 'if_statement', {'condition': self.extract_condition(first_line)}
        
        return 'compound_block', {}
    
    def parse_function_definition(self, block_text: str) -> dict:
        lines = block_text.split('\n')
        last_line_idx = len(lines) - 1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == '}':
                last_line_idx = i
                break
        
        body_lines = lines[1:last_line_idx]
        body_text = '\n'.join(body_lines)
        
        first_line = lines[0].strip()
        match = re.match(r'^(?P<return_type>int|void|float|double|char|long|short)\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)', first_line)
        if match:
            return {
                'name': match.group('name'),
                'return_type': match.group('return_type'),
                'params': match.group('params'),
                'body': body_text
            }
        return {}
    
    def parse_for_loop(self, block_text: str) -> tuple[str, dict]:
        compact = ' '.join(line.strip() for line in block_text.splitlines())
        header_match = re.search(r'for\s*\(\s*([^;]+);\s*([^;]+);\s*([^)]+)\s*\)', compact)
        
        if not header_match:
            return 'for_loop', {}
        
        init = header_match.group(1).strip()
        condition = header_match.group(2).strip()
        update = header_match.group(3).strip()
        
        body_match = re.search(r'\)\s*\{(.+)\}', compact, re.DOTALL)
        body = body_match.group(1).strip() if body_match else ''
        
        return 'for_loop', {
            'init': init,
            'condition': condition,
            'update': update,
            'body': body
        }
    
    def extract_condition(self, line: str) -> str:
        match = re.search(r'\(([^)]+)\)', line)
        return match.group(1).strip() if match else ''
    
    def parse_c_statement(self, text: str, line_no: int) -> Statement:
        text = text.rstrip(';')
        
        if text.startswith('return '):
            return Statement(
                kind='return',
                text=text + ';',
                line=line_no,
                expression=text[7:].strip()
            )
        
        decl_match = re.match(r'^(?:int|void|float|double|char|long|short)\s+([A-Za-z_]\w*)\s*(?:=\s*(.*))?$', text)
        if decl_match:
            target = decl_match.group(1)
            expr = decl_match.group(2) or ''
            if expr:
                return Statement(
                    kind='assignment',
                    text=text + ';',
                    line=line_no,
                    target=target,
                    expression=expr.strip()
                )
            return Statement(
                kind='declaration',
                text=text + ';',
                line=line_no,
                target=target,
            )
        
        assign_match = re.match(r'^([A-Za-z_]\w*)\s*=\s*(.+)$', text)
        if assign_match:
            target = assign_match.group(1)
            expr = assign_match.group(2).strip()
            return Statement(
                kind='assignment',
                text=text + ';',
                line=line_no,
                target=target,
                expression=expr
            )
        
        func_call_match = re.match(r'^([A-Za-z_]\w*)\s*\(([^)]*)\)$', text)
        if func_call_match:
            return Statement(
                kind='function_call',
                text=text + ';',
                line=line_no,
                target=func_call_match.group(1),
                expression=func_call_match.group(2)
            )
        
        return Statement(kind='unknown', text=text + ';', line=line_no)


def parse_c_code(source: str) -> Program:
    parser = CParser()
    return parser.parse(source)


def generate_c_code(program: Program) -> str:
    lines = []
    for stmt in program.statements:
        lines.extend(generate_statement(stmt))
    return '\n'.join(lines)


def generate_statement(stmt: Statement) -> list[str]:
    if stmt.kind == 'for_loop' and stmt.metadata:
        meta = stmt.metadata
        init = meta.get('init', '')
        cond = meta.get('condition', '')
        upd = meta.get('update', '')
        body = meta.get('body', '')
        lines = [f"for ({init}; {cond}; {upd}) {{"]
        if body:
            lines.append(f"    {body};")
        lines.append("}")
        return lines
    elif stmt.kind == 'assignment':
        return [stmt.text]
    elif stmt.kind == 'declaration':
        return [stmt.text]
    elif stmt.kind == 'function_call':
        return [stmt.text]
    elif stmt.kind == 'return':
        return [stmt.text]
    elif stmt.kind == 'function_definition' and stmt.metadata:
        meta = stmt.metadata
        return [f"{meta.get('return_type', 'int')} {meta.get('name', 'func')}() {{", "    // function body", "}"]
    elif stmt.kind == 'compound_block':
        return ['{', '    // compound block', '}']
    return [stmt.text]