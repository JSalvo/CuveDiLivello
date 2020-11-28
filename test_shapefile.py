import shapefile
import shutil

shutil.rmtree('shapefiles', ignore_errors=True)

# Creo uno shapefile che contenga polilinee
w = shapefile.Writer("shapefiles/test/testfile", 3)

"""
Field type: the type of data at this column index. Types can be:
"C": Characters, text.
"N": Numbers, with or without decimals.
"F": Floats (same as "N").
"L": Logical, for boolean True/False values.
"D": Dates.
"M": Memo, has no meaning within a GIS and is part of the xbase spec instead.
"""

w.field("ID", "N")


w.record(1)
w.line([[[2,1], [1,3], [2,5], [3,3], [2,1]]])

w.record(2)
w.line([[[2,4], [6,7], [3,2], [2,4]]])

w.close()
