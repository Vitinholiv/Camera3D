import pygame
import OpenGL.GL as gl
import OpenGL.GLU as glu
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

pygame.font.init()
UI_FONT = None


def update_ui_font(c_h):
    global UI_FONT
    font_size = max(12, int(c_h * 0.3))
    UI_FONT = pygame.font.SysFont('Arial', font_size)


def draw_text(text, x, y, color=(255, 255, 255)):
    if UI_FONT is None:
        return
    text_surface = UI_FONT.render(text, True, color)
    text_data    = pygame.image.tostring(text_surface, "RGBA", True)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glColor3f(1.0, 1.0, 1.0)
    gl.glRasterPos2f(x, y)
    gl.glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text_data)
    gl.glDisable(gl.GL_BLEND)


def process_window_resize(new_w, new_h):
    MIN_W = 640; MIN_H = 360
    actual_w = max(new_w, MIN_W)
    actual_h = max(new_h, MIN_H)

    target_aspect = 16.0 / 9.0
    def_w = actual_w
    def_h = int(actual_w / target_aspect)

    if def_h > actual_h:
        def_h = actual_h
        def_w = int(actual_h * target_aspect)

    delta_w = (actual_w - def_w) // 2
    delta_h = (actual_h - def_h) // 2

    pygame.display.set_mode((actual_w, actual_h), DOUBLEBUF | OPENGL | RESIZABLE)
    return def_w, def_h, delta_w, delta_h


def change_gl_mode(mode):
    if mode == 'PROJECTION':
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
    elif mode == 'MODELVIEW':
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()


def _draw_rect(x, y, w, h, inset=1):
    ix = x + inset;  iy = y + inset
    iw = w - 2 * inset;  ih = h - 2 * inset
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex2f(ix,      iy)
    gl.glVertex2f(ix + iw, iy)
    gl.glVertex2f(ix + iw, iy + ih)
    gl.glVertex2f(ix,      iy + ih)
    gl.glEnd()


def draw_ui_borders(current_w, current_h, delta_w, delta_h, A_w, A_h):
    gl.glViewport(0, 0, current_w, current_h)

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    glu.gluOrtho2D(0, current_w, 0, current_h)

    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_LIGHTING)

    gl.glColor3f(1.0, 1.0, 1.0)
    gl.glLineWidth(1.0)

    box_left_w  = int(5  * A_w)
    box_right_w = int(11 * A_w)
    box_half_h  = int(4.5 * A_h)

    x_base = delta_w
    y_base = delta_h

    _draw_rect(x_base,              y_base, box_left_w,  int(9 * A_h))
    _draw_rect(x_base + box_left_w, y_base, box_right_w, box_half_h)
    _draw_rect(x_base + box_left_w, y_base + box_half_h, box_right_w, box_half_h)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_LIGHTING)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()


def draw_ui(current_w, current_h, delta_w, delta_h, c_w, c_h,
            sliders, buttons, mode_name, params):
    """
    buttons: lista de Button (aceita tanto lista quanto objeto único para
             compatibilidade retroativa)
    """
    gl.glViewport(0, 0, current_w, current_h)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    glu.gluOrtho2D(0, current_w, 0, current_h)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_LIGHTING)

    title_y = delta_h + int(8.5 * c_h)
    if UI_FONT:
        text_w, _ = UI_FONT.size(mode_name)
        title_x   = delta_w + int(5 * c_w) // 2 - text_w // 2
        draw_text(mode_name, title_x, title_y)

    # Aceita lista ou objeto único
    btn_list = buttons if isinstance(buttons, (list, tuple)) else [buttons]
    for btn in btn_list:
        btn.draw(c_h)

    for s in sliders:
        s.draw(params)

    draw_ui_borders(current_w, current_h, delta_w, delta_h, c_w, c_h)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_LIGHTING)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()


class Button:
    def __init__(self, x, y, width, height, label):
        self.x      = x
        self.y      = y
        self.width  = width
        self.height = height
        self.label  = label

    def draw(self, c_h):
        gl.glColor3f(0.3, 0.3, 0.3)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(self.x,              self.y)
        gl.glVertex2f(self.x + self.width, self.y)
        gl.glVertex2f(self.x + self.width, self.y + self.height)
        gl.glVertex2f(self.x,              self.y + self.height)
        gl.glEnd()

        gl.glColor3f(1.0, 1.0, 1.0)
        _draw_rect(self.x, self.y, self.width, self.height)
        draw_text(self.label,
                  self.x + self.width  * 0.3,
                  self.y + self.height * 0.2)

    def is_clicked(self, mx, my):
        return (self.x <= mx <= self.x + self.width and
                self.y <= my <= self.y + self.height)


class Slider:
    def __init__(self, label, min_val, max_val, param_key):
        self.label     = label
        self.min_val   = min_val
        self.max_val   = max_val
        self.param_key = param_key
        self.x = self.y = self.width = self.height = self.kw = 0
        self.active = False

    def update_geometry(self, x, y, width, c_h):
        self.x      = x
        self.y      = y
        self.width  = width
        self.height = int(c_h * 0.3)
        self.kw     = int(width * 0.03)

    def draw(self, params):
        current_val = params[self.param_key]
        draw_text(f"{self.label}: {current_val:.2f}",
                  self.x, self.y + int(self.height * 1.2))

        gl.glColor3f(0.4, 0.4, 0.4)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(self.x,              self.y + self.height / 2)
        gl.glVertex2f(self.x + self.width, self.y + self.height / 2)
        gl.glEnd()

        percent = (current_val - self.min_val) / (self.max_val - self.min_val)
        percent = max(0.0, min(1.0, percent))
        knob_x  = self.x + percent * self.width

        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(knob_x - self.kw, self.y)
        gl.glVertex2f(knob_x + self.kw, self.y)
        gl.glVertex2f(knob_x + self.kw, self.y + self.height)
        gl.glVertex2f(knob_x - self.kw, self.y + self.height)
        gl.glEnd()

    def handle_event(self, event, mouse_pos, params):
        mx, my = mouse_pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                self.active = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.active = False
        if self.active:
            percent = (mx - self.x) / self.width
            percent = max(0.0, min(1.0, percent))
            params[self.param_key] = self.min_val + percent * (self.max_val - self.min_val)
