from backend.optimizer.c_parser import parse_c_code
code = 'sum = 0; for (i = 1; i <= n; i = i + 1) { sum = sum + i; }'
p = parse_c_code(code)
print('Statements:', len(p.statements))
for s in p.statements:
    text_preview = s.text[:50] if s.text else 'empty'
    print(f'  {s.kind}: {text_preview}...')