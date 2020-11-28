import pylab
from pylab import *
from struct import unpack, calcsize
import datetime
import shapefile
import shutil
import fill_gap


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


f = open("N46E010_without_voids.hgt", "rb")
m = []
for r in range(0, 1201):
    row = f.read(1201*2) # Leggo 2402 byte, ossia una riga della matrice
    rm = []
    for c in range(0, 1201):
		# ">h"
		# Unpack, interpreta dei caratteri, come dati binari e permette di converrtili,
		# in base al formato dato. In questo caso, il formato e' ">h" dove il
		# simbolo maggiore sta per BIG-ENDIAN, mentre h, sta per SHORT INT (con segno)
		# Produce una tupla come risultato, anche se viene prodotto un solo
		# ed unico valore

		# Row, contiene le quote altimetriche. Ogni coppia di byte (quindi di caratteri)
		# Rappresenta un valore intero con segno. la funzione calcsize, produce
		# quanti byte servono per una data codifica (">h" BIG-ENDIAN SIGNED SHORT, quindi
		# in questo caso 2 byte)
        (v, ) = unpack(">h", row[ c*calcsize(">h"): c*calcsize(">h") + calcsize(">h")])
        rm.append(v)

    m.append(rm)

matrice_sorgente = m
bucket = fill_gap.PixelVoidBucket(m)

def find_voids_on_row(m, row, i):
	points = []
	voids = []
	void0 = 0
	voidn = 0
	for x in range(i, len(m[row])):
		# Appena trovo un void ...
		if m[row][x] < 0:
			# Se non sono sul bordo ovest ...
			if x > 0:
				# Il punto precedente, non e sicuramente void
				points.append([0, m[row][x-1]])
				void0 = 1 # Indice del primo void
				# Se x e' maggiore di uno, almeno due punti precedono questo void
				# Il punto precedente al void non e' senz'altro void e lo gia'
				# inserito nella lista points, per il punto precedente al precedente vediam:
				if x > 1:
					if m[row][x-2] < 0:
						pass
					else:
						# Il punto precedente al precedente non e' void, quindi
						# lo pre-inserisco nella lista dei points
						points[0][0] = 1
					 	points.insert(0, [0, m[row][x-2]] ) # pre-inserimento
						void0 = 2 # indice del primo void

			# x, in questo moento, identifica il Primo Void in row
			voids.append(bucket.getPixelVoid(x, row))

			# Cerco altri void successivi (e contigui) al primo
			for j in range(x+1, len(m[row])):
				if m[row][j] < 0:
					voids.append(bucket.getPixelVoid(j, row))
				else:
					# Appena trovo un punto non void, esco dal for
					break

			# A questo punto, la sequenza di void che ho raccolto e' "limitata":
			# - o limitata da un punto non void
			# - o limitata dal bordo est della matrice

			# Indice dell'ultimo void
			voidn = len(points) + len(voids) - 1

			# Se il void trovato, non e' sul bordo est della matrice:
			if voids[-1].getX() <  len(m[row]) - 1:
				# Il puno successivo e' senz'altro non void, infatti a causato
				# l'uscita dalla ricorsione nel precedente for. Prendo la z
				# del punto
				nextZ = m[row][voids[-1].getX() + 1]
				# Aggiungo a points questo nuovo punto non void (delimitatore destro
				# della riga di voids)
				points.append([len(points) + len(voids), nextZ])

				# Se dopo il void ci sono almeno due punti prima del bordo est:
				if voids[-1].getX() <  len(m[row]) - 2:
					# Prendo la z del punto che segue il punto che segue il void e...
					nextZ = m[row][voids[-1].getX() + 2]
					if nextZ < 0:
						pass
					else:
						# ...se la z e' non nulla abbiamo un altro punto non void
						# da inserire nella lista points
						points.append([len(points) + len(voids), nextZ])
				# Produco, i points non void, la sequenza di void, l'indice
				# del primo void, l'indice dell'ultimo void, e l'indice del
				# primo non void appena dopo l'ultimo void.
				return( (points, voids, void0, voidn, voids[-1].getX()+1) )

			# Se arrivo in questo punto del programma, signifca che sono arrivato
			# al bordo est della matrice. None in sostanza mi permette di comunicarlo
			# al chiamante della funzione.
			return( (points, voids, void0, voidn, None ) )

	return( ([], [], void0, voidn, None ) )

