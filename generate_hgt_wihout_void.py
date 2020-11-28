import pylab
from pylab import *
from struct import unpack, pack, calcsize
import fill_gap


f = open("N46E010.hgt", "rb")
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

InterpolazioneOrizzonale = True
InterpolazioneVerticale = True

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
f.close()


f = open("N46E010_without_voids.hgt", "wb")

for row in m:
    for value in row:
        f.write(pack(">h", value))

f.close()
