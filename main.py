import pygame
from pygame.locals import QUIT, VIDEORESIZE
import OpenGL.GL as gl
import sys

from parameters import Parameters
from camera import VirtualCamera
from gui import process_window_resize

def main():
    pygame.init()
    WINDOW_WIDTH = 1280; WINDOW_HEIGHT = 720
    process_window_resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_caption("Simulador de Câmera 3D - Gomes & Velho")
    
    params = Parameters()
    cam = VirtualCamera(params)
    
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST) # Z-buffer
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == VIDEORESIZE:
                process_window_resize(event.w, event.h)
        
        # Logic
        # ...
        
        # Rendering
        gl.glClear(int(gl.GL_COLOR_BUFFER_BIT) | int(gl.GL_DEPTH_BUFFER_BIT))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()