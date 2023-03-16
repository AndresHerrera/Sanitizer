CREATE DATABASE actiontracker
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

CREATE EXTENSION postgis;



CREATE TABLE custom_geofences (
    id SERIAL PRIMARY KEY,
    clientid INTEGER,
    name TEXT,
    geom geometry(MultiPolygon, 4326)
);
