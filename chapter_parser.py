from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class ParsedChapter:
    filename: str
    title: str
    html_content: str


def parse_chapter_html(filename: str, html: str) -> ParsedChapter:
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    if soup.title and soup.title.text:
        title = soup.title.text.strip()

    if not title:
        h1 = soup.find("h1")
        if h1 and h1.text:
            title = h1.text.strip()

    if not title:
        title = filename.rsplit(".", 1)[0]

    body = soup.body
    content = str(body) if body else html

    return ParsedChapter(filename=filename, title=title, html_content=content)
