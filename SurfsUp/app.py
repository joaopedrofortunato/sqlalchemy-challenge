# Import the dependencies.

from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# DRY
#################################################

most_active_stations = session.query(measurement.station, func.count(measurement.station)).\
group_by(measurement.station).\
order_by(func.count(measurement.station).desc()).\
all()

session.close()

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        # Return all the available routes
        """Available routes: <br/>"""
        """<br/>"""
        "/api/v1.0/precipitation <br/>"
        "/api/v1.0/stations <br/>"
        "/api/v1.0/tobs <br/>"
        "/api/v1.0/&lt;start&gt; <br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt; <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return the precipitation data as json

    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    session.close()

    precipitation = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= one_year_ago).\
    order_by(measurement.date).all()

    session.close()

    return jsonify(dict(precipitation))

@app.route("/api/v1.0/stations")
def stations():
    # Return the stations data as json
    
    stations = session.query(station.station).all()
    stations_str = [str(s[0]) for s in stations]

    session.close()

    return jsonify(stations_str)

@app.route("/api/v1.0/tobs")
def tobs():
    # Return the temperature data as json

    station_temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.station == most_active_stations[0][0]).\
    all()

    session.close()

    results = list(np.ravel(station_temp))

    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start(start):
    # Return the temperature data for a specified start date as json

    result = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.station == most_active_stations[0][0],\
           measurement.date >= start).\
    all()

    session.close()

    results = list(np.ravel(result))

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Return the temperature data for a specified start and end date as json

    result = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.station == most_active_stations[0][0],\
           measurement.date >= start, measurement.date <= end).\
    all()

    session.close()

    results = list(np.ravel(result))

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
