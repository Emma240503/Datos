import heapq

class Pedido:
    def __init__(self, pickup, dropoff, weight=1, priority=0, payout=100):
        self.pickup = pickup
        self.dropoff = dropoff
        self.weight = weight
        self.priority = priority  # entre más alto, más urgente
        self.payout = payout

    def __lt__(self, other):
        # prioridad más alta primero
        return self.priority > other.priority


class ColaPedidos:
    def __init__(self, lista_pedidos):
        # Usamos heapq para mantener ordenado por prioridad
        self.cola = []
        for p in lista_pedidos:
            pedido = Pedido(
                p["pickup"],
                p["dropoff"],
                p.get("weight", 1),
                p.get("priority", 0),
                p.get("payout", 100)
            )
            heapq.heappush(self.cola, pedido)

    def agregar_pedido(self, pedido):
        heapq.heappush(self.cola, pedido)

    def obtener_siguiente(self):
        if self.cola:
            return heapq.heappop(self.cola)  # sale el de mayor prioridad
        return None
