# AI-Assisted Code Optimization Compiler

A powerful code optimization tool that transforms real C code using advanced optimization techniques.

## Features

- **Loop Pattern Recognition**: Replaces summation loops with closed-form formulas (e.g., `1+2+...+n` → `n*(n+1)/2`)
- **Loop Unrolling**: Unrolls simple counted loops to eliminate loop overhead
- **Constant Folding**: Evaluates constant expressions at compile time
- **Strength Reduction**: Replaces multiplication by powers of 2 with bit shifts
- **Common Subexpression Elimination**: Detects and eliminates redundant computations
- **Dead Code Elimination**: Removes overwritten assignments
- **Function Inlining**: Inlines simple functions to eliminate call overhead
- **Algebraic Simplifications**: Applies mathematical identities to simplify expressions
- **Static Analysis**: Reports complexity metrics and hot identifiers

## Installation

```bash
pip install -r requirements.txt
```

## Run Locally

```powershell
python backend/app.py
```

Open `http://localhost:8000`

## Example Input (C Code)

```c
int main() {
    int sum = 0;
    for (int i = 1; i <= n; i++) {
        sum = sum + i;
    }
    int x = 4 * 8;
    int y = y + 0;
    int z = z * 8;
    int temp = 10;
    temp = 20;
    return 0;
}
```

## Example Output

```c
int main() {
    sum = (n * (n + 1)) / 2;  // Closed-form formula
    x = 8;                    // Constant folding
    y = y;                    // Dead code or simplified
    z = z << 3;               // Strength reduction
    temp = 20;                // Dead assignment removed
    return 0;
}
```

## API Usage

```python
from backend.optimizer.engine import optimize_code

result = optimize_code("""
int main() {
    int sum = 0;
    for (int i = 1; i <= 100; i++) {
        sum = sum + i;
    }
    return 0;
}
""")
print(result['optimized_code'])
```

## Deployment

### Render

1. Create a [Render](https://render.com) account
2. Connect your GitHub repository
3. Create a new **Web Service** with these settings:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend/app.py`
   - **Environment**: PORT=10000

## Project Structure

```text
backend/
  app.py                 HTTP server and /optimize API
  optimizer/
    engine.py            pipeline entrypoint
    c_parser.py          C code parser
    analysis.py          static analysis metrics
    models.py            shared compiler data models
    codegen.py           C code generator
    passes/              optimization passes
      constant_folding.py
      dead_code.py
      loop_patterns.py
      strength_reduction.py
      syntax_simplification.py
      function_inlining.py
      loop_unrolling.py
      cse.py
      algebraic.py
frontend/
  index.html             browser interface
  script.js              API client and rendering
  styles.css             UI styles
requirements.txt         dependencies (pycparser)
```

## Optimization Passes

| Pass | Description | Impact |
|------|-------------|--------|
| loop_patterns | Recognizes summation loops, replaces with formulas | High |
| loop_unrolling | Unrolls small loops | High |
| constant_folding | Evaluates constant expressions | Medium |
| strength_reduction | Power-of-2 mult → bit shifts | Medium |
| function_inlining | Inlines simple functions | Medium |
| dead_code_detection | Removes overwritten assignments | Medium |
| cse | Common subexpression elimination | Medium |
| algebraic_simplification | Mathematical identities | Low |