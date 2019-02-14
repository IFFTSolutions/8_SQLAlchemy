# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import numpy as np
# Create engine using the hawaii.sqlite database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite ?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
#Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
session


from flask import Flask, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Weather App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using `date` as the key and \
         `prcp` as the value.Return the JSON representation of your dictionary.  """
    # retrieve the last date
    query_2_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    date_2 = dt.datetime.strptime(query_2_date[0],'%Y-%m-%d')
    # date truncation
    date_2 = dt.date(date_2.year, date_2.month, date_2.day)
    
    # Calculate the date 1 year ago from the last data point in the database
    query_1_date = ((date_2) - dt.timedelta(days=1* 365))
    date_1 = query_1_date

    data = session.query(Measurement.date.label('date'), (Measurement.prcp).label('prcp')).\
        filter(Measurement.date >= date_1).all() 

    # # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation_data = []
    for i in data:
         prcp_data_dict = {}
         prcp_data_dict["Date"] = i.date
         prcp_data_dict["Precipitation"] = i.prcp
         precipitation_data.append(prcp_data_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """* Return a JSON list of stations from the dataset."""
    station_results = session.query(Station.station,Station.name).all()

    return jsonify(station_results)

@app.route("/api/v1.0/tobs")
def tobs():
    """* query for the dates and temperature observations from a year from the last data point.\
      * Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # retrieve the last date
    query_2_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    date_2 = dt.datetime.strptime(query_2_date[0],'%Y-%m-%d')
    # date truncation
    date_2 = dt.date(date_2.year, date_2.month, date_2.day)
    
    # Calculate the date 1 year ago from the last data point in the database
    query_1_date = ((date_2) - dt.timedelta(days=1* 365))
    date_1 = query_1_date

    tobs_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= date_1).all()

    return jsonify(tobs_results)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    """* Return a JSON list of the minimum temperature, the average temperature, and the max \
         temperature for a given start or start-end range. \
        * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater \
         than and equal to the start date. """

    Start_Temps = session.query(Measurement.date.label('Date'), \
                      func.min(Measurement.tobs).label('Min_Temp'), \
                      func.max(Measurement.tobs).label('Max_Temp'), \
                      func.avg(Measurement.tobs).label('Avg_Temp')). \
                      filter(Measurement.date >= start_date).\
                      group_by(Measurement.date).all()         
        
    return jsonify(Start_Temps)
    

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_and_end_date(start_date,end_date):
    """* When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for \
         dates between the start and end date inclusive."""
    
    Temps = session.query(Measurement.date.label('Date'), \
                      func.min(Measurement.tobs).label('Min_Temp'), \
                      func.max(Measurement.tobs).label('Max_Temp'), \
                      func.avg(Measurement.tobs).label('Avg_Temp')). \
                      filter(Measurement.date >= start_date).\
                      filter(Measurement.date <= end_date).\
                      group_by(Measurement.date).all()         
     
    return jsonify(Temps)

if __name__ == "__main__":
    app.run(debug=True)