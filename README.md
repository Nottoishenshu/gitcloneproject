# EscapeX mygit Project

This repository contains a minimal Git-like learning project implemented in Python.

## What is included

- `mygit.py` — a small Python implementation of key Git object operations
- `README_mygit.md` — detailed usage documentation for the `mygit` tool
- `docs/index.html` — a simple demo page that can be published with GitHub Pages

## How to publish a demo URL

1. Create a GitHub repository from this project.
2. Add, commit, and push the code:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

3. Enable GitHub Pages in the repository settings.
   - Choose the `main` branch and the `/docs` folder as the source.

4. Your demo URL will become:

```text
https://<YOUR_USERNAME>.github.io/<YOUR_REPO>/
```

## Local preview

To preview the demo page locally:

```bash
cd docs
python -m http.server 8000
```

Then open `http://localhost:8000` in a browser.
