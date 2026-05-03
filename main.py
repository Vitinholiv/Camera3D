import sys
import pygame
from pygame.locals import QUIT, VIDEORESIZE
import OpenGL.GL as gl
import OpenGL.GLU as glu

from parameters import Parameters
from camera import VirtualCamera, Observer
from gui import process_window_resize, change_gl_mode, draw_ui, update_ui_font
from gui import Button, Slider
from geometry import draw_virtual_camera, draw_origin_axes, draw_xz_grid, get_frustum_planes
from objects import Sphere

INITIAL_WINDOW_WIDTH  = 1280
INITIAL_WINDOW_HEIGHT = 720
EXTERNAL_FOV    = 60.0
EXTERNAL_ASPECT = 11.0 / 4.5
EXTERNAL_NEAR   = 0.1
EXTERNAL_FAR    = 2000.0


def init_gl_states():
    gl.glClearColor(0.05, 0.05, 0.05, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_LIGHT0)

    light_pos = [10.0, 10.0, 10.0, 1.0]
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, light_pos)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT,  [0.2, 0.2, 0.2, 1.0])
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])

    gl.glEnable(gl.GL_COLOR_MATERIAL)
    gl.glColorMaterial(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE)


def update_window_variables(def_w, def_h, delta_w, delta_h):
    c_w = def_w / 16.0
    c_h = def_h / 9.0

    obswin_x = delta_w + int(5 * c_w)
    obswin_y = delta_h
    obswin_w = int(11 * c_w)
    obswin_h = int(4.5 * c_h)

    camwin_x = obswin_x
    camwin_y = obswin_y + obswin_h
    camwin_w = obswin_w
    camwin_h = obswin_h

    return c_w, c_h, obswin_x, obswin_y, obswin_w, obswin_h, camwin_x, camwin_y, camwin_w, camwin_h

def update_sliders_position(sliders_dict, mode, delta_w, delta_h, c_w, c_h,
                             btn_cam_mode, btn_frustum):
    ui_x     = delta_w + 20
    slider_w = int(5 * c_w) - 40
    update_ui_font(c_h)

    btn_size = int(c_h * 0.5)
    btn_y  = delta_h + int(8.4 * c_h)
    margin = int(9 * c_h) - int(8.4 * c_h) - btn_size

    btn_cam_mode.x      = delta_w + margin
    btn_cam_mode.y      = btn_y
    btn_cam_mode.width  = btn_size
    btn_cam_mode.height = btn_size

    btn_frustum.x      = delta_w + int(5 * c_w) - margin - btn_size
    btn_frustum.y      = btn_y
    btn_frustum.width  = btn_size
    btn_frustum.height = btn_size

    active_sliders = sliders_dict[mode]
    for i, s in enumerate(active_sliders):
        y_pos = delta_h + int((7.2 - (i * 0.9)) * c_h)
        s.update_geometry(ui_x, y_pos, slider_w, c_h)


