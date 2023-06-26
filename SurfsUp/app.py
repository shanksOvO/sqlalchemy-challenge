from flask import Flask, jsonify
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Create your welcome endpoint with the several different routes
@app.route('/')
def welcome():
    return (
        f"Weclome to the Hawaiian climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2010-01-01<br/>"
        f"/api/v1.0/start/2010-01-01/end/2017-08-23"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp from measurements table
    date_prcp = session.query(measurement.date, measurement.prcp).all()

    session.close()

    # Create dictionary with dates as keys and prcp as values
    precipitation_data = {}
    for date, prcp in date_prcp:
        precipitation_data[date] = prcp

    return jsonify(precipitation_data)


@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the entire station table
    station_names = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_names))

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Starting from the most recent data point in the database.
    latest_date = dt.date(2017, 8, 23)

    # Calculate the date one year from the last date in data set.
    year_ago = latest_date - dt.timedelta(days=365)

    # Query the temperature observations for the most active station in the last year
    temperature_observations = session.query(measurement.date, measurement.tobs).\
        filter_by(station="USC00519281").filter(measurement.date >= year_ago).all()

    session.close()

    # Create dictionary with dates as keys and temperature observations as values
    tobs_data = {}
    for date, tobs in temperature_observations:
        tobs_data[date] = tobs

    return jsonify(tobs_data)

@app.route('/api/v1.0/start/<start>')
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the date greater than or equal to start
    sel = [
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)
    ]

    start_stats = session.query(*sel).filter(measurement.date >= start).all()

    if start_stats:
        start_dict = {
            "TMIN": start_stats[0][0],
            "TAVG": start_stats[0][1],
            "TMAX": start_stats[0][2]
        }
        return jsonify(start_dict)
    else:
        return jsonify({"error": f"No data found for start date: {start}"}), 404

    session.close()

@app.route('/api/v1.0/start/<start>/end/<end>')
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the date between start and end (inclusive)
    sel = [
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)
    ]

    start_end_stats = session.query(*sel).filter(measurement.date.between(start, end)).all()

    if start_end_stats:
        start_end_dict = {
            "TMIN": start_end_stats[0][0],
            "TAVG": start_end_stats[0][1],
            "TMAX": start_end_stats[0][2]
        }
        return jsonify(start_end_dict)
    else:
        return jsonify({"error": f"No data found for start date: {start} and end date: {end}"}), 404

    session.close()


if __name__ == '__main__':
    app.run(debug=True)
