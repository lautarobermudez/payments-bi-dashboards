# payments-bi-dashboards

The same payments dashboard built twice, in **Tableau** and **Power BI**, on top of the `bi` views of [payments-data-platform](https://github.com/lautarobermudez/payments-data-platform). All data is synthetic.

The goal was to compare the two tools on one identical job (spend by month, supplier ranking, pending payables, cost centres) and to learn how far an AI coding agent can drive each of them.

## What is in the repository

| Path | What it is |
|---|---|
| `powerbi/PaymentsDashboard/` | Power BI project in the **PBIP** format (text files: TMDL semantic model + PBIR report), so it can be versioned and reviewed in git. |
| `tableau/payments_dashboard.twbx` | Packaged Tableau workbook with its CSV and a `.hyper` extract. |
| `data/` | The `bi.v_ops` view exported to CSV (decimal point and decimal comma). |
| `scripts/export_bi_views.py` | Exports `bi.v_ops` from PostgreSQL to CSV and, optionally, to a Tableau extract. |
| `docs/COMPARISON.md` | What worked, what did not, and an honest comparison of both tools. |

## Screenshots

**Power BI** (page *Tablero*): KPI cards, monthly spend with a 3-month moving average, pending payables by company and due-date status, Top 10 supplier Pareto and an overdue table.

![Power BI dashboard](docs/images/powerbi-dashboard.png)

**Tableau** (same figures, other tool): LOD-based share of spend by payment method, moving average, Pareto controlled by the Top N parameter.

![Tableau dashboard](docs/images/tableau-dashboard.png)

More: [Power BI Pareto](docs/images/powerbi-pareto.png), [Power BI cost centres](docs/images/powerbi-cost-centres.png), [Tableau Pareto sheet](docs/images/tableau-pareto.png).

## Power BI

- **Source:** PostgreSQL, schema `bi` (`localhost:5432`, database `payments`), loaded with the data-platform repository.
- **Model:** fact table `OPs` (from `bi.v_ops`), `Centros` (OP lines with cost centre), a generated `Calendario`, a `Parametros` table that holds the report cut-off date, and a `Top N` what-if table. Relationship `OPs[op_id]` → `Centros[orden_pago_id]`.
- **DAX:** 21 measures, among them net spend, pending and overdue amount, average ticket, share of company spend, 3-month moving average, month-over-month change, supplier ranking and a cumulative-% Pareto driven by the Top N parameter.
- **Pages:** Summary, Providers (Pareto with Top N slicer), Companies (average ticket), Dashboard (cards, monthly spend, pending by company, overdue table) and Cost centres.

To open it: load the database (see the other repository), open `PaymentsDashboard.pbip` in Power BI Desktop and press *Refresh*. If the connection fails with a certificate error, untick *Encrypt connections* for the PostgreSQL data source in the options (a local database uses a self-signed certificate).

## Tableau

`tableau/payments_dashboard.twbx` reads `bi.v_ops` through a CSV and an extract. It holds two parameters (cut-off date and Top N), calculated fields (LOD expressions such as `{FIXED}` and table calculations), eleven worksheets and one dashboard. To rebuild the data:

```bash
export DATABASE_URL="postgresql://payments:payments@localhost:5432/payments"
python scripts/export_bi_views.py
```

## Notes

- Labels, measure names and page titles are in Spanish, as in the original work for Spanish-speaking users.
- **How it was built:** I defined the dashboard and the metrics, and worked with Claude Code as an agent that edited the Power BI project files and, for Tableau, drove a community MCP server that edits workbook XML. I checked every figure against SQL. The findings about what the agents can and cannot do are in [docs/COMPARISON.md](docs/COMPARISON.md).
- A timed comparison is not included (see the note in the comparison document).

## License

MIT, see [LICENSE](LICENSE).
