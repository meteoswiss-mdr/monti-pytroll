from mpop.satellites import GeostationaryFactory

year=2015
month=7
day=24
day=24
hour=14
minute=15

from datetime import datetime

time=datetime(year, month, day, hour, minute, 0)

global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time)

print global_data.loaded_channels

print global_data.channels[1].name
print global_data.channels[2].name
print global_data.channels[3].name

print global_data.load(["VIS006"])

for lchan in global_data.loaded_channels():
    print lchan.name
