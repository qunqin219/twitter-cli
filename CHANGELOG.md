# Changelog

Fork of [public-clis/twitter-cli](https://github.com/public-clis/twitter-cli).
Only fork-specific releases are listed here; everything up to `0.8.6` is upstream work.

## 0.8.7

- **chore(queryIds):** refresh hardcoded `FALLBACK_QUERY_IDS` against the live signed-in bundle
  (12 ids updated: `UserByScreenName`, `UserTweets`, `TweetDetail`, `Likes`, `SearchTimeline`,
  `Followers`, `Following`, `CreateTweet`, `DeleteTweet`, `CreateRetweet`, `DeleteRetweet`,
  `TweetResultByRestId`).
- **feat(scripts):** add `scripts/refresh_query_ids.py` — resolves live ids from the authenticated
  bundle, rewrites the constants, exits `1` when something changed so a scheduler can commit.
- **test:** stop asserting a literal `SearchTimeline` id in
  `TestBuildGraphqlUrl.test_searchtimeline_fallback_query_id_regression`; assert the shape instead,
  because X rotates the value on every web-client release.

## 0.8.6

- **fix(graphql):** query-id refresh now actually refreshes.
  - scan `https://x.com/home` first, fall back to `https://x.com`;
  - send session cookies on bundle fetches (`TwitterClient._authed_url_fetch`);
  - parse `main.<hash>a.js` and pair each `operationName` with its nearest `queryId`;
  - live ids override cached/fallback ids (`setdefault` → assignment);
  - six offline tests in `tests/test_query_id_refresh.py`.
