import json

import geopandas as gpd

geodf = gpd.read_file("data/small/Provinsi.shp")

geodf.to_file("data/small/Provinsi.geojson", driver="GeoJSON")
with open("data/small/Provinsi.geojson") as geofile:
    j_file = json.load(geofile)

i = 1
for feature in j_file["features"]:
    feature["id"] = str(i).zfill(2)
    i += 1
