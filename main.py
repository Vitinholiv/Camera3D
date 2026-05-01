import sys
import pygame
from pygame.locals import QUIT, VIDEORESIZE
import OpenGL.GL as gl
import OpenGL.GLU as glu

from parameters import Parameters
from camera import VirtualCamera, Observer
from gui import process_window_resize, change_gl_mode, draw_ui, update_ui_font
from gui import Button, Slider
from geometry import draw_virtual_camera, draw_origin_axes, draw_xz_grid

INITIAL_WINDOW_WIDTH = 1280; INITIAL_WINDOW_HEIGHT = 720
EXTERNAL_FOV = 60.0; EXTERNAL_ASPECT = 11.0/4.5
EXTERNAL_NEAR = 0.1; EXTERNAL_FAR = 2000.0

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

def update_sliders_position(sliders_dict, mode, delta_w, delta_h, c_w, c_h, button):
    ui_x = delta_w + 20
    slider_w = int(5 * c_w) - 40
    update_ui_font(c_h)
    
    btn_size = int(c_h * 0.5)
    button.x = ui_x
    button.y = delta_h + int(8.4 * c_h)
    button.width = btn_size
    button.height = btn_size

    active_sliders = sliders_dict[mode]
    for i, s in enumerate(active_sliders):
        y_pos = delta_h + int((7.2 - (i * 0.9)) * c_h)
        s.update_geometry(ui_x, y_pos, slider_w, c_h)

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

    cam_mode = "RESTRICTED" # "RESTRICTED" , "STANDARD"
    btn_toggle = Button(0, 0, 0, 0, "C")
    sliders_data = {
        "STANDARD": [
            Slider("Near", 0.1, 20.0, params.n, "n"),
            Slider("Far", 10.0, 1000.0, params.f, "f"),
            Slider("Focal Dist", 0.1, 20.0, params.d, "d"),
            Slider("u_min", -2, 0.0, params.u_min, "u_min"),
            Slider("u_max", 0.0, 2.0, params.u_max, "u_max"),
            Slider("v_min", -2.0, 0.0, params.v_min, "v_min"),
            Slider("v_max", 0.0, 2.0, params.v_max, "v_max"),
        ],
        "RESTRICTED": [
            Slider("Near", 0.1, 20.0, params.n, "n"),
            Slider("Far", 10.0, 100.0, params.f, "f"),
            Slider("FOV", 10.0, 150.0, params.fov, "fov"),
            Slider("Aspect Ratio", 0.1, 5.0, params.aspect, "aspect"),
        ]
    }

    update_sliders_position(sliders_data, cam_mode, delta_w, delta_h, c_w, c_h, btn_toggle)
    
    while True:
        keys = pygame.key.get_pressed()
        obs.move(keys)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            if not obs.active:
                mx, my = pygame.mouse.get_pos()
                my = current_h - my
                for s in sliders_data[cam_mode]:
                    s.handle_event(event, (mx, my), params)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_toggle.is_clicked(mx, my):
                        cam_mode = "STANDARD" if cam_mode == "RESTRICTED" else "RESTRICTED"
                        if cam_mode == "RESTRICTED": params.restrict()
                        update_sliders_position(sliders_data, cam_mode, delta_w, delta_h, c_w, c_h, btn_toggle)

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
                c_w, c_h, obswin_x, obswin_y, obswin_w, obswin_h = update_window_variables(def_w, def_h, delta_w, delta_h)
                update_sliders_position(sliders_data, cam_mode, delta_w, delta_h, c_w, c_h, btn_toggle)
                init_gl_states()
        
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

        mode_label = "Câmera - Padrão" if cam_mode == "STANDARD" else "Câmera - Restrita"
        draw_ui(current_w, current_h, delta_w, delta_h, c_w, c_h, sliders_data[cam_mode], btn_toggle, mode_label)
        
        # --- Blit ---
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()