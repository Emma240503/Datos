import time
from collections import deque

class Jugador:
    def __init__(self, x, y, capacidad=10):
        self.x = x
        self.y = y
        self.inventario = deque()
        self.resistencia = 100
        self.puntaje = 0
        self.reputacion = 70
        self.velocidad_base = 3
        self.ticks_sin_mover = 0
        self.capacidad = capacidad
        self.bloqueado = False
        self.ultimo_recupero = time.time()
        self.mensaje = ""        # <-- Atributo para mensaje en pantalla
        self.mensaje_tiempo = 0 # <-- Tiempo en que se generó el mensaje

    def peso_total(self):
        return sum(p.weight for p in self.inventario)

    def mover(self, dx, dy, mapa, m_clima=1.0):
        if self.bloqueado:
            return
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa):
            if mapa[ny][nx] != "B":
                peso_extra = max(0, self.peso_total() - 3)
                velocidad = self.velocidad_base / (1 + 0.3 * peso_extra) * m_clima
                if velocidad > 0:
                    self.x, self.y = nx, ny
                    consumo = 0.2 + 0.1 * peso_extra
                    self.resistencia = max(0, self.resistencia - consumo)
                    self.ticks_sin_mover = 0
            else:
                self.ticks_sin_mover += 1
        else:
            self.ticks_sin_mover += 1

        if self.ticks_sin_mover > 2:
            self.recuperar()

        if self.resistencia <= 0:
            self.bloqueado = True
            self.ultimo_recupero = time.time()

    def recuperar(self):
        ahora = time.time()
        if ahora - self.ultimo_recupero >= 1:
            self.resistencia = min(100, self.resistencia + 1)
            self.ultimo_recupero = ahora
            if self.resistencia >= 30:
                self.bloqueado = False

    def recoger_pedido(self, pedido):
        # Guardamos el tiempo en que se recoge el pedido
        pedido.tiempo_recogido = time.time()
        if self.peso_total() + pedido.weight <= self.capacidad:
            self.inventario.append(pedido)
            return True
        else:
            self.mensaje = "No se puede recoger el pedido, excede la capacidad."
            self.mensaje_tiempo = time.time()
            return False

    def cancelar_ultimo_pedido(self):
        if self.inventario:  # hay pedidos en inventario
            self.inventario.pop()  # elimina el último pedido recogido
            self.reputacion = max(0, self.reputacion - 4)  # resta 4 puntos de reputación
            self.mensaje = "Pedido cancelado (-4 reputación)"
            self.mensaje_tiempo = time.time()
        else:
            self.mensaje = "No hay pedidos para cancelar"
            self.mensaje_tiempo = time.time()


    def entregar_pedido(self):
        if not self.inventario:
            return None

        # Encontrar el pedido de mayor prioridad disponible para entregar
        max_priority = max(p.priority for p in self.inventario)
        pedidos_prioridad_max = [p for p in self.inventario if p.priority == max_priority]

        # Revisar si el jugador está en el dropoff de algún pedido de mayor prioridad
        for p in pedidos_prioridad_max:
            if [self.x, self.y] == p.dropoff:
                self.inventario.remove(p)
                self.puntaje += p.payout

                # --- Sistema de reputación con tiempo máximo 20 s ---
                tiempo_transcurrido = time.time() - getattr(p, "tiempo_recogido", time.time())
                if tiempo_transcurrido <= 20:
                    self.reputacion = min(100, self.reputacion + 3)
                else:
                    self.reputacion = max(0, self.reputacion - 2)

                # --- Bonus de 5% de payout si la reputación es >= 90 ---
                if self.reputacion >= 90:
                    bonus = int(p.payout * 0.05)
                    self.puntaje += bonus

                return p

        # Si llegó aquí, no puede entregar porque hay pedido de mayor prioridad
        #self.mensaje = "No se puede entregar este pedido, hay otro de mayor prioridad."
        #self.mensaje_tiempo = time.time()
        return None

