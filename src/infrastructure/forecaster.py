from datetime import date

from sklearn.linear_model import LinearRegression


class LinearTrendForecaster:
    """Modelo ML sencillo: regresión lineal sobre la serie diaria de salidas."""

    def predict(self, history: list[tuple[date, int]], horizon_days: int) -> float:
        if not history:
            return 0.0
        history = sorted(history)
        start, end = history[0][0], max(history[-1][0], date.today())
        n = (end - start).days + 1
        y = [0.0] * n
        for d, qty in history:
            y[(d - start).days] = float(qty)
        if n < 7:  # muy poco historial: promedio simple
            return sum(y) / n * horizon_days
        model = LinearRegression().fit([[i] for i in range(n)], y)
        future = model.predict([[n + i] for i in range(horizon_days)])
        return float(sum(max(0.0, v) for v in future))
    