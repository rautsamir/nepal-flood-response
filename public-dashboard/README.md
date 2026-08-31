# Nepal Flood Response Map

Public, static dashboard backed by a governed snapshot of the
`nepal_flood_response` schema. It has no Databricks credentials, warehouse
connection, or LLM calls in the browser.

## Refresh the snapshot

From the repository root, using your workspace env or CLI profile:

```bash
python3 scripts/export_public_snapshot.py \
  --catalog YOUR_CATALOG \
  --warehouse-id YOUR_SQL_WAREHOUSE_ID
```

The exporter uses fixed read-only SQL and replaces the files in `data/`.

## Run locally

```bash
python3 -m http.server 4173 --directory public-dashboard
```

Open `http://localhost:4173`.

## Deploy to Vercel

Create a Vercel project from this repository and set **Root Directory** to
`public-dashboard`. No framework preset, build command, environment variables,
or secrets are required. The generated domain can later be replaced with a
custom domain.

The committed data is a dated public snapshot. Refresh and redeploy it whenever
the lakehouse gold tables change.
