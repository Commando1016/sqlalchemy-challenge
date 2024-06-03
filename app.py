# Import the dependencies
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

# Import SQLAlchemy libraries for ORM (Object Relational Mapper) and database manipulation
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

# Create engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables into SQLAlchemy ORM
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/start'>/api/v1.0/&lt;start&gt;</a><br/>"
        f"<a href='/api/v1.0/start/end'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
    # Calculate the date one year ago from the last date in database
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query precipitation data for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert query results to dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query all stations
    stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (tobs) for the most active station for the last year."""
    # Calculate the date one year ago from the last date in database
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query temperature data for the most active station for the last year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()

    # Convert query results to dictionary
    tobs_dict = {date: tobs for date, tobs in tobs_data}
    
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return TMIN, TAVG, TMAX for a given start date."""
    # Query temperature data for the given start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert query result to a dictionary
    temperature_data = []
    for min_temp, avg_temp, max_temp in results:
        temperature_data = {
            "TMIN": min_temp,
            "TAVG": avg_temp,
            "TMAX": max_temp
        }
    
    return jsonify(temperature_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return TMIN, TAVG, TMAX for a given start-end date range."""
    # Query temperature data for the given start and end date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert query result to a dictionary
    temperature_data = []
    for min_temp, avg_temp, max_temp in results:
        temperature_data = {
            "TMIN": min_temp,
            "TAVG": avg_temp,
            "TMAX": max_temp
        }
    
    return jsonify(temperature_data)

if __name__ == '__main__':
    app.run(debug=True)