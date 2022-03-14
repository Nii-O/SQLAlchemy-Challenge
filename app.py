from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc


#################################################
# Database
#################################################

database_path= "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
base= automap_base()
base.prepare(engine, reflect=True)
base.classes.keys()
Measurements = base.classes.measurement
Station = base.classes.station
session = Session(engine)

#################################################
# Flask Setup
#################################################
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# 3. Define what routes are available
@app.route("/")
def home():
    return(
        f"Welcome to my Home Page! Here are the available routes.<br/><br/>"

        "Returns precipitation data for the past year.<br/>"
        "/api/v1.0/precipitation<br/><br/>"

        "Returns a list of stations.<br/>"
        "/api/v1.0/stations<br/><br/>"

        "Returns Temperature observations for the most active station for the past year.<br/>"
        "/api/v1.0/tobs<br/><br/>"

        "Returns min, max and average temperature for dates greater or equal to start.<br/>"
        "/api/v1.0/<start_date><br/><br/>"

        "Returns min, max and average temperature between start and end date.<br/>"
        "/api/v1.0/<start_date>/<end_date><br/><br/>"
    )


# 4. Define what to do when a user hits the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= prev_year).all()

    session.close()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
   


# 5. Define what to do when a user hits the stations route
@app.route("/api/v1.0/stations")
def stations():
    station_freq = session.query(Measurements.station, func.count(Measurements.station)).group_by(Measurements.station).order_by(desc(func.count(Measurements.station))).all()
    session.close()
    for row in station_freq:
        final_station= {station_id: count for station_id, count in station_freq}
    return jsonify(final_station)


# 6. Define what to do when a user hits the tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    active = 'USC00519281'
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    past_temp= session.query(Measurements.tobs).\
                    filter(Measurements.station== active).\
                    filter(Measurements.date>= year_ago).\
                    order_by(Measurements.tobs).all()
    session.close()
    final_temp= []
    for row in past_temp:
        final_temp.extend(list(row))
    return jsonify(final_temp)


# 7. Define what to do when a user hits the given start route
@app.route('/api/v1.0/<start_date>')
def given_start(start_date):
    results = session.query(func.avg(Measurements.tobs), func.max(Measurements.tobs), func.min(Measurements.tobs)).\
        filter(Measurements.date >= start_date).all() 

    date_list = []
    for result in results:
        row = {}
        row['Start Date'] = start_date
        row['Average Temp'] = (result[0])
        row['Highest Temp'] = (result[1])
        row['Lowest Temp'] = (result[2])
        date_list.append(row)

    session.close()
    return jsonify(date_list)


# 8. Define what to do when a user hits the given start & end route
@app.route('/api/v1.0/<start_date>/<end_date>')
def given_start_end(start_date, end_date):
    results = session.query(func.avg(Measurements.tobs), func.max(Measurements.tobs), func.min(Measurements.tobs)).\
        filter(Measurements.date >= start_date, Measurements.date <= end_date).all()

    range_list = []
    for result in results:
        row = {}
        row['Start Date'] = start_date
        row['End Date'] = end_date
        row['Average Temp'] = (result[0])
        row['Highest Temp'] = (result[1])
        row['Lowest Temp'] = (result[2])
        range_list.append(row)
    session.close()
    return jsonify(range_list)


if __name__ == "__main__":
    app.run(debug=True)



   