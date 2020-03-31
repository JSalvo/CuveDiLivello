import pylab
from pylab import *
from struct import unpack, calcsize
import datetime

time_start = datetime.datetime.now()

def writeTrianglePatch(p1, p2, p3, resolution, destination):
	if resolution > 1:
		pm1 = ((p1[0] + p2[0])/2.0, (p1[1] + p2[1])/2.0, (p1[2] + p2[2])/2.0)
		pm2 = ((p2[0] + p3[0])/2.0, (p2[1] + p3[1])/2.0, (p2[2] + p3[2])/2.0)
		pm3 = ((p3[0] + p1[0])/2.0, (p3[1] + p1[1])/2.0, (p3[2] + p1[2])/2.0)

		writeTrianglePatch(p1, pm1, pm3, resolution - 1, destination)
		writeTrianglePatch(pm1, p2, pm2, resolution - 1, destination)
		writeTrianglePatch(pm2, p3, pm3, resolution - 1, destination)
		writeTrianglePatch(pm1, pm2, pm3, resolution - 1, destination)
	else:
		v1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
		v2 = (p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2])

		normal = (v1[1] *v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0])

		destination.write("    facet normal %f %f %f\n"%normal)
		destination.write("        outer loop\n")
		destination.write("            vertex %f %f %f\n"%(p1[0], p1[1], p1[2]/100.0))
		destination.write("            vertex %f %f %f\n"%(p2[0], p2[1], p2[2]/100.0))
		destination.write("            vertex %f %f %f\n"%(p3[0], p3[1], p3[2]/100.0))
		destination.write("        endloop\n")

def writeSquarePatch(p1, p2, p3, p4, resolution, destination):
	pm = [0, 0, 0, 0]

	for i in range(0, 3):
		pm[i] = (p1[i] + p2[i] + p3[i] + p4[i])/4.0

	writeTrianglePatch(p1, p2, pm, resolution, destination)
	writeTrianglePatch(p2, p3, pm, resolution, destination)
	writeTrianglePatch(p3, p4, pm, resolution, destination)
	writeTrianglePatch(p4, p1, pm, resolution, destination)


"""
Assunzioni:
1 - La matrice contiene almeno una figura da cui estrarre il contorno
2 - Il "bordo" della matrice e' di tutti 0


SO
46 01' 12" N
10 13' 12" E

SE
46 01' 12" N
10 22' 33" E

NE
46 05' 33" N
10 22' 33" E
1
N0
46 05' 33" N
10 13' 12" E

Larghezza 187
Altezza 87

x: 264 colonne
y: 1089 righe

Angolo in alto a sinistra:


"""


f = open("N46E010.hgt", "rb")
m = []
for r in range(0, 1201):
    row = f.read(1201*2)
    rm = []
    for c in range(0, 1201):
        (v, ) = unpack(">h", row[ c*calcsize(">h"): c*calcsize(">h") + calcsize(">h")])
        rm.append(100 if v<0 else v)

    m.append(rm)

matrice_sorgente = m

#ono = []
ono400 = []
ono450 = []
ono500 = []

# Nella matrice inserisco una cornice di tutti 0
def inserisciCornice(m):
	w = len(m[0])-1
	h = len(m) - 1
	for i in range(0, len(m)):
		m[i][0] = 0
		m[i][w] = 0

	for j in range(0, len(m[0])):
		m[0][j] = 0
		m[h][j] = 0


def estraiQuota(m, quota):
	matrice = []

	for i in range(0, len(m)):
		matrice.append([])
		for j in range(0, len(m[0])):
			if m[i][j] >= quota:
				matrice[i].append(1)
			else:
				matrice[i].append(0)
	return matrice


def get_sub_map(m, istart, jstart, hoffset, voffset):
        result = []
        for i in range(0, hoffset):
                result.append([])
                for j in range(0, voffset):
                        result[i].append(m[istart + i][jstart + j])
        return(result)



