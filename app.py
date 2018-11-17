import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Seasurement = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


lastyear='2016-08-23'

@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate App.<br/>"
        f"Avaliable routes:<br/>"
        f"/api/v1.0/precipitation   returns the last available year of precipitation data.<br/>"
        f"/api/v1.0/stations    returns a list of the available Hawaiian weather stations from the last year.<br/>"
        f"/api/v1.0/tobs    returns the last available year of temperature data.<br/>"
        f"/api/v1.0/start   returns the min, max, and avg temperatures of all dates since the selected start date.<br/>"
        f"/api/v1.0/start/end   returns the min, max, and avg temperatures of all dates from the selected start to end dates.<br/>"
        f"All dates are formatted as (yyyy-mm-dd).<br/>"
        f"The last available date is 2017-08-23.<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns the last available year of precipitation data."""
    yeardata=session.query(Measurement.date,func.avg(Measurement.prcp)).\
        filter(Measurement.date > lastyear).\
        filter(Measurement.prcp != None).\
        group_by(Measurement.date).all()
    precip = {day[0]:day[1] for day in yeardata}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Returns a list of the available Hawaiian weather stations from the last year."""
    activity=session.query(Measurement.station).\
        group_by(Measurement.station).all()
    stations=[station[0] for station in activity]
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    yeartemps=session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.tobs != None).\
        filter(Measurement.date > lastyear).all()
    temps = {day[0]:day[1] for day in yeartemps}
    return jsonify(temps)


@app.route("/api/v1.0/<start>")
def onetemps(start):
    yeartemps=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    temps={"Tmin":yeartemps[0][0],"Tavg":yeartemps[0][1],"Tmax":yeartemps[0][2]}
    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def rangetemps(start, end):
    yeartemps=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date<= end).all()
    temps={"Tmin":yeartemps[0][0],"Tavg":yeartemps[0][1],"Tmax":yeartemps[0][2]}
    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug=True)
