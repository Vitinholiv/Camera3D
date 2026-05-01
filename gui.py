import pygame
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
import OpenGL.GL as gl

def process_window_resize(new_w, new_h):
    target_aspect = 16.0/9.0
    def_w = new_w
    def_h = int(new_w / target_aspect)
    
    if def_h > new_h:
        def_h = new_h
        def_w = int(new_h * target_aspect)
    
    delta_w = (new_w - def_w) // 2
    delta_h = (new_h - def_h) // 2
    
    pygame.display.set_mode((new_w, new_h), DOUBLEBUF | OPENGL | RESIZABLE)
    gl.glViewport(delta_w, delta_h, def_w, def_h)
    
    return def_w, def_h