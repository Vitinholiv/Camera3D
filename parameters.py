import math

# Default values for the camera
DEFAULT_C = [0, 1, 0]; DEFAULT_N = [0, 0, -1]; DEFAULT_V = [0, 1, 0]
DEFAULT_NDIST = 0.1; DEFAULT_FDIST = 30.0; DEFAULT_D = 1.0
DEFAULT_UMIN = -22.0 / 9.0; DEFAULT_VMIN = -1.0
DEFAULT_UMAX = 22.0 / 9.0;  DEFAULT_VMAX = 1.0
DEFAULT_FOV = 90.0; DEFAULT_ASPECT = 22.0/9.0

class Parameters:
    BOUNDS = {
        'n': (0.1, 20.0),
        'f': (10.0, 100.0),
        'd': (0.1, 20.0),
        'u_min': (-10.0, -0.01),
        'u_max': (0.01, 10.0),
        'v_min': (-10.0, -0.01),
        'v_max': (0.01, 10.0),
        'fov': (10.0, 150.0),
        'aspect': (0.1, 5.0)
    }

    def __init__(self):
        self.C = DEFAULT_C; self.N = DEFAULT_N; self.V = DEFAULT_V
        self.n = DEFAULT_NDIST; self.f = DEFAULT_FDIST; self.d = DEFAULT_D
        self.u_min = DEFAULT_UMIN; self.u_max = DEFAULT_UMAX
        self.v_min = DEFAULT_VMIN;  self.v_max = DEFAULT_VMAX
        self._sync_restricted_from_standard()

    def _clamp(self, key, value):
        low, high = self.BOUNDS.get(key, (-1e9, 1e9))
        return max(low, min(high, value))

    def _sync_standard_from_restricted(self):
        half_height = self.d * math.tan(math.radians(self.fov / 2.0))
        half_width = half_height * self.aspect
        
        self.v_max = self._clamp('v_max', half_height)
        self.v_min = -self.v_max
        self.u_max = self._clamp('u_max', half_width)
        self.u_min = -self.u_max

    def _sync_restricted_from_standard(self):
        width = self.u_max - self.u_min
        height = self.v_max - self.v_min
        
        if height > 0:
            self.aspect = self._clamp('aspect', width / height)
            
            if self.d > 0:
                angle_top = math.atan(self.v_max / self.d)
                angle_bottom = math.atan(self.v_min / self.d)
                new_fov = math.degrees(angle_top - angle_bottom)
                self.fov = self._clamp('fov', new_fov)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        if not hasattr(self, key): return
        setattr(self, key, self._clamp(key, value))

        if key in ['fov', 'aspect']:
            self._sync_standard_from_restricted()
            self._sync_restricted_from_standard()
            
        elif key in ['u_min', 'u_max', 'v_min', 'v_max', 'd']:
            self._sync_restricted_from_standard()
            
            if key == 'd' and (self.fov >= 150.0 or self.fov <= 10.0):
                pass

    def restrict(self):
        su = (self.u_max - self.u_min) / 2.0
        sv = (self.v_max - self.v_min) / 2.0
        self.u_max = su; self.u_min = -su
        self.v_max = sv; self.v_min = -sv
        self._sync_restricted_from_standard()