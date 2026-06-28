import pandas as pd
import duckdb
import re

def create_table_from_sql(sql: str) -> dict:
    con = duckdb.connect(":memory:")
    statements = [s.strip() for s in sql.strip().split(";") if s.strip()]
    result = {"tables": {}, "logs": []}
    for stmt in statements:
        try:
            upper = stmt.upper().strip()
            if upper.startswith("CREATE TABLE"):
                con.execute(stmt)
                match = re.search(r"CREATE TABLE\s+(\w+)", stmt, re.IGNORECASE)
                table_name = match.group(1) if match else "table"
                result["logs"].append(f"[SQL] Table '{table_name}' created.")
            elif upper.startswith("INSERT"):
                con.execute(stmt)
                result["logs"].append(f"[SQL] Row inserted.")
            elif upper.startswith("SELECT"):
                df = con.execute(stmt).df()
                result["logs"].append(f"[SQL] SELECT returned {len(df)} rows.")
                result["query_result"] = df
            elif upper.startswith("ALTER TABLE"):
                con.execute(stmt)
                result["logs"].append(f"[SQL] Table altered.")
            else:
                con.execute(stmt)
                result["logs"].append(f"[SQL] Statement executed.")
        except Exception as e:
            result["logs"].append(f"[SQL ERROR] {e}")
    for tbl in con.execute("SHOW TABLES").fetchall():
        tname = tbl[0]
        df = con.execute(f"SELECT * FROM {tname}").df()
        schema = {col: str(df[col].dtype) for col in df.columns}
        result["tables"][tname] = {
            "dataframe": df,
            "schema": schema,
            "rows": len(df),
            "columns": list(df.columns),
            "sample": df.head(5).to_dict(orient="records")
        }
    return result

def get_table_properties(df: pd.DataFrame, table_name: str = "custom_table") -> dict:
    props = {
        "table_name": table_name,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": []
    }
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "nullable": bool(df[col].isnull().any()),
            "unique_count": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(3).tolist()
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["min"] = float(df[col].min())
            col_info["max"] = float(df[col].max())
            col_info["mean"] = round(float(df[col].mean()), 4)
        props["columns"].append(col_info)
    return props