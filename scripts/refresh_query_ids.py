#!/usr/bin/env python3
"""Refresh the hardcoded FALLBACK_QUERY_IDS in twitter_cli/graphql.py.

X rotates GraphQL queryIds regularly. The runtime already self-heals (a 404
triggers a live bundle scan), but keeping the constants current means the first
request of a session does not need a wasted round-trip.

Needs cookies (TWITTER_AUTH_TOKEN + TWITTER_CT0): the operation table only
exists in the signed-in shell, so this cannot run anonymously or in CI.

Exit codes: 0 = unchanged, 1 = updated (commit me), 2 = error.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from twitter_cli import graphql  # noqa: E402
from twitter_cli.client import TwitterClient  # noqa: E402

TARGETS = [
    "HomeTimeline", "HomeLatestTimeline", "UserByScreenName", "UserTweets",
    "TweetDetail", "Likes", "SearchTimeline", "Bookmarks",
    "ListLatestTweetsTimeline", "Followers", "Following", "CreateTweet",
    "DeleteTweet", "FavoriteTweet", "UnfavoriteTweet", "CreateRetweet",
    "DeleteRetweet", "CreateBookmark", "DeleteBookmark",
    "TweetResultByRestId", "BookmarkFoldersSlice", "BookmarkFolderTimeline",
]


def main() -> int:
    auth_token = os.environ.get("TWITTER_AUTH_TOKEN", "")
    ct0 = os.environ.get("TWITTER_CT0", "")
    if not auth_token or not ct0:
        print("TWITTER_AUTH_TOKEN / TWITTER_CT0 missing", file=sys.stderr)
        return 2

    client = TwitterClient(auth_token, ct0)

    # Force a fresh scan against the signed-in shell and read what it resolved.
    graphql._cached_query_ids.clear()
    graphql._bundles_scanned = False
    graphql._scan_bundles(client._authed_url_fetch)
    live = dict(graphql._cached_query_ids)

    if not live:
        print("could not resolve any live queryId", file=sys.stderr)
        return 2

    path = ROOT / "twitter_cli" / "graphql.py"
    source = path.read_text()
    changes = []
    for operation in TARGETS:
        new_id = live.get(operation)
        if not new_id:
            continue
        pattern = re.compile(r'("%s":\s*")([A-Za-z0-9_-]+)(")' % re.escape(operation))
        match = pattern.search(source)
        if match and match.group(2) != new_id:
            source = pattern.sub(lambda m: (m.group(1) or "") + new_id + (m.group(3) or ""),
                                source, count=1)
            changes.append((operation, match.group(2), new_id))

    if not changes:
        print(f"all {len(live)} live queryIds already current")
        return 0

    path.write_text(source)
    for operation, old, new in changes:
        print(f"{operation}: {old} -> {new}")
    print(f"\n{len(changes)} queryId(s) updated")
    return 1


if __name__ == "__main__":
    sys.exit(main())
