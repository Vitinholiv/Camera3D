import sys
import pygame
from pygame.locals import QUIT, VIDEORESIZE
import OpenGL.GL as gl
import OpenGL.GLU as glu

from parameters import Parameters
from camera import VirtualCamera
from gui import process_window_resize, change_gl_mode, draw_ui_borders
from geometry import draw_virtual_camera, draw_origin_axes, draw_xz_grid

INITIAL_WINDOW_WIDTH = 1280; INITIAL_WINDOW_HEIGHT = 720
EXTERNAL_FOV = 60.0; EXTERNAL_ASPECT = 11.0/4.5
EXTERNAL_NEAR = 0.1; EXTERNAL_FAR = 100.0
EXTERNAL_POS = (10.0, 8.0, 10.0, 
                0.0, 0.0, 0.0, 
                0.0, 1.0, 0.0)

def init_gl_states():
    gl.glClearColor(0.05, 0.05, 0.05, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST) # Z-Buffer
    gl.glEnable(gl.GL_LIGHTING)

def main():
    pygame.init()
    current_w, current_h = INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT
    def_w, def_h, delta_w, delta_h = process_window_resize(current_w, current_h)
    pygame.display.set_caption("Simulador de Câmera 3D")

    init_gl_states()
    
    params = Parameters()
    cam = VirtualCamera(params)
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == VIDEORESIZE:
                current_w, current_h = event.w, event.h
                def_w, def_h, delta_w, delta_h = process_window_resize(current_w, current_h)
                init_gl_states()
        
        # --- Logic and Calculations ---

        screen_unit_w = def_w / 16.0
        screen_unit_h = def_h / 9.0
        observer_window_x = delta_w + int(5 * screen_unit_w)
        observer_window_y = delta_h 
        observer_window_w = int(11 * screen_unit_w)
        observer_window_h = int(4.5 * screen_unit_h)
        
        # --- Rendering ---

        gl.glViewport(0, 0, current_w, current_h)
        gl.glClear(int(gl.GL_COLOR_BUFFER_BIT) | int(gl.GL_DEPTH_BUFFER_BIT))

        # External Camera
        gl.glViewport(observer_window_x, observer_window_y, observer_window_w, observer_window_h)
        change_gl_mode('PROJECTION')
        glu.gluPerspective(EXTERNAL_FOV, EXTERNAL_ASPECT, EXTERNAL_NEAR, EXTERNAL_FAR) 
        change_gl_mode('MODELVIEW')
        p1,p2,p3,p4,p5,p6,p7,p8,p9 = EXTERNAL_POS
        glu.gluLookAt(p1,p2,p3,p4,p5,p6,p7,p8,p9)

        # Objects
        draw_xz_grid(size=10, step=1)
        draw_origin_axes()
        draw_virtual_camera(cam)

        # UI
        draw_ui_borders(current_w, current_h, delta_w, delta_h, screen_unit_w, screen_unit_h)

        # --- Blit ---
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()