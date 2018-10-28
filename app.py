import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


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
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Add start date<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Add start date/end date for specific time frame, use only year and month in this format 2017-04")

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()

    # Convert list of tuples into normal list
    precipitation =  list(np.ravel(results))

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    stations_list = []
    for station in station_results:
        station_dict = {}
        station_dict["station"] = station[0]
        station_dict["counts"] = station[1]
        stations_list.append(station_dict)
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def last_year():
    results = session.query(Measurement.date, func.avg(Measurement.tobs)).filter(func.strftime("%Y-%m", Measurement.date)>="2016-08").filter_by(station = "USC00519281").group_by(Measurement.date).all()
    years_list =[]
    for result in results:
        years_dict = {}
        years_dict["date"] = result[0]
        years_dict["temp"] = result[1]
        years_list.append(years_dict)
    return jsonify(years_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    min_temp = session.query(func.min(Measurement.tobs)).filter(func.strftime("%Y-%m", Measurement.date)>= start).all()
    max_temp = session.query(func.max(Measurement.tobs)).filter(func.strftime("%Y-%m", Measurement.date)>= start).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(func.strftime("%Y-%m", Measurement.date)>= start).all()
  
    return (f"Lowest Temp:{min_temp}<br/>"
            f"Highest Temp:{max_temp}<br/>"
            f"Average Temp:{avg_temp}")

@app.route("/api/v1.0/<start>/<end>")
def time_frame(start, end):
    min_temp = session.query(func.min(Measurement.tobs)).filter(func.strftime("%Y-%m", Measurement.date)>= start).filter(func.strftime("%Y-%m", Measurement.date)<= end).filter_by(station = "USC00519281").all()
    max_temp = session.query(func.max(Measurement.tobs)).filter(func.strftime("%Y-%m", Measurement.date)>= start).filter(func.strftime("%Y-%m", Measurement.date)<= end).filter_by(station = "USC00519281").all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(func.strftime("%Y-%m", Measurement.date)>= start).filter(func.strftime("%Y-%m", Measurement.date)<= end).filter_by(station = "USC00519281").all()
  
    return (f"Lowest Temp:{min_temp}<br/>"
            f"Highest Temp:{max_temp}<br/>"
            f"Average Temp:{avg_temp}")
    


if __name__ == '__main__':
    app.run(debug=True)