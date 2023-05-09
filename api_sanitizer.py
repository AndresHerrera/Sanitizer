from flask import Flask, request, jsonify
import geopandas as gpd
from sqlalchemy import create_engine, text as sql_text
from shapely.geometry import Point

app = Flask(__name__)


# Load shapefile into a geopandas dataframe
# shapefile = gpd.read_file("path/to/shapefile.shp")
# Load GeoPackage into a geopandas dataframe
# geopackage = gpd.read_file("path/to/geopackage.gpkg", layer="layer_name")

# data source: https://gadm.org/data.html
geodataterrain = gpd.read_file("db_fences/gadm_410.gpkg", layer="gadm_410")
geodataoceans = gpd.read_file("db_fences/eez_v11.gpkg", layer="eez_v11")

password='remplaceporpasswordaca'
# Connect to PostGIS database using sqlalchemy
engine = create_engine('postgresql://dev_crud_user:'+password+'@dev01.actiontracker.es:5432/ActionTracker', pool_size=20, max_overflow=30)

# Open a connection to the database
#with engine.connect() as conn:

#data source https://www.marineregions.org/downloads.php

@app.route('/api/coords', methods=['POST'])
def get_coords():
    data = request.get_json()

    lat = data['latitude']
    lon = data['longitude']

    # Create a shapely Point object from the lat/lon coordinates
    point = Point(lon, lat)
    # Use the geopandas "contains" method to check if the point intersects with any polygons in the shapefile
    gdfterrain = geodataterrain.contains(point)
    gdfocean = geodataoceans.contains(point)
    # Get the index of the first polygon that the point intersects with
    #print(gdfterrain)
    #print(gdfocean)
    
    # Define SQL query to get data from PostGIS layer
    query =  "SELECT * FROM public.geosanitizadora WHERE ST_Intersects(\"geomUbicacion\", ST_GeomFromText('{}', 4326))".format(point.wkt)
    #
        
    # Read data into geopandas dataframe
    gdfpostgis = gpd.read_postgis(sql=sql_text(query), con=engine.connect(), geom_col='geomUbicacion')
    #print(gdfpostgis)

    response={'latitude': lat, 'longitude': lon}

    if gdfterrain.any():
        terrain_index = gdfterrain[gdfterrain == True].index[0]
        # Get the attribute value for the specified column from the intersecting polygon
        continent = geodataterrain.loc[terrain_index, "CONTINENT"]
        alevel0 = geodataterrain.loc[terrain_index, "NAME_0"]
        alevel1 = geodataterrain.loc[terrain_index, "NAME_1"]
        alevel2 = geodataterrain.loc[terrain_index, "NAME_2"]
        alevel3 = geodataterrain.loc[terrain_index, "NAME_3"]
        response = {'continent': continent,'alevel0': alevel0, 'alevel1': alevel1, 'alevel2': alevel2, 'alevel3': alevel3, 'latitude': lat, 'longitude': lon}

    if gdfocean.any():
        ocean_index = gdfocean[gdfocean == True].index[0]
        oceant1= geodataoceans.loc[ocean_index, "TERRITORY1"]
        response = {'oceant1': oceant1,'latitude': lat, 'longitude': lon}

    if gdfpostgis['idUbicacion'].all() > 0:
        if gdfpostgis[gdfpostgis == True].size > 0:
            fence_index = gdfpostgis[gdfpostgis == True].index[0]
            idUbicacion= gdfpostgis.loc[fence_index, "idUbicacion"]
            idUbicacionPadre= gdfpostgis.loc[fence_index, "idUbicacionPadre"]
            nomUbicacion= gdfpostgis.loc[fence_index, "nomUbicacion"]
            idEmpresa= gdfpostgis.loc[fence_index, "idEmpresa"]
            habilitado= gdfpostgis.loc[fence_index, "habilitado"]
            indSanitizador= gdfpostgis.loc[fence_index, "indSanitizador"]
            response = {'idUbicacion': idUbicacion,'idUbicacionPadre': idUbicacionPadre,'nomUbicacion': nomUbicacion,'idEmpresa': idEmpresa,'habilitado': habilitado,'indSanitizador': indSanitizador,'latitude': lat, 'longitude': lon}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)