# mapa.py
import pygame

def cargar_mapa(api):
    ciudad_data = api.obtener_mapa()["data"]
    return ciudad_data["tiles"]

def dibujar_mapa(screen, tiles, colors, cam_x, cam_y, tile_size, view_width, view_height):
    for y in range(cam_y, cam_y + view_height):
        for x in range(cam_x, cam_x + view_width):
            tile = tiles[y][x]
            pygame.draw.rect(screen, colors.get(tile,(255,0,0)),
                             ((x-cam_x)*tile_size, (y-cam_y)*tile_size, tile_size, tile_size))
