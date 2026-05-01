import math

# Default values for the camera
DEFAULT_C = [0, 0, 0]; DEFAULT_N = [0, 0, -1]; DEFAULT_V = [0, 1, 0]
DEFAULT_NDIST = 0.1; DEFAULT_FDIST = 100.0; DEFAULT_D = 1.0
DEFAULT_UMIN = -22.0 / 9.0; DEFAULT_VMIN = -1.0
DEFAULT_UMAX = 22.0 / 9.0;  DEFAULT_VMAX = 1.0
DEFAULT_FOV = 90.0; DEFAULT_ASPECT = 22.0/9.0

class Parameters:
    def __init__(self,
            C = DEFAULT_C, N = DEFAULT_N, V = DEFAULT_V, n = DEFAULT_NDIST, f = DEFAULT_FDIST, d = DEFAULT_D,
            u_min = DEFAULT_UMIN, v_min = DEFAULT_VMIN, u_max = DEFAULT_UMAX, v_max = DEFAULT_VMAX,
            fov = DEFAULT_FOV, aspect = DEFAULT_ASPECT
        ):
            self.C = C; self.N = N; self.V = V
            self.n = n; self.f = f; self.d = d
            self.u_min = u_min; self.v_min = v_min
            self.u_max = u_max; self.v_max = v_max
            self.fov = fov; self.aspect = aspect

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Parâmetro '{key}' não existe.")

    def __setitem__(self, key, value):
        if not hasattr(self, key):
            raise KeyError(f"Parâmetro '{key}' não existe.")
        setattr(self, key, value)
    
        # Fov/Aspect changes -> Virtual Screen Coordinates change
        if key in ['fov', 'aspect']:
            sv = self.d * math.tan(math.radians(self.fov) / 2.0)
            su = sv * self.aspect
            self.v_max = sv
            self.v_min = -sv
            self.u_max = su
            self.u_min = -su
            
        # Virtual Screen Coordinates change -> Fov/Aspect changes
        elif key in ['u_min', 'u_max', 'v_min', 'v_max']:
            width = self.u_max - self.u_min
            height = self.v_max - self.v_min
            
            if height != 0:
                self.aspect = width / height
                sv = height / 2.0
                if self.d != 0:
                    self.fov = math.degrees(2 * math.atan(sv / self.d))

        # d changes -> preserve FOV/Aspect
        elif key == 'd':
            sv = self.d * math.tan(math.radians(self.fov) / 2.0)
            su = sv * self.aspect
            self.v_max = sv
            self.v_min = -sv
            self.u_max = su
            self.u_min = -su

    # Apply restricted model changes
    def restrict(self):
        su = (self.u_max - self.u_min) / 2.0
        sv = (self.v_max - self.v_min) / 2.0
        self.u_max = su
        self.u_min = -su
        self.v_max = sv
        self.v_min = -sv
        self.d = self.n