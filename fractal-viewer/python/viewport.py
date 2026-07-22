class Viewport:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cx = -0.5
        self.cy = 0.0
        self.zoom = 200.0

    def screen_to_complex(self, sx, sy):
        px = (sx - self.width / 2) / self.zoom + self.cx
        py = (sy - self.height / 2) / self.zoom + self.cy
        return px, py

    def zoom_at(self, sx, sy, factor):
        px, py = self.screen_to_complex(sx, sy)
        self.zoom *= factor
        self.cx = px - (sx - self.width / 2) / self.zoom
        self.cy = py - (sy - self.height / 2) / self.zoom

    def pan(self, dx, dy):
        self.cx -= dx / self.zoom
        self.cy -= dy / self.zoom
