# AI-Assisted Code Optimization Compiler

A small teaching project that combines:

- Python heuristic optimization rules
- An HTML interface for trying optimization suggestions in the browser
- A Vercel-ready Python serverless endpoint

The runnable demo uses Python's standard library only.

## Features

- Detects simple inefficient loops and suggests direct formulas
- Performs constant folding for arithmetic expressions
- Replaces multiplication by powers of two with left shifts
- Recommends compound assignments such as `x += y`
- Detects overwritten assignments as dead-code candidates
- Reports basic static analysis metrics and per-pass optimization counts
- Returns optimization explanations and an estimated confidence score

## Project Structure

```text
api/
  optimize.py            Vercel serverless /optimize API
frontend/
  index.html             browser interface
  script.js              API client and rendering
  styles.css             UI styles
backend/
  app.py                 local HTTP server and /optimize API
  optimizer/
    engine.py            pipeline entrypoint
    parser.py            lightweight Python parser fallback
    analysis.py          static analysis metrics
    models.py            shared compiler data models
    passes/              pluggable optimization passes
vercel.json              Vercel build and route config
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

If port 8000 is already being used, the app automatically starts on the next
available port and prints the URL. You can still request a specific starting
port:

```powershell
python backend/app.py 8001
```

## Deploy To Vercel

Push this repository to GitHub, then import it from Vercel. Keep the project
root as the Vercel root directory.

Vercel uses:

- `frontend/` for static files
- `api/optimize.py` for the `/optimize` serverless function
- `backend/optimizer/` for the optimization engine imported by the API
- `vercel.json` for routing

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
