

import math

# from http://www.movable-type.co.uk/scripts/latlong-db.html
# assumes lat/long in degrees, radius in miles
def create_radial_query(lat_in, long_in, radius):
	r_earth = 3959 # in miles

	# create a bounding box first to create a coarse set of posibilities
	# avoids running cosine matching on every point in the db
	maxLat = lat_in + math.degrees(radius/r_earth)
	minLat = lat_in - math.degrees(radius/r_earth)
	maxLon = long_in + math.degrees(math.asin(radius/r_earth) / math.cos(math.radians(lat_in)))
	minLon = long_in - math.degrees(math.asin(radius/r_earth) / math.cos(math.radians(lat_in)))

	query_str = "select *,\
       acos(sin(radians(" + str(lat_in) + "))*sin(radians(facilitylatitude)) + \
       cos(radians(" + str(lat_in) + "))*cos(radians(facilitylatitude))*cos(radians(facilitylongitude)-radians(" + str(long_in) + ")))\
        * " + str(r_earth) + " As D \
		 From campnear_consolidated_toorcamp where \
		acos(sin(radians(" + str(lat_in) + "))*sin(radians(facilitylatitude)) + \
		  	cos(radians(" + str(lat_in) + "))*cos(radians(facilitylatitude))*cos(radians(facilitylongitude) - \
		  		radians(" + str(long_in) + "))) * " + str(r_earth) + " < " + str(radius) + " order by D ;"



	return query_str