def find_voids_on_column(m, column, i):
	points = []
	voids = []
	void0 = 0
	voidn = 0
	for y in range(i, len(m)):
		# Appena trovo un void ...
		if m[y][column] < 0:
			# Se non sono sul bordo ovest ...
			if y > 0:
				# Il punto precedente, non e sicuramente void
				points.append([0, m[y-1][column]])
				void0 = 1 # Indice del primo void
				# Se x e' maggiore di uno, almeno due punti precedono questo void
				# Il punto precedente al void non e' senz'altro void e lo gia'
				# inserito nella lista points, per il punto precedente al precedente vediam:
				if y > 1:
					if m[y-2][column] < 0:
						pass
					else:
						# Il punto precedente al precedente non e' void, quindi
						# lo pre-inserisco nella lista dei points
						points[0][0] = 1
					 	points.insert(0, [0, m[y-2][column]] ) # pre-inserimento
						void0 = 2 # indice del primo void

			# x, in questo moento, identifica il Primo Void in row
			voids.append(bucket.getPixelVoid(column, y))

			# Cerco altri void successivi (e contigui) al primo
			for j in range(y+1, len(m)):
				if m[j][column] < 0:
					voids.append(bucket.getPixelVoid(column, j))
				else:
					# Appena trovo un punto non void, esco dal for
					break

			# A questo punto, la sequenza di void che ho raccolto e' "limitata":
			# - o limitata da un punto non void
			# - o limitata dal bordo est della matrice

			# Indice dell'ultimo void
			voidn = len(points) + len(voids) - 1

			# Se il void trovato, non e' sul bordo est della matrice:
			if voids[-1].getY() <  len(m) - 1:
				# Il puno successivo e' senz'altro non void, infatti a causato
				# l'uscita dalla ricorsione nel precedente for. Prendo la z
				# del punto
				nextZ = m[voids[-1].getY() + 1][column]
				# Aggiungo a points questo nuovo punto non void (delimitatore destro
				# della riga di voids)
				points.append([len(points) + len(voids), nextZ])

				# Se dopo il void ci sono almeno due punti prima del bordo est:
				if voids[-1].getY() <  len(m) - 2:
					# Prendo la z del punto che segue il punto che segue il void e...
					nextZ = m[voids[-1].getY() + 2][column]
					if nextZ < 0:
						pass
					else:
						# ...se la z e' non nulla abbiamo un altro punto non void
						# da inserire nella lista points
						points.append([len(points) + len(voids), nextZ])
				# Produco, i points non void, la sequenza di void, l'indice
				# del primo void, l'indice dell'ultimo void, e l'indice del
				# primo non void appena dopo l'ultimo void.
				return( (points, voids, void0, voidn, voids[-1].getY()+1) )

			# Se arrivo in questo punto del programma, signifca che sono arrivato
			# al bordo est della matrice. None in sostanza mi permette di comunicarlo
			# al chiamante della funzione.
			return( (points, voids, void0, voidn, None ) )

	return( ([], [], void0, voidn, None ) )

InterpolazioneOrizzonale = False
InterpolazioneVerticale = False

if InterpolazioneOrizzonale:
	for row in range(0, len(m)):
		i = 0
		while i != None:
			points, voids, void0, voidn, next_i = find_voids_on_row(m, row, i)

			if len(voids) > 0:
				fill_gap.process_scan_line(points, void0, voidn, voids)
			else:
				break

			i = next_i

if InterpolazioneVerticale:
	for column in range(0, len(m[0])):
		j = 0
		while j != None:
			points, voids, void0, voidn, next_i = find_voids_on_column(m, column, j)

			if len(voids) > 0:
				fill_gap.process_scan_line(points, void0, voidn, voids)
			else:
				break

			j = next_i

bucket.fillAllVoids()


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


def get_sub_map(m, x, y, width, height):
        result = []
        for i in range(0, height):
                result.append([])
                for j in range(0, width):
                        result[i].append(m[y + i][x + j])
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


def is_on_the_border(p, hl, vl):
	if p[0] == 1 or p[1] == 1 or p[0] == hl or p[1] == vl:
		return True
	else:
		return False


