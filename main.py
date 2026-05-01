import sys
import pygame
from pygame.locals import QUIT, VIDEORESIZE
import OpenGL.GL as gl
import OpenGL.GLU as glu

from parameters import Parameters
from camera import VirtualCamera, Observer
from gui import process_window_resize, change_gl_mode, draw_ui_borders
from geometry import draw_virtual_camera, draw_origin_axes, draw_xz_grid

INITIAL_WINDOW_WIDTH = 1280; INITIAL_WINDOW_HEIGHT = 720
EXTERNAL_FOV = 60.0; EXTERNAL_ASPECT = 11.0/4.5
EXTERNAL_NEAR = 0.1; EXTERNAL_FAR = 500.0

def init_gl_states():
    gl.glClearColor(0.05, 0.05, 0.05, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST) # Z-Buffer
    gl.glEnable(gl.GL_LIGHTING)

def update_window_variables(def_w, def_h, delta_w, delta_h):
    c_w = def_w / 16.0
    c_h = def_h / 9.0
    obswin_x = delta_w + int(5 * c_w)
    obswin_y = delta_h 
    obswin_w = int(11 * c_w)
    obswin_h = int(4.5 * c_h)
    return c_w, c_h, obswin_x, obswin_y, obswin_w, obswin_h

def main():
    pygame.init()
    pygame.display.set_caption("Simulador de Câmera 3D")

    current_w, current_h = INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT
    def_w, def_h, delta_w, delta_h = process_window_resize(current_w, current_h)
    c_w, c_h, obswin_x, obswin_y, obswin_w, obswin_h = update_window_variables(def_w, def_h, delta_w, delta_h)

    init_gl_states()
    
    obs = Observer()
    params = Parameters()
    cam = VirtualCamera(params)
    clock = pygame.time.Clock()
    
    while True:
        keys = pygame.key.get_pressed()
        obs.move(keys)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                my = current_h - my # GL coordinate inversion
                in_x_obs = obswin_x <= mx <= obswin_x + obswin_w
                in_y_obs = obswin_y <= my <= obswin_y + obswin_h
                
                if in_x_obs and in_y_obs:
                    if not obs.active:
                        obs.active = True
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                    else:
                        obs.toggle_speed()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                obs.active = False
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)

            if event.type == pygame.MOUSEMOTION and obs.active:
                obs.rotate(event.rel[0], event.rel[1])
                
            if event.type == VIDEORESIZE:
                current_w, current_h = event.w, event.h
                def_w, def_h, delta_w, delta_h = process_window_resize(current_w, current_h)
                init_gl_states()
        
        # --- Logic and Calculations ---

        c_w, c_h, obswin_x, obswin_y, obswin_w, obswin_h = update_window_variables(def_w, def_h, delta_w, delta_h)
        
        # --- Rendering ---

        gl.glViewport(0, 0, current_w, current_h)
        gl.glClear(int(gl.GL_COLOR_BUFFER_BIT) | int(gl.GL_DEPTH_BUFFER_BIT))

        # External Camera
        gl.glViewport(obswin_x, obswin_y, obswin_w, obswin_h)
        change_gl_mode('PROJECTION')
        glu.gluPerspective(EXTERNAL_FOV, EXTERNAL_ASPECT, EXTERNAL_NEAR, EXTERNAL_FAR) 
        change_gl_mode('MODELVIEW')
        obs.update_view()

        # Objects
        draw_xz_grid(size=50, step=1)
        draw_origin_axes()
        draw_virtual_camera(cam)

        # UI
        draw_ui_borders(current_w, current_h, delta_w, delta_h, c_w, c_h)

        # --- Blit ---
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()