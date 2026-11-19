# Changelog

Fork of [public-clis/twitter-cli](https://github.com/public-clis/twitter-cli).
Only fork-specific releases are listed here; everything up to `0.8.6` is upstream work.

## 0.8.8

- **fix(article):** `twitter article` now works with `x.com/i/article/<id>` links and bare
  article entity ids. Article entity ids live in a different id space than posts, so
  `TweetResultByRestId` returned nothing and the command failed with `Article not found`
  for every article URL. Article ids are now resolved through `ArticleRedirectScreenQuery`
  (the same query X's own client fires on an article page: `articleEntityId` →
  `metadata.tweet_results.rest_id`), with a search-by-id fallback if that query id rotates.
  Post ids still take the direct path — no extra request.
- **fix(packaging):** install the package editable in the CLI venv, so repo edits take
  effect instead of the stale `site-packages` copy.
- **test:** four offline tests for article id resolution (direct hit, resolved hit,
  `_iter_tweet_results` traversal, not-found).

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