c1 = [(2,2)]
c2 = [(2,2), (3,3)]
c3 = [(1,1)]
c4 = [(1,1), (2,1)]
c5 = [(2,2), (3,3), (4, 4)]
c6 = [(1,1), (2,1), (1, 3)]
c7 = [(3,3), (1,1), (2,1), (1, 3), (4, 4)]
c8 = [(3,3), (5, 5), (1,1), (2,1), (1, 3), (4, 4)]
c9 = [(3,3), (5, 5), (1,1), (2,1), (1, 3), (4, 4), (8, 8)]

test_cases = [c1, c2, c3, c4, c5, c6, c7, c8, c9];


def find_first_no_border(contour, i, hl, vl):
	for j in range(i, len(contour)):
		if is_on_the_border(contour[j], hl, vl):
			pass
		else:
			return j
	return None

def find_last_no_border(contour, i, hl, vl):
	for j in range(i, len(contour)):
		if is_on_the_border(contour[j], hl, vl):
			return(j-1)

	return len(contour) - 1

def no_border_subset_indices(contour, hl, vl):
	result = []
	stop = False

	i = 0
	while not stop:
		nb1 = find_first_no_border(contour, i, hl, vl)
		if nb1 != None:
			nb2 = find_last_no_border(contour, nb1, hl, vl)
			result.append((nb1, nb2))
			i = nb2+1
		else:
			stop = True

	return result



def compute_contour_line(mappa, visualizza, latN, longE, step, altitude_begin=400, altitude_offset=2500, countour_line_distance = 50, preview=True):
	shutil.rmtree('risultato', ignore_errors=True)
	# Creo uno shapefile che contenga polilinee
	w = shapefile.Writer("risultato/contorno", 3)
	w.field("ID", "N", size=8, decimal=0)
	w.field("height", "N", size=12, decimal=3)
	counter = 0

	for i in range(0, altitude_offset / countour_line_distance):
		altitude = altitude_begin+countour_line_distance*i
		rasterlivello = estraiQuota(mappa, altitude)
		inserisciCornice(rasterlivello)
		gruppi = findGroups(rasterlivello)
		hl = len(mappa[0]) - 2
		vl = len(mappa) - 2

		for j in range(2, gruppi):
			contour = getContour(rasterlivello, j)
			if preview == True:
				subsets = no_border_subset_indices(contour, hl, vl)

				for subset in subsets:
					new_pline = []
					for e in contour[subset[0]:subset[1]+1]:
						new_pline.append([longE + step*e[1], latN - step*e[0]])
						visualizza[e[0]][e[1]] = 1

					w.line([new_pline])
					w.record(counter, altitude)
					counter = counter + 1

		print "%f%% completato"%(((i+1.0)/ (altitude_offset / countour_line_distance))*100)
	w.close()


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

if True == True:

	"""
	latn = 45 + (1/1201.0)*1089
	longo = 10 + (1/1201.0)*264
	bstep = (1/1201.0)*50

	ono = get_sub_map(mk, 1089, 264, 50, 50)
	mappa = incrementResolution(ono)

	lstep = bstep / len(mappa)
	visualizza = getMatrix(len(mappa), len(mappa[0]))
	compute_contour_line(mappa, visualizza, latn, longo, lstep)
	"""

	latN = 47
	longE= 10 + (1/1201.0)*100
	bstep = (1/1201.0)*100

	submap100 = get_sub_map(mk, 100, 0, 100, 100)
	mappa = incrementResolution(submap100)
	#mappa = incrementResolution(mappa)
	#mappa = incrementResolution(mappa)


	lstep = bstep / len(mappa)

	visualizza = getMatrix(len(mappa), len(mappa[0]))
	compute_contour_line(mappa, visualizza, latN, longE, lstep)


	time_end = datetime.datetime.now()

	print("Programma eseguito in: ")
	print((time_end - time_start).total_seconds())

	matshow(visualizza)
	show()


if True == False:
	for test in test_cases:
		result = no_border_subset_indeces(test)
		print(result)

w = shapefile.Writer('shapefiles/test/testfile', 3)
w.close()

if True == False:
	print(mk[0][0])
	print(mk[0][1200])
	print(mk[1200][0])
	print(mk[1200][1200])

#wgs84 to EPSG:4326 python

# +proj=longlat +datum=WGS84 +no_defs
#Proj(init='EPSG:4326')
