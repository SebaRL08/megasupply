class InMemoryProductRepository:
    def __init__(self):
        self._d, self._n = {}, 0
    def add(self, p):
        self._n += 1; p.id = self._n; self._d[p.id] = p; return p
    def get(self, i): return self._d.get(i)
    def get_by_code(self, c): return next((p for p in self._d.values() if p.codigo_qr == c), None)
    def list(self): return list(self._d.values())
    def update(self, i, **f):
        p = self._d.get(i)
        if p:
            for k, v in f.items(): setattr(p, k, v)
        return p
    def delete(self, i): return self._d.pop(i, None) is not None

class InMemoryMovementRepository:
    def __init__(self): self._m = []
    def add(self, m):
        m.id = len(self._m) + 1; self._m.append(m); return m
    def stock_of(self, pid):
        return sum(m.cantidad if m.tipo == "entrada" else -m.cantidad if m.tipo == "salida" else 0
                   for m in self._m if m.product_id == pid)