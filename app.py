# imports
import pandas as pd
import numpy as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func 

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create flask app
app = Flask(__name__)

@app.route("/")
def Homepage():
    return (
        f"All routes that are available:"
        f"Precipitation data by date (/api/v1.0/precipitation)"
        f"List of Stations (/api/v1.0/stations)"
        f"Temperature measurements from active stations (/api/v1.0/tobs)"
        f"Min, max, and mean temp for date range (/api/v1.0/<start) and (/api/v1.0/<start>/<end)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").all()
    
    # convert to python dict to jsonify
    prcp_data = {}
    for date,prcp  in precipitation_data:
        prcp_data["date"] = date
        prcp_data["prcp"] = prcp

    session.close()

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    total_stations = session.query(Measurement.station).distinct().all()
    
    station_list = list(total_stations[0])
    station_dict = {}
    station_dict['stations'] = station_list
    
    session.close()

    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    max_station_measurements = session.query(Measurement.station, Measurement.tobs).filter(Measurement.station == "USC00519281").all()
    
    tobs_list = list(max_station_measurements[1])
    tobs_max = max(tobs_list)
    tobs_min = min(tobs_list)
    tobs_mean = pd.mean(tobs_list)


    tobs_dict = {
        'Max Temp': tobs_max,
        'Min Temp': tobs_min,
        'Mean Temp': tobs_mean,
    }
    
    session.close()

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def daterange(start):
    session = Session(engine)
    TMIN = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    TMAX = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    TAVG = session.query(func.mean(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    tobs_dict = {
        "Min Temp": TMIN,
        "Max Temp": TMAX,
        "Avg Temp": TAVG
    }

    session.close()

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>/<end>")
def daterange(start, end):
    session = Session(engine)
    TMIN = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    TMAX = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    TAVG = session.query(func.mean(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    tobs_dict = {
        "Min Temp": TMIN,
        "Max Temp": TMAX,
        "Avg Temp": TAVG
    }

    session.close()

    return jsonify(tobs_dict)


if __name__ == '__main__':
    app.run(debug=True)

    






