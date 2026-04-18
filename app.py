from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from flask import Flask, render_template, request

from chapter_parser import ParsedChapter, parse_chapter_html
from royalroad_uploader import RoyalRoadUploader, UploadResult

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


@dataclass
class UploadRequest:
    email: str
    password: str
    fiction_id: str
    publish_immediately: bool
    dry_run: bool


def _read_uploaded_chapters() -> List[ParsedChapter]:
    files = request.files.getlist("chapter_files")
    chapters: List[ParsedChapter] = []

    for file in files:
        if not file.filename:
            continue

        if not file.filename.lower().endswith(".html"):
            raise ValueError(f"{file.filename} is not an HTML file.")

        raw = file.stream.read()
        html = raw.decode("utf-8", errors="replace")
        parsed = parse_chapter_html(file.filename, html)
        chapters.append(parsed)

    if not chapters:
        raise ValueError("Please upload at least one .html chapter file.")

    chapters.sort(key=lambda c: c.filename.lower())
    return chapters


def _parse_form() -> UploadRequest:
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    fiction_id = request.form.get("fiction_id", "").strip()

    if not email:
        raise ValueError("Email is required.")
    if not password:
        raise ValueError("Password is required.")
    if not fiction_id:
        raise ValueError("Fiction ID is required.")

    return UploadRequest(
        email=email,
        password=password,
        fiction_id=fiction_id,
        publish_immediately=(request.form.get("publish_immediately") == "on"),
        dry_run=(request.form.get("dry_run") == "on"),
    )


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload():
    try:
        upload_request = _parse_form()
        chapters = _read_uploaded_chapters()

        uploader = RoyalRoadUploader(headless=(os.getenv("HEADLESS", "true").lower() == "true"))

        if upload_request.dry_run:
            fake_results = [
                UploadResult(title=ch.title, success=True, detail="Dry run: validated chapter data.")
                for ch in chapters
            ]
            return render_template(
                "index.html",
                success=True,
                message="Dry run completed. No chapters were uploaded.",
                results=fake_results,
            )

        results = uploader.upload_chapters(
            email=upload_request.email,
            password=upload_request.password,
            fiction_id=upload_request.fiction_id,
            chapters=chapters,
            publish_immediately=upload_request.publish_immediately,
        )

        all_success = all(r.success for r in results)
        message = "All chapters uploaded successfully." if all_success else "Some chapters failed to upload."

        return render_template("index.html", success=all_success, message=message, results=results)

    except Exception as exc:
        return render_template("index.html", success=False, message=str(exc), results=[])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
