from app import app, db
import json, celery, serial, io, base64, time, datetime
import pandas as pd
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, Response
from app.models import LightSetting, WateringSetting, MoistureData, DailyLog
from app.forms import WateringForm, PlotForm, DailyLogForm

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

ports = serial.tools.list_ports.comports()
port = ports[0].device
ser = serial.Serial(port, 9600)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   7 : {'name' : 'Lights', 'state' : GPIO.LOW},
   11 : {'name' : 'Drip Pump', 'state' : GPIO.LOW}
   }

# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)

@app.route("/index", methods=['GET','POST'])
@app.route("/", methods=['GET','POST'])
def index():
   form = WateringForm()
   form2 = PlotForm()
   form3 = DailyLogForm()
   plotdaterange = "/mp/{}/{}/MoisturePlot.png".format('sdt', 'edt')
   if len(WateringSetting.query.all()) > 0:
	   currentwatersetting = WateringSetting.query.all()[-1]
   
   if form.validate_on_submit():
	   wateringsetting = WateringSetting(zone= int(form.wateringzone.data), frequency= int(form.wateringfrequency.data), duration=float(form.wateringduration.data))
	   db.session.add(wateringsetting)
	   db.session.commit()

   if form3.validate_on_submit():
	   dailylog = DailyLog(datetime = datetime.datetime.now(), TDS = int(form3.TDSreading.data), PH = float(form3.PHreading.data))
	   db.session.add(dailylog)
	   db.session.commit()
	   
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   if form2.validate_on_submit():
	   fsdt = form2.startdatetime.data
	   fedt = form2.enddatetime.data
	   plotdaterange = "/mp/{}/{}/MoisturePlot.png".format(fsdt, fedt)
   templateData = {
      'pins' : pins,
      'wateringfrequency': currentwatersetting.frequency,
	  'wateringzone': currentwatersetting.zone,
	  'wateringduration': currentwatersetting.duration,
	  'plotdaterange' : plotdaterange,
	  'form' : form,
	  'form2' : form2,
	  'form3' : form3
      }   
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)
   
@app.route("/data", methods=["GET"])
def dataview():
	return render_template('data.html')
	
@app.route("/settings", methods=["GET", "POST"])
def settingsview():
	form = WateringForm()
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)
	if len(WateringSetting.query.all()) > 0:
		currentwatersetting = WateringSetting.query.all()[-1]
	
	templateData = {
	'wateringfrequency': currentwatersetting.frequency,
	'wateringzone': currentwatersetting.zone,
	'wateringduration': currentwatersetting.duration,
	'form' : form,
	'pins': pins
	}
	return render_template('settings.html', **templateData)
	
	
@app.route("/moisturesensor/<sensornum>", methods=["GET"])
def moisturesensor(sensornum):
	sensorobj = MoistureData.query.filter_by(sensor = sensornum).all()
	sensorval = sensorobj[-1].value
	return jsonify(moisturereading= sensorval)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>", methods=['GET','POST'])
def action(changePin, action):
   form = WateringForm()
   form2 = PlotForm()
   form3 = DailyLogForm()
   plotdaterange = "/mp/{}/{}/MoisturePlot.png".format('sdt', 'edt')
   if len(WateringSetting.query.all()) > 0:
	   currentwatersetting = WateringSetting.query.all()[-1]
   if form.validate_on_submit():
	   wateringsetting = WateringSetting(zone= int(form.wateringzone.data), frequency= int(form.wateringfrequency.data), duration=float(form.wateringduration.data))
	   db.session.add(wateringsetting)
	   db.session.commit()
	   #return redirect(url_for('index'))
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " on."
   if action == "off":
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " off."
   if action == "toggle":
      # Read the pin and set it to whatever it isn't (that is, toggle it):
      GPIO.output(changePin, not GPIO.input(changePin))
      message = "Toggled " + deviceName + "."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'message' : message,
      'pins' : pins,
      'wateringfrequency': currentwatersetting.frequency,
      'wateringzone': currentwatersetting.zone,
      'wateringduration': currentwatersetting.duration,
      'plotdaterange' : plotdaterange,
      'form' : form,
      'form2' : form2,
      'form3' : form3
   } 

   return render_template('main.html', **templateData)

@app.route("/LightSetting", methods=['GET', 'POST'])
def return_all():
    if request.method == 'GET':
        lightsettings= []
        ls = LightSetting.query.all()
        for s in ls:
            lightsettings.append(s.as_dict())            
        return json.dumps(lightsettings)
        
@app.route("/CWS", methods=['GET'])
def return_first():
	currentwatersetting = WateringSetting.query.all()[-1]
	cwsdict = currentwatersetting.as_dict()
	return json.dumps(cwsdict)
	
@app.route("/MoistureData", methods=['GET', 'POST'])
def moisturedata():
	if request.method == 'POST':
		rd = json.loads(request.json)
		dt = rd['datetime']
		dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
		rd = rd['sensordata']
		for k in rd.keys():
			md = MoistureData(sensor=int(k),value=int(rd[k]), datetime= dt)
			db.session.add(md)
		db.session.commit()
		resp = jsonify(success=True)
		return resp

@app.route("/mp/<startdatetime>/<enddatetime>/MoisturePlot.png", methods=['GET'])
def plot_png(startdatetime, enddatetime):
	fig = create_figure(startdatetime, enddatetime)
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')
	
def create_figure(startdatetime, enddatetime):
	df = pd.read_sql(MoistureData.query.statement, db.session.bind)
	fig = Figure(figsize=(8,8))
	current_time = time.strftime('%Y-%m-%d %H:%M')
	if startdatetime != 'sdt':
		startdatetime = '2019-' + startdatetime
		st = datetime.datetime.strptime(startdatetime, '%Y-%m-%d-%H-%M')
	else:
		st = datetime.datetime.strptime('2019-06-14 00:00', '%Y-%m-%d %H:%M')
	if enddatetime != 'edt':
		enddatetime = '2019-' + enddatetime
		et = datetime.datetime.strptime(enddatetime, '%Y-%m-%d-%H-%M')
	else:
		et = datetime.datetime.strptime(current_time, '%Y-%m-%d %H:%M')
	df = df[(df["datetime"] > st) & (df["datetime"] < et)] 
	axis = fig.add_subplot(1, 1, 1)
	axis.plot(df.loc[df['sensor'] == 0, 'datetime'],df.loc[df['sensor'] == 0, 'value'], c = 'blue', label= 'Sensor 1')
	axis.plot(df.loc[df['sensor'] == 1, 'datetime'],df.loc[df['sensor'] == 1, 'value'], c ='red', label= 'Sensor 2')
	axis.plot(df.loc[df['sensor'] == 2, 'datetime'],df.loc[df['sensor'] == 2, 'value'], c = 'green', label= 'Sensor 3')
	axis.plot(df.loc[df['sensor'] == 3, 'datetime'],df.loc[df['sensor'] == 3, 'value'], c = 'yellow', label= 'Sensor 4')
	axis.tick_params(labelrotation=45)
	axis.set_ylim(0,100)
	axis.set_ylabel('Percent Moisture')
	axis.legend(loc='lower left')
	return fig
	
@app.route("/arduino/<command>")
def send_to_arduino(command):
	command = command.encode('UTF-8')
	command = command + '\n'
	command.encode('UTF-8')
	ser.write(command)
	return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
"""
@celery.task
def water_for_duration(duration):
    
    return result
"""
