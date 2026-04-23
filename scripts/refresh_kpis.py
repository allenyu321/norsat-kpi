"""Fetch Shopify QTD visitors/sessions and write kpis.json.

Runs in GitHub Actions (see .github/workflows/refresh.yml). Credentials come
from Actions Secrets via environment variables — never from a committed file.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


SHOP = os.environ["SHOPIFY_SHOP"].strip()
TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"].strip()
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-10").strip()

OUT = Path(__file__).resolve().parent.parent / "kpis.json"


def main() -> None:
    url = f"https://{SHOP}/admin/api/{API_VERSION}/graphql.json"
    shopifyql = (
        "FROM sessions "
        "SHOW online_store_visitors, sessions "
        "WHERE human_or_bot_session IN ('human', 'bot') "
        "DURING this_quarter"
    )
    query = """
    query GetVisitors($q: String!) {
      shopifyqlQuery(query: $q) {
        parseErrors
        tableData { rows columns { name } }
      }
    }
    """
    resp = requests.post(
        url,
        json={"query": query, "variables": {"q": shopifyql}},
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"HTTP {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    if "errors" in data:
        sys.exit(f"GraphQL errors: {data['errors']}")

    result = (data.get("data") or {}).get("shopifyqlQuery") or {}
    parse_errors = result.get("parseErrors") or []
    if parse_errors:
        sys.exit(f"ShopifyQL parse error: {parse_errors}")

    rows = (result.get("tableData") or {}).get("rows") or []
    if not rows:
        sys.exit(f"No rows returned: {result}")

    totals = {"online_store_visitors": 0, "sessions": 0}
    for row in rows:
        if not row:
            continue
        for key in totals:
            try:
                totals[key] += int(row.get(key, 0))
            except (TypeError, ValueError):
                pass

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "period": "quarter_to_date",
        "visitors": totals["online_store_visitors"],
        "sessions": totals["sessions"],
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}: visitors={output['visitors']:,} sessions={output['sessions']:,}")


if __name__ == "__main__":
    main()
