# weekly-kpi

Auto-updated JSON snapshot of weekly traffic metrics.

Served at: https://allenyu321.github.io/weekly-kpi/kpis.json

## How it refreshes

`.github/workflows/refresh.yml` runs every Friday at 15:00 UTC
(08:00 PDT / 07:00 PST). It calls `scripts/refresh_kpis.py`, which queries
Shopify via ShopifyQL and writes `kpis.json`. If the content changed, the
workflow commits and pushes; GitHub Pages then serves the new file within a
minute or two.

To refresh ad-hoc, open the **Actions** tab and click **Run workflow** on
the *Weekly KPI Refresh* workflow.

## Secrets (GitHub → Settings → Secrets and variables → Actions)

- `SHOPIFY_SHOP` — e.g. `norsat.myshopify.com`
- `SHOPIFY_ACCESS_TOKEN` — Admin API access token, read-only scopes
  (`read_analytics`, `read_reports`) are enough
- `SHOPIFY_API_VERSION` — e.g. `2025-10`
