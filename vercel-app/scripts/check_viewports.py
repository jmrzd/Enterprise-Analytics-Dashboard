"""Headless smoke checks for responsive navigation, charts, overlays and Safari.

Run with:
  python -m playwright install chromium webkit
  python vercel-app/scripts/check_viewports.py --browser chromium

Use with a local FastAPI dev server at http://127.0.0.1:8765.
Emulation is NOT equivalent to real physical-device testing.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

CASES = [
    ("phone-small", 320, 690),
    ("iphone-se", 375, 667),
    ("iphone-regular", 390, 844),
    ("iphone-large", 430, 932),
    ("phone-landscape", 932, 430),
    ("tablet", 768, 1024),
    ("ipad", 834, 1194),
    ("ipad-landscape", 1024, 768),
    ("notebook", 1280, 800),
    ("desktop", 1440, 900),
    ("wide-monitor", 1920, 1080),
]


def assert_no_horizontal_overflow(page, name: str) -> None:
    metrics = page.evaluate(
        """() => ({
            width: window.innerWidth,
            document: document.documentElement.scrollWidth,
            body: document.body.scrollWidth
        })"""
    )
    if metrics["document"] > metrics["width"] + 4:
        raise AssertionError(f"{name}: document overflows horizontally: {metrics}")


def assert_visible_inside_screen(page, selector: str, name: str) -> None:
    loc = page.locator(selector)
    assert loc.is_visible(), f"{name}: hidden {selector}"
    box = loc.bounding_box()
    assert box, f"{name}: no box {selector}"
    h = page.evaluate("window.innerHeight")
    if box["x"] < -5 or box["x"] + box["width"] > page.viewport_size["width"] + 5:
        raise AssertionError(f"{name}: {selector} extends horizontally: {box}")
    if box["y"] < -8 or box["y"] + box["height"] > h + 12:
        raise AssertionError(f"{name}: {selector} extends vertically: {box}, viewport h={h}")


def check_mobile(page, name: str, width: int) -> None:
    bar = page.locator("#mobileBottomNav")
    assert bar.is_visible(), f"{name}: bottom navigation not visible"
    assert_visible_inside_screen(page, "#mobileBottomNav", name)

    for button in page.locator("#mobileBottomNav button").all():
        box = button.bounding_box()
        assert box and box["height"] >= 44, f"{name}: undersized touch target"

    page.locator("#menuToggle").click()
    assert page.locator("#sidebar").evaluate(
        "(e) => e.classList.contains('open')"
    ), f"{name}: sidebar did not open"
    assert page.locator("body").evaluate(
        "(e) => e.classList.contains('ea-menu-locked')"
    ), f"{name}: background was not locked"
    page.locator(".mobile-sidebar-close").click()
    assert not page.locator("#sidebar").evaluate(
        "(e) => e.classList.contains('open')"
    ), f"{name}: sidebar did not close"

    page.locator("#mobileBottomNav [data-mobile-id='sales']").click()
    page.wait_for_function(
        "document.getElementById('pageTitle').textContent.includes('Vendas')"
    )
    assert_no_horizontal_overflow(page, f"{name}-sales")

    # Verify the tabs can be swiped, without enlarging the whole viewport.
    if page.locator(".v2-tabs").count():
        assert page.locator(".v2-tabs").is_visible(), f"{name}: sub-tabs not visible"
        page.locator(".v2-tabs .v2-tab").last.click()
        page.wait_for_timeout(120)
        assert_no_horizontal_overflow(page, f"{name}-performance-tab")

    page.locator("#mobileBottomNav [data-mobile-id='integrations']").click()
    page.wait_for_function(
        "() => !document.getElementById('integrationPage').hidden"
    )
    assert page.locator("#integrationPage").is_visible(), f"{name}: integrations hidden"
    assert_no_horizontal_overflow(page, f"{name}-integrations")

    # Exercise a complete user-facing integration workflow without a real DB.
    page.locator("[data-next]").click()
    page.locator("[data-demo]").click()
    assert page.locator("#integrationPage [data-analyze]").is_visible()
    assert_no_horizontal_overflow(page, f"{name}-mapping")

    page.locator("#assistantLauncher").click()
    assert_visible_inside_screen(page, "#assistantPanel", name)
    # Open settings through the chatbot; no real API key is provided.
    page.locator("#aiSettingsShortcut").click()
    assert page.locator("#aiSettingsOverlay").is_visible()
    size = page.locator("#aiApiKey").evaluate(
        "(e) => Number.parseFloat(getComputedStyle(e).fontSize)"
    )
    assert size >= 16, f"{name}: iOS input text {size}px will auto-zoom"
    page.locator("#aiSettingsClose").click()
    page.locator("#assistantClose").click()
    assert_no_horizontal_overflow(page, f"{name}-after-overlays")


def check_desktop(page, name: str) -> None:
    assert not page.locator("#mobileBottomNav").is_visible()
    assert page.locator("#sidebar").is_visible()
    assert_no_horizontal_overflow(page, f"{name}-initial")
    page.locator('button.nav-item[data-view="sales"]').click()
    page.wait_for_function(
        "document.getElementById('pageTitle').textContent.includes('Vendas')"
    )
    assert_no_horizontal_overflow(page, f"{name}-sales")
    page.locator('button.nav-item[data-view="powerbi"]').click()
    page.wait_for_function("document.getElementById('v2Module').textContent.includes('Power BI')")
    assert_no_horizontal_overflow(page, f"{name}-powerbi")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=("chromium", "webkit"), default="chromium")
    args = parser.parse_args()
    base = os.getenv("DASHBOARD_TEST_URL", "http://127.0.0.1:8765/")
    failures = []
    screenshot_dir = Path("/tmp/ea-mobile-screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = getattr(playwright, args.browser).launch(headless=True)
        try:
            for name, width, height in CASES:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=2,
                    has_touch=width <= 960,
                    is_mobile=width <= 960,
                    reduced_motion="reduce",
                )
                # External Google Fonts may be unavailable on CI runners.
                # Test the dashboard itself without waiting on third-party CSS.
                context.route("https://fonts.googleapis.com/**", lambda route: route.abort())
                context.route("https://fonts.gstatic.com/**", lambda route: route.abort())
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                try:
                    page.goto(base, wait_until="domcontentloaded", timeout=12000)
                    page.locator(".metric-grid .metric").first.wait_for(timeout=8000)
                    page.wait_for_timeout(120)
                    assert_no_horizontal_overflow(page, f"{name}-home")
                    if width <= 960:
                        check_mobile(page, name, width)
                    else:
                        check_desktop(page, name)
                    if errors:
                        raise AssertionError(f"{name}: JS exceptions: {errors[:3]}")
                    print(f"✓ {args.browser}: {name} ({width}×{height})", flush=True)
                except Exception as exc:
                    print(f"✗ {args.browser}: {name} ({width}×{height}) — {exc}", flush=True)
                    failures.append(f"{name}: {exc}")
                    try:
                        page.screenshot(
                            path=str(screenshot_dir / f"{args.browser}-{name}.png"),
                            full_page=True, timeout=5000
                        )
                    except Exception:
                        pass
                finally:
                    context.close()
        finally:
            browser.close()

    if failures:
        raise SystemExit(
            f"{args.browser}: {len(failures)} viewport failures:\n"
            + "\n".join(failures)
        )
    print(f"All {len(CASES)} responsive {args.browser} viewports passed.")


if __name__ == "__main__":
    main()
