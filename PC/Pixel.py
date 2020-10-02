from Color import Color


class Pixel:

    """
    col_pix
    reg_id
    color (0, 1, 2)
    link
    """

    def __init__(self):
        self.reg_id = -1
        self.reg_id_2 = -1
        self.color = 0
        self.link = []
        self.col_pix = Color()
        self.is_edge = False
        self.potential = False

    def __str__(self):
        return str(self.reg_id)

    def add_link(self, link_id):
        if not self.link.__contains__(link_id):
            self.link.append(link_id)

    def r(self):
        return self.col_pix.r

    def g(self):
        return self.col_pix.g

    def b(self):
        return self.col_pix.b

    def acceptable(self, pixel, tolerance):
        if max(abs(self.r() - pixel.r()),
               abs(self.g() - pixel.g()),
               abs(self.b() - pixel.b())) < tolerance:
            return True
        return False

    def average(self):
        return (self.col_pix.r + self.col_pix.g + self.col_pix.b) / 3
