from gis.geocoder import GeoCoder

geo = GeoCoder()

result = geo.get_coordinates("Bansgaon")

print(result)