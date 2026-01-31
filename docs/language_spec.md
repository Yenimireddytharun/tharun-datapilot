# DataPilot Language Specification (v1.0)

## 1. General Rules
- **Comments:** Start with `\\`. Everything after `\\` on a line is ignored.
- **Case Sensitivity:** **NONE**. `LOAD`, `load`, and `Load` are all valid and identical.
- **Variables:** User-defined names (e.g., `myData`) are also case-insensitive.
- **Line Endings:** Each command ends with a new line. Semicolons (;) are optional.
- **Strings:** Must be enclosed in double quotes (e.g., "sales.csv").

## 2. Syntax Structure
`ACTION` + `SOURCE` + `CONDITION` + `AS` + `VARIABLE`

## 3. Mapping Table
| Command | Python Action |
| :--- | :--- |
| load | pandas.read_csv() |
| filter | df.query() |
| train | sklearn.fit() |
| plot | plotly.express |