def main():
    pygame.init()
    pygame.display.set_caption("Simulador de Câmera 3D")

    # --- Init ---

    current_w, current_h = INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT
    def_w, def_h, delta_w, delta_h = process_window_resize(current_w, current_h)
    c_w, c_h, obswin_x, obswin_y, obswin_w, obswin_h, \
        camwin_x, camwin_y, camwin_w, camwin_h = update_window_variables(
            def_w, def_h, delta_w, delta_h)

    init_gl_states()

    obs    = Observer()
    params = Parameters()
    cam    = VirtualCamera(params)
    clock  = pygame.time.Clock()

    cam_mode     = "RESTRICTED"   # "RESTRICTED" | "STANDARD"
    frustum_mode = "EDGES"        # "EDGES" | "FACES"

    btn_cam_mode = Button(0, 0, 0, 0, "C")
    btn_frustum  = Button(0, 0, 0, 0, "F")

    sliders_data = {
        "STANDARD": [
            Slider("Near",         0.1,   20.0,  "n"),
            Slider("Far",         10.0, 100.0,  "f"),
            Slider("Dist Focal",   0.1,   20.0,  "d"),
            Slider("u_min",      -10.0,    0.0,  "u_min"),
            Slider("u_max",        0.0,   10.0,  "u_max"),
            Slider("v_min",      -10.0,    0.0,  "v_min"),
            Slider("v_max",        0.0,   10.0,  "v_max"),
        ],
        "RESTRICTED": [
            Slider("Near",        0.1,   20.0,  "n"),
            Slider("Far",        10.0, 100.0,  "f"),
            Slider("FOV",        10.0,  150.0,  "fov"),
            Slider("Aspect Ratio", 0.1,   5.0,  "aspect"),
        ],
    }

    world_objects = [
        Sphere(position=[5, 2, 5], radius=2.0, color=(1.0, 0.5, 0.5))
    ]

    update_sliders_position(sliders_data, cam_mode, delta_w, delta_h,
                            c_w, c_h, btn_cam_mode, btn_frustum)

    while True:
        keys = pygame.key.get_pressed()
        obs.move(keys)
        cam.move(keys)

        # --- Events ---

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            mx, my = pygame.mouse.get_pos()
            my_gl = current_h - my

            if not obs.active and not cam.active:
                for s in sliders_data[cam_mode]:
                    s.handle_event(event, (mx, my_gl), params)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_cam_mode.is_clicked(mx, my_gl):
                        cam_mode = "STANDARD" if cam_mode == "RESTRICTED" else "RESTRICTED"
                        if cam_mode == "RESTRICTED": params.restrict()
                        update_sliders_position(sliders_data, cam_mode, delta_w, delta_h, c_w, c_h, btn_cam_mode, btn_frustum)
                    
                    elif btn_frustum.is_clicked(mx, my_gl):
                        frustum_mode = "FACES" if frustum_mode == "EDGES" else "EDGES"

                    elif (obswin_x <= mx <= obswin_x + obswin_w and obswin_y <= my_gl <= obswin_y + obswin_h):
                        obs.active = True
                        pygame.mouse.set_visible(False); pygame.event.set_grab(True)
                    elif (camwin_x <= mx <= camwin_x + camwin_w and camwin_y <= my_gl <= camwin_y + camwin_h):
                        cam.active = True
                        pygame.mouse.set_visible(False); pygame.event.set_grab(True)
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if obs.active: obs.toggle_speed()
                    if cam.active: cam.toggle_speed()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    obs.active = False; cam.active = False
                    pygame.mouse.set_visible(True); pygame.event.set_grab(False)

                if event.type == pygame.MOUSEMOTION:
                    if obs.active: obs.rotate(event.rel[0], event.rel[1])
                    if cam.active: cam.rotate(event.rel[0], event.rel[1])

            if event.type == VIDEORESIZE:
                current_w, current_h = event.w, event.h
                def_w, def_h, delta_w, delta_h = process_window_resize(current_w, current_h)
                c_w, c_h, obswin_x, obswin_y, obswin_w, obswin_h, camwin_x, camwin_y, camwin_w, camwin_h = update_window_variables(def_w, def_h, delta_w, delta_h)
                update_sliders_position(sliders_data, cam_mode, delta_w, delta_h, c_w, c_h, btn_cam_mode, btn_frustum)
                init_gl_states()

        # --- Rendering ---

        gl.glViewport(0, 0, current_w, current_h)
        gl.glClear(int(gl.GL_COLOR_BUFFER_BIT) | int(gl.GL_DEPTH_BUFFER_BIT))

        # Main Camera
        gl.glViewport(camwin_x, camwin_y, camwin_w, camwin_h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        proj_matrix = cam.get_full_projection_matrix()
        gl.glLoadMatrixd(proj_matrix.T)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        view_matrix = cam.get_view_matrix()
        gl.glLoadMatrixd(view_matrix.T)

        draw_xz_grid(size=50, step=1)
        draw_origin_axes()
        for obj in world_objects:
            obj.draw()

        # External Camera
        gl.glViewport(obswin_x, obswin_y, obswin_w, obswin_h)
        change_gl_mode('PROJECTION')
        glu.gluPerspective(EXTERNAL_FOV, EXTERNAL_ASPECT, EXTERNAL_NEAR, EXTERNAL_FAR)
        change_gl_mode('MODELVIEW')
        obs.update_view()

        draw_xz_grid(size=50, step=1)
        draw_origin_axes()
        draw_virtual_camera(cam, frustum_mode)
        
        for obj in world_objects:
            obj.draw(color_mult=0.18)

        gl.glDepthFunc(gl.GL_LEQUAL)
        planes = get_frustum_planes(cam)
        for i, plane in enumerate(planes):
            gl.glClipPlane(int(gl.GL_CLIP_PLANE0) + i, plane)
            gl.glEnable(int(gl.GL_CLIP_PLANE0) + i)
        for obj in world_objects:
            obj.draw()
        for i in range(6):
            gl.glDisable(int(gl.GL_CLIP_PLANE0) + i)
        gl.glDepthFunc(gl.GL_LESS)

        # UI
        mode_label = "Câmera - Padrão" if cam_mode == "STANDARD" else "Câmera - Restrita"
        draw_ui(current_w, current_h, delta_w, delta_h, c_w, c_h,
                sliders_data[cam_mode],
                [btn_cam_mode, btn_frustum],
                mode_label, params)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
