import duckdb
import pandas as pd


def trm_stats(rows: list[dict]) -> dict:
    df = pd.DataFrame(rows)
    df["valor"] = df["valor"].astype(float)
    df["vigenciadesde"] = pd.to_datetime(df["vigenciadesde"])
    con = duckdb.connect()
    con.register("trm", df)
    n, avg, mn, mx, sd = con.execute("""
        SELECT count(*), round(avg(valor), 2), min(valor), max(valor), round(stddev_samp(valor), 2)
        FROM trm WHERE valor > 0 AND vigenciadesde >= current_date - INTERVAL 180 DAY
    """).fetchone()
    return {"observations": n, "avg_cop_per_usd": avg, "min": mn, "max": mx, "volatility_std": sd}


def gncv_stats(rows: list[dict]) -> dict:
    df = pd.DataFrame(rows)
    df["precio"] = pd.to_numeric(df["precio_promedio_publicado"], errors="coerce")
    con = duckdb.connect()
    con.register("gncv", df)
    total, avg, mn, mx = con.execute("""
        SELECT count(*), round(avg(precio), 2), min(precio), max(precio)
        FROM gncv WHERE precio > 0
    """).fetchone()
    top = con.execute("""
        SELECT departamento_eds, round(avg(precio), 2), count(*)
        FROM gncv WHERE precio > 0
        GROUP BY departamento_eds ORDER BY 2 DESC LIMIT 5
    """).fetchall()
    return {"observations": total, "avg_price": avg, "min": mn, "max": mx,
            "top5_departments": [{"department": d, "avg_price": a, "observations": n}
                                 for d, a, n in top]}