from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from chapter_parser import ParsedChapter


@dataclass
class UploadResult:
    title: str
    success: bool
    detail: str


class RoyalRoadUploader:
    def __init__(self, *, headless: bool = True):
        self.headless = headless

    def upload_chapters(
        self,
        *,
        email: str,
        password: str,
        fiction_id: str,
        chapters: Iterable[ParsedChapter],
        publish_immediately: bool,
    ) -> List[UploadResult]:
        results: List[UploadResult] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                self._login(page, email, password)

                for chapter in chapters:
                    result = self._upload_single_chapter(
                        page,
                        fiction_id=fiction_id,
                        chapter=chapter,
                        publish_immediately=publish_immediately,
                    )
                    results.append(result)
            finally:
                browser.close()

        return results

    def _login(self, page, email: str, password: str) -> None:
        page.goto("https://www.royalroad.com/account/login", wait_until="domcontentloaded")

        page.get_by_label("Email").fill(email)
        page.get_by_label("Password").fill(password)
        page.get_by_role("button", name="Login").click()

        try:
            page.wait_for_url("**/home", timeout=15_000)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError(
                "Login may have failed. Royal Road might require CAPTCHA/2FA/manual verification."
            ) from exc

    def _upload_single_chapter(self, page, *, fiction_id: str, chapter: ParsedChapter, publish_immediately: bool) -> UploadResult:
        try:
            page.goto(
                f"https://www.royalroad.com/author-dashboard/fiction/{fiction_id}/chapters/new",
                wait_until="domcontentloaded",
            )

            page.get_by_label("Chapter Title").fill(chapter.title)

            editor = page.locator("textarea[name='Text'], [contenteditable='true']").first
            editor.click()
            editor.fill(chapter.html_content)

            if publish_immediately:
                page.get_by_label("Publish Now").check()

            page.get_by_role("button", name="Publish Chapter").click()
            page.wait_for_timeout(1500)

            return UploadResult(title=chapter.title, success=True, detail="Uploaded")
        except Exception as exc:
            return UploadResult(title=chapter.title, success=False, detail=str(exc))
