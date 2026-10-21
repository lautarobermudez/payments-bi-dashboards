# Tableau vs Power BI: notes from building the same dashboard twice

**Method:** one dashboard (spend by month and status, top suppliers with a Pareto, pending payables by company and age, cost centres), same data (`bi.v_ops` and `bi.v_ops_centro_costo`), same checks (every headline figure compared with a SQL query).

**What is *not* here:** timed measurements. I did not stopwatch the same task in both tools, so this document makes no claim of the form "X is 40% faster". It records observations and where the effort went.

## Working with an AI agent

| | Power BI | Tableau |
|---|---|---|
| File format | PBIP: TMDL and PBIR text files. A diff shows exactly what changed. | `.twb` XML (or packaged `.twbx`). Verbose, order-sensitive XML. |
| Agent access | Microsoft's own Modeling MCP (read-only mode used) plus a report-authoring CLI and a Desktop bridge for screenshots. | A community MCP server with about 80 tools, no vendor support. |
| What the agent could do | Write the semantic model and measures in TMDL, build report pages as PBIR JSON, validate them with the CLI, take screenshots of the open report. | Add parameters, calculated fields, worksheets and a dashboard to an existing workbook. |
| What needed a human | Installing Desktop, enabling preview features, clicking *Refresh* (no refresh command), and one MCP binary that did not start on Windows. | Creating the first workbook (the MCP cannot start from scratch), opening the result in Tableau, and fixing XML the server wrote wrongly. |

## Lessons worth keeping

- **Validate with the tool's own validator.** For Tableau, well-formed XML was not enough: Tableau rejected files with elements in the wrong order, formats placed inside the wrong parent and fields missing from a worksheet's dependency list. I ended up with a repair script run after every save.
- **Text formats win.** The PBIP project reviews, diffs and merges like source code. The workbook XML does not.
- **Name clashes are silent.** A column and a measure with the same name in one table broke the load in Power BI; the modelling server did not detect it, Desktop did.
- **Verify numbers independently.** Every figure shown on the dashboards was compared with a SQL query on the same data. That check found mistakes the agents did not.
- **Table calculations need care.** A Tableau filter on a table-calculation field was evaluated row by row and produced a blank worksheet until it was changed to a table-calculation field instance.

## My reading

For a dashboard that will keep changing and needs review, the text-based Power BI project is easier to build with an agent and easier to maintain. For quick visual exploration by hand, Tableau was faster to *explore* in. Both conclusions are impressions from one project, not benchmarks.