"""


for row in range(0, 87):
	ono400.append([])
	for column in range(0, 187):
		if m[1089+row][264+column] > 1000:
			ono400[row].append(1)
		else:
			ono400[row].append(0)

for row in range(0, 87):
	ono450.append([])
	for column in range(0, 187):
		if m[1089+row][264+column] > 1050:
			ono450[row].append(1)
		else:
			ono450[row].append(0)

for row in range(0, 87):
	ono500.append([])
	for column in range(0, 187):
		if m[1089+row][264+column] > 1100:
			ono500[row].append(1)
		else:
			ono500[row].append(0)

"""




# Normalizzo
"""
for i in range(0, 1201):
    for j in range(0, 1201):
        m[i][j] = (m[i][j] + 32767) / 32767.0
"""

# Seguono alcune matrici campione (test case), da utilizzare per testare l'algoritmo che trova il contorno di un'immagine
mk = m

m = [\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],\
[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],\
[0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],\
[0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],\
[0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],\
[0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],\
[0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],\
[0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],\
[0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

x = 2

m2 = [\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, x, x, 0, 0, 0],\
[0, 0, 0, 0, x, x, 0, x, 1, x, 0, 0, 0],\
[0, 0, 0, 0, 0, x, x, x, x, x, 0, 0, 0],\
[0, 0, 0, 0, 0, x, x, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, x, x, x, x, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

m3 = [\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],\
[0, 4, 4, 4, 0, 0, 0, 0, 1, 1, 1, 0, 0],\
[0, 4, 4, 4, 0, 0, 0, 0, 1, 1, 1, 0, 0],\
[0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],\
[0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],\
[0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],\
[0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0],\
[0, 0, 2, 2, 2, 0, 0, 0, 3, 3, 3, 0, 0],\
[0, 0, 2, 2, 2, 0, 0, 0, 3, 3, 3, 0, 0],\
[0, 0, 2, 2, 2, 0, 0, 0, 3, 3, 3, 3, 0],\
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# Non ricordo il motivo, ma questo e' un caso infame
bastardo = [\
[1, 0, 0, 0, 0, 0, 0, 0],\
[1, 0, 0, 0, 0, 1, 0, 0],\
[1, 1, 0, 1, 1, 1, 1, 0],\
[1, 0, 0, 1, 1, 1, 1, 1],\
[1, 0, 0, 1, 1, 1, 1, 1],\
[1, 1, 1, 1, 1, 1, 1, 1]]

singolopixel = [[0,0,0,0], [0,1,0,0], [0,0,0,0]]

# Produce il minimo tra due valori
def min2v(v1, v2):
	if v1 != -1:
		if v1 < v2 or v2 == -1:
			return v1
	return v2

# Produce il minimo tra tre valori
def min3v(v1, v2, v3):
	vm = min2v(v1, v2)
	result = min2v(vm, v3)
	return result


# Ho scoperto che due gruppi di pixel si congiungono, per cui aggiorno il valore rappresentante
# uno dei due gruppi cosi' che formino un gruppo unico
def updateGroupsId(dic, oldvalue, newvalue):
	keys = dic.keys()

	for key in keys:
		if dic[key] == oldvalue:
			dic[key] = newvalue



# Marca i pixel appartenenti a dei gruppi di pixel, utilizzando numeri progressivi a partire da 2.
# Modifica m
def findGroups(m):


	"""
	Questo dizionario, conterra' gli id dei gruppi. L'algoritmo scansiona i pixel
	da sinistra a destra, dall'alto in basso, quindi puo' generare id di gruppi di pixel
	che in realta' si riferiscono allo stesso gruppo. L'indice del dizionario si ritrovera'
	quindi nella bitmap, associato all'indice vi e' l'id di gruppo. A diversi indici
	chiaramente puo' essere associato lo stesso gruppo.
	"""
	groupsid = {}

	# Il primo group id e' 2
	groupid = 2

	# Scansiono la matrice (la bitmap) 2 1
	for i in range(0, len(m)):
		for j in range(0, len(m[0])):
			# Per quei pixel (candidati) che hanno il valore a 1 ...
			if m[i][j] == 1:

				povest = -1 # Punto a ovest del candidato
				pnordovest = -1 # Punto a nord-ovest del candidato
				pnord = -1 # Punto a nord del candidato

				if j-1 > -1:
					# ... memorizzo il valore del pixel a ovest
					if m[i][j-1] > 1:
						if m[i][j-1] in groupsid:
							povest = groupsid[m[i][j-1]]
						else:
							povest = m[i][j-1]


					# ... memorizzo il valore del pixel a nord-ovest
					if i-1 > -1:
						if m[i-1][j-1] > 1:
							if m[i-1][j-1] in groupsid:
								pnordovest = groupsid[m[i-1][j-1]]
							else:
								pnordovest = m[i-1][j-1]
				# ... memorizzo il valore del pixel a nord
				if i-1 > -1:
					if m[i-1][j] > 1:
						if m[i-1][j] in groupsid:
							pnord = groupsid[m[i-1][j]]
						else:
							pnord = m[i-1][j]

				if povest == 0:
					povest = -1

				if pnordovest == 0:
					pnordovest = -1

				if pnord == 0:
					pnord = -1

				# Cerco il valore minimo (diverso da -1) tra i pixel a ovest nord-ovest e nord
				# del candidato...
				minp1p2p3 = min3v(povest, pnordovest, pnord)

				# ... se tale valore e' uguale a -1 il pixel non ha pixel predecessori adiacenti
				# (angolo in alto a sinistra della matrice) oppure quelli adiacenti hanno tutti il valore 0 ..
				if minp1p2p3 == -1:
					# ... assegno al pixel il groupid corrente ...
					m[i][j] = groupid
					# ... aggiungo al dizionario il nuovo group id ...
					groupsid[groupid] = groupid
					# ... passo al groupid successivo
					groupid = groupid + 1
					#print "Nuovo Group ID"
				else: # ... altrimenti i pixel adiacenti appartengono gia' ad un gruppo ...
					# ... associo il pixel candidato al gruppo con id minimo
					m[i][j] = minp1p2p3

					# Uniformo l'appartenenza al gruppo per tutti i pixel adiacenti al candidato
					# che di fatto e' il punto di congiungimento tra gruppi che fino ad
					# ora consideravo disgiunti.
					if povest > 0:
						updateGroupsId(groupsid, povest, minp1p2p3)
					if pnordovest > 0:
						updateGroupsId(groupsid, pnordovest, minp1p2p3)
					if pnord > 0:
						updateGroupsId(groupsid, pnord, minp1p2p3)

	for i in range(0, len(m)):
		for j in range(0, len(m[0])):
			if m[i][j] != 0:
				m[i][j] = groupsid[m[i][j]]


	return groupid



def getMatrix(row, column):
	result = []
	for i in range(0, row):
		newrow = []
		for j in range(0, column):
			newrow.append(0)
		result.append(newrow)
	return result

def incrementResolution(m):
	rows = len(m)
	columns = len(m[0])

	result = getMatrix(rows+rows-1, columns+columns-1)

	for i in range(0, rows-1):
		for j in range(0, columns-1):
			result[i*2][j*2] = m[i][j]
			result[i*2][j*2+1] = (m[i][j] + m[i][j+1]) / 2.0
			result[i*2][j*2+2] = m[i][j+1]

			result[i*2+1][j*2] = (m[i][j] + m[i+1][j]) / 2.0
			result[i*2+1][j*2+1] = (m[i][j] + m[i][j+1] + m[i+1][j] + m[i+1][j+1]) / 4.0
			result[i*2+1][j*2+2] = (m[i][j+1] + m[i+1][j+1]) / 2.0

			result[i*2+2][j*2] = m[i+1][j]
			result[i*2+2][j*2+1] = (m[i+1][j] + m[i+1][j] ) / 2.0
			result[i*2+2][j*2+2] = (m[i+1][j+1])
	return result

#Trova il punto di partenza (First Step) dell'algoritmo
def getFirstStep(raster, groupid):
	for j in range(0, len(raster[0])):
		for i in reversed(range(0, len(raster))):
			if raster[i][j] == groupid:
				return (i, j)
	return None

# Il primo Back Step dipende dal metodo di ricerca ed e' sempre sotto il "First Step"
def getFirstBackStep(firststep):
	return(firststep[0]+1, firststep[1])



def nextAround(v):
	if v == (-1, 0):
		return(-1, -1)
	elif v == (-1, -1):
		return(0, -1)
	elif v == (0, -1):
		return(1, -1)
	elif v == (1, -1):
		return(1, 0)
	elif v == (1, 0):
		return(1, 1)
	elif v == (1, 1):
		return(0, 1)
	elif v == (0, 1):
		return(-1, 1)
	elif v == (-1, 1):
		return(-1, 0)



def getNextSteps(step, backstep, raster, groupid):
	v = (backstep[0] - step[0], backstep[1] - step[1])


	for i in range(0, 8):
		na = nextAround(v)

		if (raster[step[0] + na[0]][step[1] + na[1]] == groupid):
			return((step[0] + na[0], step[1] + na[1]), (step[0] + v[0], step[1] + v[1]))
		else:
			v = na

	return(None, None) # Per premessa non si deve arrivare a questa condizione

def getCurrentAround(v1, v2):
	if v1 < 0:
		if v2 > 0:
			return(0)
		elif v2 < 0:
			return(2)
		else:
			return(1)
	elif v1 > 0:
		if v2 > 0:
			return(6)
		elif v2 < 0:
			return(4)
		else:
			return(5)
	else:
		if v2 < 0:
			return(3)
		else:
			return(7)

nextAroundo = [(-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1) ]


def getNextSteps2(step, backstep, raster, groupid):
	v = (backstep[0] - step[0], backstep[1] - step[1])
	l = getCurrentAround(v[0], v[1])

	for i in range(l, 16):
		na = nextAroundo[i+1]

		if (raster[step[0] + na[0]][step[1] + na[1]] == groupid):
			return((step[0] + na[0], step[1] + na[1]), (step[0] + v[0], step[1] + v[1]))
		else:
			v = na

	return(None, None) # Per premessa non si deve arrivare a questa condizione






def getIncomingDirection(step, backstep):
	#print (step[0] - backstep[0], step[1] - backstep[1])
	return(step[0] - backstep[0], step[1] - backstep[1])


def getContour(m, groupid):
	listpoints = []

	step = getFirstStep(m, groupid)

	if step != None:
		backstep = getFirstBackStep(step)

		incomingDirection = getIncomingDirection(step, backstep)

		listpoints.append(step)

		(nstep, nbackstep) = getNextSteps(step, backstep, m, groupid)

		if nstep == None and nbackstep == None: # Singolo Pixel
			return listpoints

		while backstep != nstep and step != nstep:
			listpoints.append(nstep)
			(nstep, nbackstep) = getNextSteps(nstep, nbackstep, m, groupid)

	return listpoints


def compute_contour_line(mappa, visualizza, altitude_begin=400, altitude_offset=2500, countour_line_distance = 50):

    for i in range(0, altitude_offset / countour_line_distance):
        rasterlivello = estraiQuota(mappa, altitude_begin+countour_line_distance*i)

        inserisciCornice(rasterlivello)
        gruppi = findGroups(rasterlivello)

        for j in range(2, gruppi):
	        contour = getContour(rasterlivello, j)
	        for e in contour:
		        visualizza[e[0]][e[1]] = 1

        print "%f%% completato"%(((i+1.0)/ (altitude_offset / countour_line_distance))*100)


# Genera un file da dare in pasto ad un programma di modellazione
def draw3d(m):
	f = file("./mappa.stl", "w")
	f.write("solid 3d\n")
	for i in range(0, len(m)-1):
		for j in range(0, len(m[0])-1):
			writeSquarePatch([j, i+1, m[i+1][j]], [j+1, i+1, m[i+1][j+1]], [j+1, i, m[i][j+1]], [j, i, m[i][j]], 1, f)

	f.write("endsolid 3d\n")
	f.close()

#draw3d(ono)


ono = get_sub_map(mk, 1089, 264, 50, 50)
mappa = incrementResolution(ono)
mappa = incrementResolution(mappa)
mappa = incrementResolution(mappa)
mappa = incrementResolution(mappa)


visualizza = getMatrix(len(mappa), len(mappa[0]))
compute_contour_line(mappa, visualizza)

time_end = datetime.datetime.now()

print("Programma eseguito in: ")
print((time_end - time_start).total_seconds())

matshow(visualizza)
show()
