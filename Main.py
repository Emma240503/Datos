import pygame
import time
import api
from jugador import Jugador
from mapa import cargar_mapa, dibujar_mapa
from pedidos import reubicar_pedidos
from clases import ColaPedidos, Pedido
import random

pygame.init()
clock = pygame.time.Clock()

# --- Configuración ---
tile_size = 60
view_width, view_height = 16, 16
screen = pygame.display.set_mode((view_width * tile_size, view_height * tile_size))
pygame.display.set_caption("Courier Quest - Mapa")

colors = {"C": (200, 200, 200), "B": (0, 0, 0), "P": (0, 200, 0)}
player_color = (0, 0, 255)
pickup_color = (255, 165, 0)
dropoff_color = (255, 0, 0)

# --- Cargar mapa y pedidos iniciales ---
tiles = cargar_mapa(api)
pedidos_data = api.obtener_pedidos()["data"]
reubicar_pedidos(pedidos_data, tiles)
cola_pedidos = ColaPedidos(pedidos_data)

# --- Crear jugador ---
jugador = Jugador(0, 0)
map_width, map_height = len(tiles[0]), len(tiles)
m_clima = 1.0

# --- Variables de control ---
ultimo_check = time.time()
check_interval = 15
pedidos_activos = []  # pedidos visibles en el mapa

# --- Variables de liberación ---
ultimo_liberado = 0
liberar_interval = 5  # segundos entre liberar pedidos

# --- Tiempo de juego ---
tiempo_inicio = time.time()
duracion = 10 * 60  # 10 minutos

