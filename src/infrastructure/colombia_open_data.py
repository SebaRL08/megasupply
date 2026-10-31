from src.infrastructure.resilient_http import ResilientClient

BASE = "https://www.datos.gov.co/resource"
TRM_DATASET = "32sa-8pi3"     # TRM - Superintendencia Financiera
GNCV_DATASET = "he3q-86dn"    # GNCV prices - Ministerio de Minas y Energía


class OpenDataClient:
    def __init__(self, http: ResilientClient | None = None):
        self._http = http or ResilientClient()

    def dataset(self, dataset_id: str, **params) -> list[dict]:
        return self._http.get_json(f"{BASE}/{dataset_id}.json", params)

    def trm_history(self, limit: int = 90) -> list[dict]:
        return self.dataset(TRM_DATASET, **{"$limit": limit, "$order": "vigenciadesde DESC"})

    def gncv_prices(self, year: str, limit: int = 5000) -> list[dict]:
        return self.dataset(GNCV_DATASET, **{
            "$select": "departamento_eds,fecha_precio,precio_promedio_publicado",
            "$where": f"anio_precio = '{year}'",
            "$limit": limit,
        })