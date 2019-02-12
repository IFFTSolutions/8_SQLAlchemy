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
        f"/api/v1.0/start_and_end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using `date` as the key and \
         `prcp` as the value.Return the JSON representation of your dictionary.  """
    query_2_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    date_2 = dt.datetime.strptime(query_2_date[0],'%Y-%m-%d')
    # date truncation
    date_2 = dt.date(date_2.year, date_2.month, date_2.day)
    
    query_1_date = dt.date(2017, 8, 23) - dt.timedelta(days=1* 365)    
    
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_1_date).all()

    # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation_data = []
    for data in results:
        prcp_data_dict = {}
        prcp_data_dict["Date"] = data.date
        prcp_data_dict["Precipitation"] = data.prcp
        precipitation_data.append(prcp_data_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """* Return a JSON list of stations from the dataset."""
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    all_sts = []
    for sts in results:
        stations_dict = {}
        stations_dict["Station"] = sts.station
        stations_dict["Station Name"] = sts.name
        stations_dict["Latitude"] = sts.latitude
        stations_dict["Longitude"] = sts.longitude
        stations_dict["Elevation"] = sts.elevation
        all_sts.append(stations_dict)

    return jsonify(all_sts)

@app.route("/api/v1.0/tobs")
def tobs():
    """* query for the dates and temperature observations from a year from the last data point.\
      * Return a JSON list of Temperature Observations (tobs) for the previous year."""
    
    query_2_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    date_2 = dt.datetime.strptime(query_2_date[0],'%Y-%m-%d')
    # date truncation
    date_2 = dt.date(date_2.year, date_2.month, date_2.day)
    query_1_date = ((date_2) - dt.timedelta(days=1* 365))
    query_1_date

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= query_1_date).all()

    # Create a dictionary from the row data and append to a list of for the precipitation data
    tobs_data = []
    for data in results:
        tobs_dict = {}
        tobs_dict["Date"] = data.date
        tobs_dict["Temperature"] = data.tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/start_date")
def start_date():
    """* Return a JSON list of the minimum temperature, the average temperature, and the max \
         temperature for a given start or start-end range. \
        * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater \
         than and equal to the start date. \
        * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for \
         dates between the start and end date inclusive."""
    
    st_date = dt.datetime(2016,8,23)
    
    Temps = session.query(Measurement.date.label('Date'), \
                      func.min(Measurement.tobs).label('Min_Temp'), \
                      func.max(Measurement.tobs).label('Max_Temp'), \
                      func.avg(Measurement.tobs).label('Avg_Temp')). \
                      filter(Measurement.date >= st_date).all()         
        # Create a dictionary from the row data and append to a list of for the precipitation data
    
    Temps_data = []
    for data in Temps:
        Temps_dict = {}
        #Temps_dict["Date"] = data.Date
        Temps_dict["Min_Temp"] = data.Min_Temp
        Temps_dict["Max_Temp"] = data.Max_Temp        
        Temps_dict["Avg_Temp"] = data.Avg_Temp
        Temps_data.append(Temps_dict)

    return jsonify(Temps_data)
    

@app.route("/api/v1.0/start_and_end_date")
def start_and_end_date():
    """* When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for \
         dates between the start and end date inclusive."""
    
    date1 = dt.datetime(2017,2,15)
    date2 = dt.datetime(2017,2,25)
    
    Temps = session.query(Measurement.date.label('Date'), \
                      func.min(Measurement.tobs).label('Min_Temp'), \
                      func.max(Measurement.tobs).label('Max_Temp'), \
                      func.avg(Measurement.tobs).label('Avg_Temp')). \
                      filter(Measurement.date >= date1).\
                      filter(Measurement.date <= date2).all()         
        # Create a dictionary from the row data and append to a list of for the precipitation data
    
    Temps_data = []
    for data in Temps:
        Temps_dict = {}
        Temps_dict["Min_Temp"] = data.Min_Temp
        Temps_dict["Max_Temp"] = data.Max_Temp        
        Temps_dict["Avg_Temp"] = data.Avg_Temp
        Temps_data.append(Temps_dict)

    return jsonify(Temps_data)


if __name__ == "__main__":
    app.run(debug=True)