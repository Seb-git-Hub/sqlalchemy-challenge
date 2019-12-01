import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    former_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= former_year).all()
    session.close()
    tuple_list=[]
    for date, prcp in precipitation:
        precipitation_dict={}
        precipitation_dict["date"]=date
        precipitation_dict["precipitation"]=prcp
        tuple_list.append(precipitation-dict)

    # Dict with date as the key and prcp as the value
    #precip = dict(tuple_list)
    #precip = {date: prcp for date, prcp in precipitation}
    return jsonify(tuple_list)
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    """Return a list of stations.""" 
    results = Session.query(Station.station).all()
    # Unravel results into a 1D array and convert to a list
    stations=list(np.ravel(results))
    return jsonify(stations)
    session.close()
     #tttt
@app.route("/api/v1.0/tobs")
def temp_monthly():
    session=Session(engine)
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    former_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the primary station for all tobs from the last year
    results = Session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= former_year).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    # Return the results
    return jsonify(temps)
    session.close()
@app.route("/api/v1.0/temp/start")
@app.route("/api/v1.0/temp/start end")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    selquery = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = Session.query(*selquery).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
    # calculate TMIN, TAVG, TMAX with start and stop
    results = Session.query(*selquery).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)
if __name__ == '__main__':
    app.run(debug=True)
    #app.run(threaded=False, processes=1)