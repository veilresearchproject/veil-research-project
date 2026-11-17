"""Check the Research Library in Chromium at desktop and phone widths."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

REPO = Path(__file__).resolve().parents[2]
ENTRY = {
    "id": "VEIL-IR-2026-001", "title": "<b>Synthetic temperature fixture</b>",
    "summary": "Controlled bench test", "classification": "Explained",
    "publication_date": "2026-11-16", "status": "published",
    "report_url": "reports/fixture.v1.pdf", "topics": ["Sensor Trace"], "review_version": "1",
}
FIXTURES = [
    ENTRY,
    dict(ENTRY, id="VEIL-IR-2026-002", title="Synthetic audio fixture", classification="Inconclusive"),
    dict(ENTRY, title="Draft fixture", status="draft"),
    dict(ENTRY, title="Offsite fixture", report_url="//example.invalid/report.pdf"),
    None,
]


class CatalogPreview(SimpleHTTPRequestHandler):
    def do_GET(self):
        routes = {
            "/research-library/": "/research-library/index.html",
            "/research-library/cases.json": "/research-library/cases.json",
            "/research-library/catalog.js": "/research-library/catalog.js",
            "/styles.css": "/styles.css",
            "/mtc/": "/mtc/index.html",
            "/temperature-curtain/": "/temperature-curtain/index.html",
            "/echo/": "/echo/index.html",
            "/evidence-review/": "/evidence-review/index.html",
        }
        if self.path in routes:
            self.path = routes[self.path]
            super().do_GET()
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


def check_page(page, base, width):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base + "/research-library/")
    page.get_by_text("No VEIL investigation reports have been published yet.").wait_for()
    assert page.locator("input[type=file]").count() == 0
    assert page.evaluate("document.documentElement.scrollWidth") <= width
    for path in ("mtc", "temperature-curtain", "echo", "evidence-review"):
        link = page.locator(f'a[href="../{path}/"]')
        target = link.evaluate("(link) => link.href")
        assert page.request.get(target).ok, path

    page.route("**/cases.json", lambda route: route.fulfill(
        json={"schema_version": "1.0", "cases": FIXTURES}))
    page.reload()
    page.get_by_text("2 matching reports.", exact=True).wait_for()
    page.get_by_text("<b>Synthetic temperature fixture</b>", exact=False).wait_for()
    assert page.locator("#case-results b").count() == 0
    assert page.get_by_text("Version 1", exact=False).count() == 2
    assert page.evaluate("document.documentElement.scrollWidth") <= width

    page.get_by_label("Finding", exact=True).select_option("Explained")
    page.get_by_text("1 matching report.", exact=True).wait_for()
    page.get_by_label("Search published cases").fill("sensor trace")
    page.get_by_text("1 matching report.", exact=True).wait_for()
    page.get_by_label("Search published cases").fill("no-match")
    page.get_by_text("No published cases match your filters.").wait_for()

    page.unroute("**/cases.json")
    page.route("**/cases.json", lambda route: route.fulfill(status=503))
    page.reload()
    page.get_by_text("The case catalog is temporarily unavailable.").wait_for()
    assert not errors, errors


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--chromium", type=Path, help="Path to Chromium or a compatible desktop browser")
    cli.add_argument("--preview", action="store_true", help="Start a manual desktop preview without Playwright")
    args = cli.parse_args()
    handler = partial(CatalogPreview, directory=REPO)
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        base = f"http://127.0.0.1:{server.server_port}"
        if args.preview:
            print(f"{base}/research-library/", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            return
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            cli.error("For the automated checks, use an environment with Playwright. For a manual check, use --preview.")
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=args.chromium)
                for width in (320, 390, 1440):
                    page = browser.new_page(viewport={"width": width, "height": 900})
                    check_page(page, base, width)
                    page.close()
                    print(f"PASS: catalog browser checks at {width} px")
                browser.close()
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
