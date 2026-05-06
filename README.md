# AI-Assisted Code Optimization Compiler

A small teaching project that combines:

- Python heuristic optimization rules
- An HTML interface for trying optimization suggestions in the browser

The runnable demo uses Python's standard library only.

## Features

- Detects simple inefficient loops and suggests direct formulas
- Performs constant folding for arithmetic expressions
- Replaces multiplication by powers of two with left shifts
- Recommends compound assignments such as `x += y`
- Detects overwritten assignments as dead-code candidates
- Reports basic static analysis metrics and per-pass optimization counts
- Returns optimization explanations and an estimated confidence score

## Installation

Clone the repository:

```bash
git clone https://github.com/atiqueshahriar2001/AI-Assisted-Code-Optimization-Compiler.git
cd AI-Assisted-Code-Optimization-Compiler
```

No additional dependencies are required as the project uses only Python's standard library.

## Project Structure

```text
backend/
  app.py                 local HTTP server and /optimize API
  optimizer/
    engine.py            pipeline entrypoint
    parser.py            lightweight Python parser fallback
    analysis.py          static analysis metrics
    models.py            shared compiler data models
    passes/              pluggable optimization passes
frontend/
  index.html             browser interface
  script.js              API client and rendering
  styles.css             UI styles
requirements.txt         Python dependency marker
```

## Run Locally

```powershell
python backend/app.py
```

Open:

```text
http://localhost:8000
```

## Example Input

```c
sum = 0;
for (i = 1; i <= n; i = i + 1) {
    sum = sum + i;
}
x = 4 * 8;
y = y + total;
z = value * 8;
temp = 10;
temp = 20;
```

## Deployment

### Render

1. Create a [Render](https://render.com) account
2. Connect your GitHub repository
3. Create a new **Web Service** with these settings:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt` (or leave blank if no dependencies)
   - **Start Command**: `python backend/app.py`
   - **Region**: Your preferred region
   - **Plan**: Free (or higher)
4. Add environment variable `PORT` with the value `10000` (Render's default port)
5. Deploy!

The app will be available at `https://your-service-name.onrender.com`