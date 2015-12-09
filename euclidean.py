"""
Euclidean space defined on x-y plane.
"""
SIGNIFICANT = 8


class Point:
    def __init__(self, *args):
        self._x, self._y = 0, 0
        if len(args):
            if isinstance(args[0], Point):
                self._x, self._y = args[0].x, args[0].y
            elif len(args) == 2:
                if all(isinstance(a, (int, float)) for a in args):
                    self._x, self._y = args
                else:
                    raise TypeError("unknown input type: '%s' and '%s'" %
                                    (type(args[0]).__name__, type(args[1]).__name__))
            else:
                raise SyntaxError("invalid constructor: %s" % repr(args))

    def __repr__(self):
        return "({0:.14g}, {1:.14g})".format(self._x, self._y)

    def __add__(self, other):
        assert isinstance(other, Point), "incorrect addend type: %s" % type(other).__name__
        return Point(self._x + other.x, self._y + other.y)

    def __eq__(self, other):
        assert isinstance(other, Point), "incorrect addend type: %s" % type(other).__name__
        return self._x == other.x and self._y == other.y

    def __sub__(self, other):
        assert isinstance(other, Point), "incorrect input type: %s" % type(other).__name__
        return Point(self._x - other.x, self._y - other.y)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = float(x)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = float(y)

    @property
    def norm(self):
        return (self._x ** 2 + self._y ** 2) ** .5

    @property
    def is_origin(self):
        return self._x == 0 and self._y == 0

    @property
    def theta(self):
        from math import atan2
        return atan2(self._y, self._x)

    def distance_from(self, point):
        if not isinstance(point, Point):
            raise SyntaxError("incorrect input type: %s" % type(point).__name__)
        return ((self._x - point.x) ** 2 + (self._y - point.y) ** 2) ** .5


class Section:
    def __init__(self, *args):
        self._this, self._that = Point(), Point()
        if len(args):
            if len(args) == 4 and all(isinstance(a, (int, float)) for a in args):
                self._this = Point(args[0], args[1])
                self._that = Point(args[2], args[3])
            elif len(args) == 2 and all(isinstance(a, Point) for a in args):
                self._this = args[0]
                self._that = args[1]
            else:
                raise SyntaxError("invalid syntax: (%s)" %
                                  ", ".join(type(a).__name__ for a in args))

    def __repr__(self):
        return "[" + ", ".join([self._this.__str__(), self._that.__str__()]) + "]"

    @property
    def is_decayed(self):
        if self._this and self._that:
            return self._this == self._that

    @property
    def is_horizontal(self):
        return self.this.y == self.that.y

    @property
    def is_vertical(self):
        return self.this.x == self.that.x

    @property
    def norm(self):
        return self._this.distance_from(self._that)

    @property
    def this(self):
        return self._this

    @this.setter
    def this(self, point):
        if isinstance(point, Point):
            self._this = point
        else:
            raise TypeError("invalid input type")

    @property
    def that(self):
        return self._that

    @that.setter
    def that(self, point):
        if isinstance(point, Point):
            self._that = point
        else:
            raise TypeError("invalid input type")

    @property
    def vector(self):
        return self._that - self._this

    def area(self, ref=Point(0, 0)):
        """Calculate the triangular, and VECTOR area surrounded by points of Section
        and the referenced point (default the origin).
        """
        if self._this == self._that:
            return 0

        from math import sin

        if not isinstance(ref, Point):
            raise TypeError("invalid input type: %s" % type(ref).__name__)
        pair = (self._this - ref), (self._that - ref)
        theta = pair[1].theta - pair[0].theta
        return .5 * pair[0].norm * pair[1].norm * sin(theta)

    def __contains__(self, point):
        if not isinstance(point, Point):
            raise TypeError("argument of type '%s' is not valid. use Point instead"
                            % type(point).__name__)
        if point in (self._this, self._that):
            return True
        if not self.is_decayed:
            m1 = point - self._this
        return False


class Line:
    def __init__(self, *args):
        self._points = []
        gtype = type(a for a in [])
        if args:
            if all(isinstance(a, (Point, Section)) for a in args):
                for a in args:
                    if isinstance(a, Point):
                        self._points.append(a)
                    elif isinstance(a, Section):
                        self._points.append(a.this)
                        self._points.append(a.that)
            # must include generator type for further usage (class Polygon)
            elif isinstance(args[0], gtype):
                for aa in args[0]:
                    self._points.append(aa)
            else:
                raise TypeError("invalid input type(s)")

    def __repr__(self):
        return "[" + ", ".join([p.__str__() for p in self._points]) + "]"

    @property
    def len(self):
        if self._points:
            return len(self._points)

    @property
    def norm(self):
        if self._points:
            if len(self._points) == 1:
                return 0
            elif 2 <= len(self._points):
                return sum(self._points[i].distance_from(self._points[i+1])
                           for i in range(len(self._points)-2))

    @property
    def points(self):
        if self._points:
            return self._points

    def append(self, *args):
        """Append points, sections or lines"""
        if args:
            if all(isinstance(a, (Point, Section, Line)) for a in args):
                for a in args:
                    if isinstance(a, Point):
                        self._points.append(a)
                    elif isinstance(a, Section):
                        self._points.append(a.this)
                        self._points.append(a.that)
                    elif isinstance(a, Line):
                        for p in a.points:
                            self._points.append(p)
            else:
                raise TypeError("invalid input type(s)")

    def dedupe(self):
        """Remove the consecutively identical points in line."""
        if 2 <= len(self._points):
            for i in range(len(self._points)-2):
                if self._points[i] == self._points[i+1]:
                    self._points.pop(i)


class Polygon(Line):
    def __init__(self, *args):
        super(Polygon, self).__init__(a for a in args)
        # Ensure the last point overlapped with the first.
        if self._points:
            if self._points[0] != self._points[-1]:
                self._points.append(self._points[0])

    def area(self, ref=Point(0, 0)):
        # Note that the last point is circle back to the first.
        # Also recall that the area of Section is a vector hence could be negative.
        # Here we supply positive area numbers instead
        if not isinstance(ref, Point):
            raise TypeError("invalid input type: %s" % type(ref).__name__)
        if self.len <= 3:
            return 0
        try:
            ans = abs(sum(Section(self._points[i], self._points[i+1]).area(ref)
                          for i in range(self.len-2)))
            return round(ans, SIGNIFICANT)
        except Exception as error:
            print(error)


class Triangle(Polygon):
    pass


class Rectangle(Polygon):
    pass


class Circle(Polygon):
    pass
