"""Resumen mensual con IA. Siempre devuelve un resumen: si la IA falla, usa reglas locales."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import os
from concurrent.futures import TimeoutError as FutureTimeout
from src.domain.ports import ReportWriter

_CACHE: dict[str, dict] = {}  # solo guarda respuestas reales de la IA
AI_TIMEOUT_SECONDS = 40

def _clean_error(exc: Exception) -> str:
    """Mensaje corto y sin la llave, para mostrar al usuario."""
    msg = " ".join(str(exc).split())
    key = os.getenv("GEMINI_API_KEY")
    if key:
        msg = msg.replace(key, "***")
    return msg[:300]

def _compact(data: dict) -> dict:
    """Reduce el informe a lo esencial para gastar pocos tokens."""
    return {
        "periodo": data["period"],
        "mas_demandados": [{"codigo": r["codigo_qr"], "producto": r["nombre"], "unidades": r["unidades"],
                            "salidas": r["salidas"]} for r in data["most_demanded"][:5]],
        "por_agotarse": [{"codigo": a["codigo_qr"], "en_cajon": a["cajon"], "minimo": a["minimo"],
                          "en_cajas": a["caja"]} for a in data["near_depletion"][:8]],
        "pedidos_pendientes": data["pending_orders"],
        "recomendaciones_pendientes": [{"codigo": r["codigo_qr"], "sugerida": r["cantidad_sugerida"],
                                        "riesgo": r["nivel_riesgo"], "datos_base": r["datos_base"]}
                                       for r in data["recommendations"][:5]],
    }


def _local_summary(c: dict) -> str:
    """Respaldo sin IA: redacta el resumen con reglas a partir de los mismos datos."""
    lines = [f"Resumen de {c['periodo']} (generado con reglas locales)."]
    top = c["mas_demandados"]
    if top:
        lines.append("Mayor demanda: " + "; ".join(f"{t['producto']} ({t['unidades']} u)" for t in top[:3]) + ".")
    else:
        lines.append("No hubo salidas registradas en el mes.")
    risk = c["por_agotarse"]
    if risk:
        lines.append("Riesgo de faltante en cajón: " + ", ".join(
            f"{r['codigo']} ({r['en_cajon']}/{r['minimo']})" for r in risk[:5]) + ".")
    else:
        lines.append("Ningún producto está por debajo del mínimo en cajones.")
    lines.append(f"Pedidos pendientes: {c['pedidos_pendientes']}.")
    recs = c["recomendaciones_pendientes"]
    if recs:
        lines.append("Recomendaciones por decidir: " + ", ".join(
            f"{r['codigo']} sugerido {r['sugerida']} (riesgo {r['riesgo']})" for r in recs) + ".")
        if any(r["datos_base"] == "simulado" for r in recs):
            lines.append("Nota: algunas cifras se basan en datos de prueba simulados.")
    return "\n".join(lines)


class AIReportService:
    def __init__(self, reports, writer: ReportWriter | None = None, timeout: float = AI_TIMEOUT_SECONDS):
        self._reports = reports  # cualquier objeto con .monthly(year, month)
        self._writer = writer
        self._timeout = timeout

    def monthly_summary(self, year: int, month: int, refresh: bool = False) -> dict:
        compact = _compact(self._reports.monthly(year, month))
        key = hashlib.sha256(json.dumps(compact, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if not refresh and key in _CACHE:
            return {**_CACHE[key], "cached": True}
        text, model, error = self._try_ai(compact)
        if text:
            result = {"period": compact["periodo"], "summary": text, "source": "ai", "model": model,
                      "cached": False, "note": ""}
            _CACHE[key] = result
            return result
        note = "La IA no estuvo disponible; resumen generado con reglas locales a partir de los mismos datos."
        if error:
            note += f" Motivo: {error}"
        return {"period": compact["periodo"], "summary": _local_summary(compact), "source": "local",
                "model": None, "cached": False, "note": note}

    def _try_ai(self, compact: dict):
        if self._writer is None:
            return None, None, "no hay GEMINI_API_KEY configurada en .env"
        pool = ThreadPoolExecutor(max_workers=1)
        try:
            text = (pool.submit(self._writer.write, compact).result(timeout=self._timeout) or "").strip()
            if text:
                return text, getattr(self._writer, "last_model", None), None
            return None, None, "la IA devolvió una respuesta vacía"
        except FutureTimeout:
            return None, None, f"tiempo de espera agotado ({self._timeout:.0f} s)"
        except Exception as exc:  # conexión perdida, cuota agotada, modelo inexistente...
            return None, None, _clean_error(exc)
        finally:
            pool.shutdown(wait=False)