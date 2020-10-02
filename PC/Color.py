class Color:
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0

    def __str__(self):
        return str([self.r, self.g, self.b])

    def get(self, index):
        if index == 0:
            return self.r
        elif index == 1:
            return self.g
        elif index == 2:
            return self.b
        else:
            return -1
