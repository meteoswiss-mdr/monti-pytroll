import datetime as dt

from mpop.satellites import GenericFactory as GF

tslot = dt.datetime(2015, 7, 7, 16)
glbl = GF.create_scene("Meteosat-9", "", "seviri", tslot, None)
glbl.load([0.6, 0.8, 10.8], area_def_names=["euro4",])

#lcl_bil = glbl.project('euro4', nprocs=1, mode="bilinear", radius=50e3)
lcl_bil = glbl.project('euro4', nprocs=1, mode="ewa")
img = lcl_bil.image.overview()
img.show()
