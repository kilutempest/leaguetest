# Royal Road Chapter Uploader

Small Flask app that lets you upload chapter `.html` files and automates posting them to Royal Road.

## Features

- Upload multiple `.html` chapter files at once.
- Chapters are sorted by filename (e.g., `001.html`, `002.html`, ...).
- Extracts chapter title from `<title>`, then `<h1>`, then filename fallback.
- Optional **Dry run** to validate parsing without posting.
- Optional **Publish immediately** checkbox.

## Requirements

- Python 3.10+
- A Royal Road author account with an existing fiction

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
```

## Run

```bash
python app.py
```

Open: <http://127.0.0.1:5000>

## How to use

1. Enter your Royal Road email/password.
2. Enter your fiction ID (from your fiction URL).
3. Upload one or more `.html` files.
4. Optional: select **Dry run** first.
5. Submit.

## Notes

- This automation depends on Royal Road page structure and may break if their UI changes.
- If login prompts extra verification (CAPTCHA/2FA), automation may fail and need manual completion.
- Keep file names zero-padded so chapter order is correct (`001`, `002`, `003`, ...).
