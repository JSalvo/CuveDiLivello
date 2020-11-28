import shapefile
import shutil

# Creo uno shapefile che contenga polilinee

sf = shapefile.Reader("curve_di_livello/contour")
#sf = shapefile.Reader("shapefiles/test/testfile")
#sf = shapefile.Reader("risultato/contorno")

"""
Field type: the type of data at this column index. Types can be:
"C": Characters, text.
"N": Numbers, with or without decimals.
"F": Floats (same as "N").
"L": Logical, for boolean True/False values.
"D": Dates.
"M": Memo, has no meaning within a GIS and is part of the xbase spec instead.

with sf as shp:
    print(shp)
"""

# Tipo della shape, il test lo sto eseguendo sulla polilinea quindi 3
print("Shapes Type: %s"%(sf.shapeType))

# Rettangolo che contiene l'intero oggetto
print("BBox: %s"%(sf.bbox))

# Recupero i vari oggetti
shapes = sf.shapes()
print("Numero di geometrie: %s\n"%(len(shapes)))

records = sf.records()

fields = sf.fields
print("Campi: %s\n"%fields)

# Itero sui vari oggetti e stampo un po' di informazioni
for i in range(0, len(shapes)):
    if i > 0:
        break
    s = sf.shape(i)

    print("Record -> ID: %s, height: %s"%(records[i][0], records[i][1]))
    print("Tipo: %s"%s.shapeType)
    print("Nome del Tipo: %s"%s.shapeTypeName)
    print("BBox della shape %i: %s"%(i, s.bbox))
    print("Parti: %s"%s.parts)
    print("Numero punti: %s"%len(s.points))
    print("Punti: %s"%s.points)
    print("")

sf.close()
