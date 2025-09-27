# pedidos.py
from collections import deque
from clases import Pedido

# pedidos.py
from collections import deque


def reubicar_pedidos(pedidos, mapa, ocupadas=None, separacion=4):
    """
    Reubica los pedidos evitando casillas bloqueadas o ocupadas, con separación mínima de 4.

    pedidos: lista de dicts con "pickup" y "dropoff"
    mapa: matriz del mapa
    ocupadas: conjunto de tuplas (x,y) de casillas ya ocupadas
    separacion: número mínimo de casillas alrededor que deben estar libres
    """
    if ocupadas is None:
        ocupadas = set()

    for p in pedidos:
        for punto in ["pickup", "dropoff"]:
            x0, y0 = p[punto]

            # Si el punto está bloqueado o ocupado, buscamos un lugar libre
            if mapa[y0][x0] == "B" or (x0, y0) in ocupadas:
                visitados = set()
                cola = deque([(x0, y0)])
                encontrado = False

                while cola and not encontrado:
                    x, y = cola.popleft()
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa):
                            if (nx, ny) not in visitados:
                                visitados.add((nx, ny))

                                # Verificar si cumple separación
                                libre = mapa[ny][nx] != "B"
                                if libre:
                                    for sx in range(-separacion, separacion + 1):
                                        for sy in range(-separacion, separacion + 1):
                                            tx, ty = nx + sx, ny + sy
                                            if 0 <= tx < len(mapa[0]) and 0 <= ty < len(mapa):
                                                if (tx, ty) in ocupadas:
                                                    libre = False
                                                    break
                                        if not libre:
                                            break

                                if libre:
                                    p[punto] = [nx, ny]
                                    ocupadas.add((nx, ny))
                                    encontrado = True
                                    break
                                else:
                                    cola.append((nx, ny))
            else:
                ocupadas.add((x0, y0))


def crear_objetos_pedidos(pedidos_data):
    return [Pedido(p["pickup"], p["dropoff"], p.get("weight",1), p.get("priority",0), p.get("payout",100)) for p in pedidos_data]
