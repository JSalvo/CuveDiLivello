import numpy as np

import matplotlib.pyplot as plt
import random

# f(t) = z, produce un valore costante indipendentemente dal parametro t
class CostantFunction:
    def __init__(self, c):
        self._c = c
    def z(self, t):
        return self._c

# f(t) = z, funzione lineare
class LinearFunction:
    def __init__(self, p1, p2): # Vincolo: p1 e p2, devono avere ascisse diverse
        if p1[0] == p2[0]:
            1 / 0 # Poi mettere eccezione

        self._p1 = p1

        deltat = p2[0] - p1[0]
        deltaz = p2[1] - p1[1]
        self._delta = (1.0 * deltaz) / deltat
    def z(self, t):
        result = self._p1[1] + (t - self._p1[0]) * self._delta

        return( result if result > 0 else 0 )

# f(t) = z, funzione quadratica (o parabola)
class SquareFunction:
    def __init__(self, p1, p2, p3): # Vincolo p1, p2 e p3, non devono avere la stessa ordinata
        if (p1[1] == p2[1] and p2[1] == p3[1]):
            pass

        m_list = [[p1[0]**2, p1[0], 1], [p2[0]**2, p2[0], 1], [p3[0]**2, p3[0], 1]]
        A = np.array(m_list)
        B = np.array([p1[1], p2[1], p3[1]])
        X = np.linalg.inv(A).dot(B)

        self._a = X[0]
        self._b = X[1]
        self._c = X[2]

    def z(self, t):
        result = self._a * t**2 + self._b * t + self._c

        return( result if result > 0 else 0 )

# Questa classe, permette di rappresentare un pixel "void" della mappa di
# altitudine.
class PixelVoid:
    def __init__(self, x=None, y=None, grid=None): # Nella fase di test, non ho bisogno delle coordinate
        self._x = x
        self._y = y
        self._grid = grid
        self._weights = []
    # Tutti i valori assegnabili a questo void per interpolazione, vengono
    # associati tramite questa funzione e poi mediati.
    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def addWeight(self, w):
        self._weights.append(w)
    # Media i pesi associati a questo void, producendo una stima della quota
    # ivi passante
    def calcZ(self):
        if self._weights > 0:
            z = 0
            len_w = len(self._weights)
            for w in self._weights:
                z = z + (1.0 * w) / len_w
            return z
        else:
            return None
    def writeInterpolatedValuedOnTheGrid(self):
        z = self.calcZ()
        if z != None:
            self._grid[self._y][self._x] = z
        else:
            self._grid[self._y][self._x] = 0

class PixelVoidBucket:
    def __init__(self, grid):
        self._allVoids = {}
        self._grid = grid
    def getPixelVoid(self, x, y):
        key = "%s,%s"%(x, y)
        if key in self._allVoids:
            return self._allVoids[key]
        else:
            newPixelVoid = PixelVoid(x, y, self._grid)
            self._allVoids[key] = newPixelVoid
            return newPixelVoid
    def fillAllVoids(self):
        for key in self._allVoids:
            self._allVoids[key].writeInterpolatedValuedOnTheGrid()


# Calcola per interpolazione, tramite la funzione f, i valori nell'intervallo
# [void0, voidn]
def get_weights(void0, voidn, f):
    weights = []
    for x in range(void0, voidn + 1):
        weights.append(f.z(x))

    return weights

# Dati massimo tre punti, produce una funzione costante, lineare o quadratica
# da utilizzare per interpolare nell'intervallo dei void
def get_function(points): #max 3 points
    points_length = len(points)

    if points_length == 0:
        f = CostantFunction(0)
    # FUNZIONE COSTANTE
    elif points_length == 1:
        print("Ok sono qui!")

        f = CostantFunction(points[0][1])
    # FUNZIONE LINEARE se p1 e p2 non hanno la stessa ordinata, altrimenti
    # degenera nella funzione costante
    elif points_length == 2:
        p1 = points[0]
        p2 = points[1]

        f = LinearFunction(p1, p2)
    # FUNZIONE QUADRATICA se p1, p2 e p3 non sono allineati, altrimenti puo'
    # degnerare in una funzione costante o in una funzione lineare
    elif points_length == 3:
        p1 = points[0]
        p2 = points[1]
        p3 = points[2]

        f = SquareFunction(p1, p2, p3)
    else:
        1/0 # Non deve succedere

    return(f)

def process_scan_line(points, void0, voidn, voids): # void0 < voidn
    if void0 > voidn:
        1 / 0 # Poi mettere eccezione

    f1 = None
    f2 = None

    if len(points) < 4:
        f1 = get_function(points)
        print(f1)

        weights = get_weights(void0, voidn, f1)
        print("Pesi")
        print(weights)

        for i in range(0, len(voids)):
            voids[i].addWeight(weights[i])

    elif len(points) == 4:
        f1 = get_function(points[0:3])
        f2 = get_function(points[1:4])

        weights1 = get_weights(void0, voidn, f1)
        weights2 = get_weights(void0, voidn, f2)

        for i in range(0, len(voids)):
            voids[i].addWeight(weights1[i])
            voids[i].addWeight(weights2[i])
    else:
        1 / 0 # Massimo 4 punti

