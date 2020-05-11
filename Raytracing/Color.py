class Color:
    def __init__(self, r, g, b):
        if r > 255:
            self.r = 255
        if r < 0:
            self.r = 0
        else:
            self.r = r

        if g > 255:
            self.g = 255
        if g < 0:
            self.g = 0
        else:
            self.g = g

        if b > 255:
            self.b = 255
        if b < 0:
            self.b = 0
        else:
            self.b = b

    def __repr__(self):

        return 'Color(%s,%s,%s)' % (repr(self.r), repr(self.g), repr(self.b))

    def getColor(self):
        return [int(self.r), int(self.g), int(self.b)]

    def __rmul__(self, scalar):
        return Color(self.r * scalar, self.g * scalar, self.b * scalar)

    def __mul__(self, other):
        return Color(self.r * other.r, self.g * other.g, self.b * other.b)

    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)