# --- Bucle principal ---
running = True
while running:
    ahora = time.time()
    jugador.recuperar()



    # --- Finalizar juego ---
    if ahora - tiempo_inicio >= duracion:
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.fill((0, 0, 0))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(5000)
        running = False
        continue


   #---Finalizar juego---
    if jugador.reputacion <= 20:
        font = pygame.font.SysFont(None, 72)
        text = font.render("REPUTACIÓN MUY BAJA - FIN DEL JUEGO", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.fill((0, 0, 0))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(5000)
        running = False
        continue



    # --- Chequear nuevos pedidos ---
    if ahora - ultimo_check >= check_interval:
        try:
            resp = api.obtener_pedidos()
            nuevos_pedidos_data = resp.get("data", []) if isinstance(resp, dict) else resp
        except Exception as e:
            print("Error al obtener pedidos de la API, usando locales:", e)
            nuevos_pedidos_data = []

        for p in nuevos_pedidos_data:
            existe = any(
                p["pickup"] == ped.pickup and p["dropoff"] == ped.dropoff
                for ped in list(cola_pedidos.cola) + pedidos_activos
            )
            if not existe:
                ocupadas = set()
                for ped in pedidos_activos + list(jugador.inventario):
                    ocupadas.add(tuple(ped.pickup))
                    ocupadas.add(tuple(ped.dropoff))
                ocupadas.add((jugador.x, jugador.y))
                reubicar_pedidos([p], tiles, ocupadas)

                # Obtener prioridad desde la API
                prioridad = p.get("priority", 0)

                # Hacer que algunos pedidos normales suban a máxima prioridad (50% de probabilidad)
                if prioridad == 0 and random.random() < 0.5:
                    prioridad = 1

                nuevo_pedido = Pedido(
                    p["pickup"],
                    p["dropoff"],
                    p.get("weight", 1),
                    prioridad,
                    p.get("payout", 100)
                )
                cola_pedidos.agregar_pedido(nuevo_pedido)
                break
        ultimo_check = ahora

    # --- Liberar pedidos ---
    if len(pedidos_activos) < 5 and ahora - ultimo_liberado >= liberar_interval:
        pedido = cola_pedidos.obtener_siguiente()
        if pedido:
            pedidos_activos.append(pedido)
            ultimo_liberado = ahora

    # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            dx = dy = 0
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_UP:
                dy = -1
            elif event.key == pygame.K_DOWN:
                dy = 1
            elif event.key==pygame.K_q:
                jugador.cancelar_ultimo_pedido()

            jugador.mover(dx, dy, tiles, m_clima)

    # --- Revisar pickups ---
    for pedido in list(pedidos_activos):
        if [jugador.x, jugador.y] == pedido.pickup:
            if jugador.recoger_pedido(pedido):
                pedidos_activos.remove(pedido)
                print("Pedido recogido en:", pedido.pickup)

    # --- Revisar dropoffs ---
    entregado = jugador.entregar_pedido()
    if entregado:
        print("Pedido entregado en:", entregado.dropoff,
              "Puntaje:", jugador.puntaje,
              "Reputación:", jugador.reputacion,
              "Resistencia:", jugador.resistencia)

    # --- Cámara ---
    cam_x = max(0, min(jugador.x - view_width // 2, map_width - view_width))
    cam_y = max(0, min(jugador.y - view_height // 2, map_height - view_height))

    # --- Dibujar mapa y objetos ---
    screen.fill((255, 255, 255))
    dibujar_mapa(screen, tiles, colors, cam_x, cam_y, tile_size, view_width, view_height)

    for pedido in pedidos_activos:
        px, py = pedido.pickup
        if cam_x <= px < cam_x + view_width and cam_y <= py < cam_y + view_height:
            pygame.draw.rect(screen, pickup_color,
                             ((px - cam_x) * tile_size, (py - cam_y) * tile_size, tile_size, tile_size))

    for pedido in jugador.inventario:
        dx, dy = pedido.dropoff
        if cam_x <= dx < cam_x + view_width and cam_y <= dy < cam_y + view_height:
            color_dropoff = (255, 0, 0) if pedido.priority == 1 else (255, 105, 180)
            pygame.draw.rect(screen, color_dropoff,
                             ((dx - cam_x) * tile_size, (dy - cam_y) * tile_size, tile_size, tile_size))

    # --- Leyenda ---
    font = pygame.font.SysFont(None, 24)
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, 20, 20))
    screen.blit(font.render("Prioridad máxima", True, (0, 0, 0)), (35, 10))
    pygame.draw.rect(screen, (255, 105, 180), (10, 40, 20, 20))
    screen.blit(font.render("Prioridad normal", True, (0, 0, 0)), (35, 40))

    # --- Dibujar jugador ---
    pygame.draw.rect(screen, player_color,
                     ((jugador.x - cam_x) * tile_size, (jugador.y - cam_y) * tile_size, tile_size, tile_size))

    # --- Barra de resistencia ---
    max_resistencia = jugador.max_resistencia if hasattr(jugador, "max_resistencia") else 100
    ancho_barra = 200
    alto_barra = 20
    x_barra = 10
    y_barra = screen.get_height() - 40
    porcentaje = max(0, jugador.resistencia / max_resistencia)
    ancho_actual = int(ancho_barra * porcentaje)
    color_barra = (0, 255, 0) if porcentaje > 0.3 else (255, 0, 0)
    pygame.draw.rect(screen, (100, 100, 100), (x_barra, y_barra, ancho_barra, alto_barra))
    pygame.draw.rect(screen, color_barra, (x_barra, y_barra, ancho_actual, alto_barra))
    screen.blit(font.render("Resistencia", True, (0, 0, 0)), (x_barra, y_barra - 20))

    # --- Barra de reputación ---
    ancho_barra = 200
    alto_barra = 20
    x_barra = 10
    y_barra_reputacion = screen.get_height() - 100
    porcentaje_rep = max(0, jugador.reputacion / 100)
    ancho_actual_rep = int(ancho_barra * porcentaje_rep)
    color_barra_rep = (0, 0, 255)  # azul para reputación



    pygame.draw.rect(screen, (100, 100, 100), (x_barra, y_barra_reputacion, ancho_barra, alto_barra))
    pygame.draw.rect(screen, color_barra_rep, (x_barra, y_barra_reputacion, ancho_actual_rep, alto_barra))
    screen.blit(font.render("Reputación", True, (0, 0, 0)), (x_barra, y_barra_reputacion - 20))

    # --- Cronómetro ---
    tiempo_restante = max(0, int(duracion - (ahora - tiempo_inicio)))
    minutos = tiempo_restante // 60
    segundos = tiempo_restante % 60
    cronometro_texto = f"Tiempo: {minutos:02d}:{segundos:02d}"
    font_crono = pygame.font.SysFont(None, 36)
    screen.blit(font_crono.render(cronometro_texto, True, (0, 0, 0)),
                (screen.get_width() - 180, 10))

    # --- Mostrar mensajes temporales ---
    if jugador.mensaje and time.time() - jugador.mensaje_tiempo < 3:  # 3 seg visibles
        font_msg = pygame.font.SysFont(None, 28)
        aviso = font_msg.render(jugador.mensaje, True, (0, 0, 0))
        screen.blit(aviso, (10, screen.get_height() - 130))


    # --- Mensaje de energía ---
    if jugador.bloqueado:
        font_msg = pygame.font.SysFont(None, 36)
        aviso = font_msg.render("¡Sin energía! Descansando...", True, (255, 0, 0))
        screen.blit(aviso, (10, screen.get_height() - 70))

    # --- Texto fijo esquina inferior derecha ---
    font_fijo = pygame.font.SysFont(None, 28)
    texto_fijo = font_fijo.render(' "Q" para cancelar último pedido', True, (0, 0, 0))
    rect_fijo = texto_fijo.get_rect()
    rect_fijo.bottomright = (screen.get_width() - 10, screen.get_height() - 10)
    screen.blit(texto_fijo, rect_fijo)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
