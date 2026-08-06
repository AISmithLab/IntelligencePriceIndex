#!/usr/bin/env python3
"""
Shared row filter: which archived Fiverr URLs are actually gigs.

A Fiverr gig URL is `fiverr.com/<seller>/<slug>`, so the pipeline keys every
observation by (seller, slug). But the crawl frame also picked up *landing*
pages that share that two-segment shape — `fiverr.com/hire/<category>` (Fiverr
Pro category directories) and `fiverr.com/agencies/<name>` — whose first path
segment is a reserved site section, not a seller handle.

Those pages carry no packageList JSON, so `09-extract-prices.py` fell through to
its `dollar_fallback` branch and scraped the largest dollar figure on the page.
On a `/hire/` directory that figure is the **budget-filter widget's default**,
not a price. Fiverr changed that default from $1000 to $500 between 2024Q4 and
2025Q1, which injected a synthetic -50% move into every affected category — the
defect that motivated this module (found 2026-07-30; see progress.md).

Scale of the problem in `recent-prices.csv`: 3,846 of 15,150 rows (25.4%), of
which 2,436 sit at exactly $500.0 and 330 at $1000.0. `pilot-prices.csv` (the
historical crawl) contains zero such rows.

WHY NOT JUST DROP `extraction_method == "dollar_fallback"`:
    That was the other candidate rule and it is wrong. In `pilot-prices.csv`
    2,531 rows are `dollar_fallback` and 2,527 of them are genuine gigs — real
    seller handles with "<seller> : I will ... for $5 on www.fiverr.com" titles,
    clustered at $5 because that was Fiverr's original price floor. Dropping the
    method would delete valid history. The defect is the URL family, not the
    parser branch, so the filter keys on the path segment.

Use `is_gig(seller)` on any code path that reads a price CSV.
"""

# Fiverr URL path segments that are NOT seller handles. `hire` and `agencies`
# are the two observed in the crawl; the rest are known site sections included
# so a future crawl cannot reintroduce the same class of defect silently.
RESERVED = {"hire", "agencies", "categories", "category", "search", "gig", "gigs",
            "s", "users", "user", "profile", "inbox", "support", "help", "business",
            "pro", "resource", "resources", "cp", "community", "blog", "invite",
            "logo-maker", "start_selling", "seller_onboarding", "login", "join"}


def is_gig(seller):
    """True if `seller` is a real handle rather than a reserved site section."""
    return bool(seller) and seller.lower() not in RESERVED


def is_gig_id(gig_id):
    """Same test against a 'seller/slug' string."""
    return is_gig(gig_id.split("/", 1)[0]) if gig_id else False
