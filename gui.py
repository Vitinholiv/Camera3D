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
    if UI_FONT is None: return
    text_surface = UI_FONT.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glColor3f(1.0, 1.0, 1.0)
    gl.glRasterPos2f(x, y)
    gl.glDrawPixels(text_surface.get_width(), text_surface.get_height(), 
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text_data)
    gl.glDisable(gl.GL_BLEND)

class Slider:
    def __init__(self, label, min_val, max_val, initial_val, param_key):
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.param_key = param_key
        
        self.x = 0; self.y = 0; self.width = 0; self.height = 0; self.kw = 0
        self.active = False

    def update_geometry(self, x, y, width, c_h):
        self.x = x
        self.y = y
        self.width = width
        self.height = int(c_h * 0.3)
        self.kw = int(width * 0.03)

    def draw(self):
        label_text = f"{self.label}: {self.value:.2f}"
        draw_text(label_text, self.x, self.y + int(self.height * 1.2))

        gl.glColor3f(0.4, 0.4, 0.4)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(self.x, self.y + self.height/2)
        gl.glVertex2f(self.x + self.width, self.y + self.height/2)
        gl.glEnd()

        percent = (self.value - self.min_val) / (self.max_val - self.min_val)
        knob_x = self.x + (percent * self.width)
        
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
            percent = max(0, min(1, percent))
            self.value = self.min_val + percent * (self.max_val - self.min_val)
            params[self.param_key] = self.value

    def _get_knob_x(self):
        percent = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.x + (percent * self.width)

    def _val_to_pos(self, val):
        percent = (val - self.min_val) / (self.max_val - self.min_val)
        return self.x + (percent * self.width)

    def _pos_to_val(self, px):
        percent = (px - self.x) / self.width
        percent = max(0, min(1, percent))
        return self.min_val + percent * (self.max_val - self.min_val)
    
def process_window_resize(new_w, new_h):
    MIN_W = 640; MIN_H = 360
    actual_w = max(new_w, MIN_W)
    actual_h = max(new_h, MIN_H)
    
    target_aspect = 16.0/9.0
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
        ix = x + inset
        iy = y + inset
        iw = w - (2 * inset)
        ih = h - (2 * inset)
        
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex2f(ix, iy)
        gl.glVertex2f(ix + iw, iy)
        gl.glVertex2f(ix + iw, iy + ih)
        gl.glVertex2f(ix, iy + ih)
        gl.glEnd()

def draw_ui_borders(current_w, current_h, delta_w, delta_h, A_w, A_h):
    gl.glViewport(0, 0, current_w, current_h)
    
    # Save State
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    glu.gluOrtho2D(0, current_w, 0, current_h)
    
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_LIGHTING)

    # Drawing
    gl.glColor3f(1.0, 1.0, 1.0)
    gl.glLineWidth(1.0)
    
    box_left_w = int(5 * A_w)
    box_right_w = int(11 * A_w)
    box_full_h = int(9 * A_h)
    box_half_h = int(4.5 * A_h)
    
    x_base = delta_w
    y_base = delta_h

    _draw_rect(x_base, y_base, box_left_w, box_full_h)
    _draw_rect(x_base + box_left_w, y_base, box_right_w, box_half_h)
    _draw_rect(x_base + box_left_w, y_base + box_half_h, box_right_w, box_half_h)

    # Restore State
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_LIGHTING)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()
    
def draw_ui(current_w, current_h, delta_w, delta_h, c_w, c_h, sliders):
    gl.glViewport(0, 0, current_w, current_h)
    
    # Save
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    glu.gluOrtho2D(0, current_w, 0, current_h)
    
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_LIGHTING)
    
    # Draw
    for s in sliders:
        s.draw()

    draw_ui_borders(current_w, current_h, delta_w, delta_h, c_w, c_h)
    
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_LIGHTING)
    
    # Restore
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPopMatrix()