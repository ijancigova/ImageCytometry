class BoundingBox:

    def __init__(self, x, y, in_track, frame, width, height):
        self.x = x
        self.y = y
        self.in_track = in_track
        self.frame_index = frame
        self.width = width
        self.height = height

    def __str__(self):
        return "[" + str(self.x) + "," + str(self.y) + "," + str(self.in_track) + "," + str(self.frame_index) + "," + "]"

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.in_track == other.in_track:
            return True
        return False

    def __ne__(self, other):
        if self == other:
            return False
        return True

