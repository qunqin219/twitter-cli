"""Query-id resolution: live bundle scanning must use the signed-in page."""
from __future__ import annotations

import pytest

from twitter_cli import graphql


@pytest.fixture(autouse=True)
def _reset_caches():
    graphql._cached_query_ids.clear()
    graphql._bundles_scanned = False
    yield
    graphql._cached_query_ids.clear()
    graphql._bundles_scanned = False


def test_extract_query_ids_forward_order():
    bundle = 'x={queryId:"abc123",operationName:"SearchTimeline",operationType:"query"}'
    assert graphql._extract_query_ids(bundle) == {"SearchTimeline": "abc123"}


def test_extract_query_ids_reverse_order():
    bundle = 'x={operationName:"UserTweets",metadata:{},queryId:"def456"}'
    assert graphql._extract_query_ids(bundle) == {"UserTweets": "def456"}


def test_extract_query_ids_first_entry_wins_and_merges_orders():
    bundle = (
        '{queryId:"first",operationName:"SearchTimeline"},'
        '{queryId:"second",operationName:"SearchTimeline"},'
        '{operationName:"UserTweets",queryId:"third"}'
    )
    assert graphql._extract_query_ids(bundle) == {
        "SearchTimeline": "first",
        "UserTweets": "third",
    }


def test_scan_bundles_prefers_authenticated_home_page():
    main_url = "https://abs.twimg.com/responsive-web/client-web/main.abc123a.js"
    pages = {
        "https://x.com/home": f'<script src="{main_url}"></script>',
        "https://x.com": '<script src="https://abs.twimg.com/x-web/entry-logged-out.js"></script>',
    }
    fetched = []

    def fetch(url, headers=None):
        fetched.append(url)
        if url in pages:
            return pages[url]
        if url == main_url:
            return '{queryId:"liveSearchId",operationName:"SearchTimeline"}'
        return ""

    graphql._scan_bundles(fetch)

    assert fetched[0] == "https://x.com/home", "must try the signed-in page first"
    assert "https://x.com" not in fetched, "logged-out page is skipped once main.js is known"
    assert graphql._cached_query_ids["SearchTimeline"] == "liveSearchId"


def test_scan_bundles_falls_back_to_logged_out_page():
    def fetch(url, headers=None):
        if url == "https://x.com/home":
            raise RuntimeError("401")
        if url == "https://x.com":
            return '<script src="https://abs.twimg.com/responsive-web/client-web/main.zzz.js"></script>'
        return '{queryId:"idFromFallbackPage",operationName:"Likes"}'

    graphql._scan_bundles(fetch)

    assert graphql._cached_query_ids["Likes"] == "idFromFallbackPage"


def test_authed_url_fetch_attaches_cookies():
    from twitter_cli.client import TwitterClient

    seen = {}

    def fake_fetch(url, headers=None):
        seen.update(headers or {})
        return ""

    client = TwitterClient("tok123", "csrf456")
    client._cookie_string = None
    original = graphql.__dict__.get("_url_fetch")
    import twitter_cli.client as client_mod

    client_mod._url_fetch, saved = fake_fetch, client_mod._url_fetch
    try:
        client._authed_url_fetch("https://x.com/home")
    finally:
        client_mod._url_fetch = saved

    assert "auth_token=tok123" in seen["Cookie"]
    assert "ct0=csrf456" in seen["Cookie"]
