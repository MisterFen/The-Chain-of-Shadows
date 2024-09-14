import pygame

class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  # pygame.Rect
        self.capacity = capacity  # max objects per node
        self.objects = []
        self.divided = False

    def subdivide(self):
        """Divide the current node into 4 children."""
        x, y, w, h = self.boundary
        nw = pygame.Rect(x, y, w / 2, h / 2)
        ne = pygame.Rect(x + w / 2, y, w / 2, h / 2)
        sw = pygame.Rect(x, y + h / 2, w / 2, h / 2)
        se = pygame.Rect(x + w / 2, y + h / 2, w / 2, h / 2)
        self.northwest = QuadTree(nw, self.capacity)
        self.northeast = QuadTree(ne, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)
        self.divided = True

    def insert(self, obj):
        """Insert an object into the quadtree."""
        if not self.boundary.colliderect(obj.rect):
            return False  # Ignore objects outside boundary

        if len(self.objects) < self.capacity:
            self.objects.append(obj)
            return True

        if not self.divided:
            self.subdivide()

        if self.northwest.insert(obj):
            return True
        if self.northeast.insert(obj):
            return True
        if self.southwest.insert(obj):
            return True
        if self.southeast.insert(obj):
            return True

        return False

    def query(self, range_rect, found):
        """Find all objects within a certain range."""
        if not self.boundary.colliderect(range_rect):
            return found

        for obj in self.objects:
            if range_rect.colliderect(obj.rect):
                found.append(obj)

        if self.divided:
            self.northwest.query(range_rect, found)
            self.northeast.query(range_rect, found)
            self.southwest.query(range_rect, found)
            self.southeast.query(range_rect, found)

        return found