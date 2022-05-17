from unittest import result
import numpy as np
import pandas as pd
import datetime as dt
from requests import session

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    print(Base.classes.keys())

    # Dict with date as the key and prcp as the value 
    prev_last_date = dt.date(2017, 8, 23) - dt.timedelta(days= 365)
    query_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_last_date).all()
    prcp_dict = {}
    for result in query_results:
        prcp_dict[result[0]] = result[1]

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#    * Query for the dates and temperature observations from the last year.
    session = Session(engine)
    prev_last_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > prev_last_date).\
        order_by(Measurement.date).all()

#     * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
# #   * Return the json representation of your dictionary.
    session.close()
    """
    tobs_dict = {}
    for result in temperature:
        tobs_dict[result[0]] = result[1]
    """
    tobs_dict = list(np.ravel(temperature))
    return jsonify(tobs_dict)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def tempTrip1(start=None, end=None):
    select_statement = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    session = Session(engine)
    if not end:
        # This logic is for when someone did not put in a end date

        start  = dt.datetime.strptime(start, "%Y-%m-%d")
        result  = session.query(*select_statement).filter(Measurement.date >= start).all()
        session.close()
        start_only = list(np.ravel(result))
        return jsonify(start_only)
    
    # This logic is for when both start and end date are included
    # start  = dt.datetime.strptime(start, "%m%d%Y")
    start  = dt.datetime.strptime(start, "%Y-%m-%d")
    end  = dt.datetime.strptime(end, "%Y-%m-%d")
    result  = session.query(*select_statement).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    start_end = list(np.ravel(result))
    return jsonify(start_end)

    session.close()

    

if __name__ == "__main__":
    app.run(debug=True)