# Test1
def test1():
    points = [[0, 4]]
    voids = [PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid()]

    process_scan_line(points, 1, 4, voids) # void0 < voidn

    #plt.hist([points[0][1]])

    estremi = [4]

    filled_hole = []
    for i in  range(0, len(voids)):
        filled_hole.append(voids[i].calcZ())
        estremi.append(0)

    filled_hole.insert(0, 0)
    x = [1,2,3,4,5]
    plt.bar(x, estremi)
    plt.bar(x, filled_hole)

    plt.show()

def test2():
    points = [[0, 4], [9, 8]]
    voids = [PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid()]

    process_scan_line(points, 1, 8, voids) # void0 < voidn

    #plt.hist([points[0][1]])

    estremi = [4]

    filled_hole = []
    for i in  range(0, len(voids)):
        filled_hole.append(voids[i].calcZ())
        estremi.append(0)

    estremi.append(8)

    filled_hole.insert(0, 0)
    filled_hole.append(0)

    x = [1,2,3,4,5, 6, 7, 8, 9, 10]
    plt.bar(x, estremi)
    plt.bar(x, filled_hole)

    plt.show()

def test3():
    points = [[0, 4], [1, 3], [9, 8]]
    voids = [PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid()]

    process_scan_line(points, 2, 8, voids) # void0 < voidn

    #plt.hist([points[0][1]])

    estremi = [4, 3]

    filled_hole = []
    for i in  range(0, len(voids)):
        filled_hole.append(voids[i].calcZ())
        estremi.append(0)

    estremi.append(8)

    filled_hole.insert(0, 0)
    filled_hole.insert(0, 0)
    filled_hole.append(0)

    x = [1,2,3,4,5, 6, 7, 8, 9, 10]
    plt.bar(x, estremi)
    plt.bar(x, filled_hole)

    plt.show()


def test4():
    points = [[0, 3], [8, 8], [9, 4]]
    voids = [PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid()]

    process_scan_line(points, 1, 7, voids) # void0 < voidn

    #plt.hist([points[0][1]])

    estremi = [3]

    filled_hole = []
    for i in  range(0, len(voids)):
        filled_hole.append(voids[i].calcZ())
        estremi.append(0)

    estremi.append(8)
    estremi.append(4)

    filled_hole.insert(0, 0)
    filled_hole.append(0)
    filled_hole.append(0)

    x = [1,2,3,4,5, 6, 7, 8, 9, 10]
    plt.bar(x, estremi)
    plt.bar(x, filled_hole)

    plt.show()

def test5():
    points = [[0, 5], [1, 3], [8, 8], [9, 4]]
    voids = [PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid(), PixelVoid()]

    process_scan_line(points, 2, 7, voids) # void0 < voidn

    #plt.hist([points[0][1]])

    estremi = [5, 3]

    filled_hole = []
    for i in  range(0, len(voids)):
        filled_hole.append(voids[i].calcZ())
        estremi.append(0)

    estremi.append(8)
    estremi.append(4)

    filled_hole.insert(0, 0)
    filled_hole.insert(0, 0)

    filled_hole.append(0)
    filled_hole.append(0)

    x = [1,2,3,4,5, 6, 7, 8, 9, 10]
    plt.bar(x, estremi)
    plt.bar(x, filled_hole)

    plt.show()


def myrandom(minv, maxv):
    return( int(round(minv + random.random() * (maxv - minv))) )

def test_random():
    l = 5   # altezza minima della colonna
    h = 20  # altezza massima della colonna
    vn = 15 # Numero di void massimo

    pre_points = []
    for i in range(0, myrandom(0, 2)):
        pre_points.append([i, myrandom(l, h)])

    voids = []
    for i in range(0, myrandom(1, vn)):
        voids.append(PixelVoid())

    post_points = []
    for i in range(0, myrandom(0, 2)):
        post_points.append([len(pre_points) + len(voids)+i, myrandom(l, h)])

    process_scan_line(pre_points + post_points, len(pre_points), len(pre_points)+len(voids)-1, voids) # void0 < voidn

    estremi = []
    filled_hole = []
    for p in pre_points:
        estremi.append(p[1])
        filled_hole.append(0)

    for i in  range(0, len(voids)):
        filled_hole.append(voids[i].calcZ())
        estremi.append(0)

    for p in post_points:
        estremi.append(p[1])
        filled_hole.append(0)

    x = []
    for i in range(0, len(filled_hole)):
        x.append(i)

    plt.bar(x, estremi)
    plt.bar(x, filled_hole)

    plt.show()


#test_random()
