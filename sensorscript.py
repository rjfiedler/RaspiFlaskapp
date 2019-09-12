import time, datetime, serial, json, requests
import serial, json
import serial.tools.list_ports
import RPi.GPIO as GPIO

def moisture_to_percent(val, waterval, airval):
	val = (val/30)
	print(val)
	val = (val - waterval)
	print(val)
	percent = val/(airval - waterval)
	print(percent)
	percent = (1 - percent)*100
	print(percent)
	percent = int(round(percent))
	print(percent)
	return percent
	
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

class MoistureSensor:
	def __init__(self, name, waterval, airval):
		self.name = name
		self.waterval = waterval
		self.airval = airval
	
	def moisture_to_percent(self, val):
		val = (val/30)
		val = (val - self.waterval)
		percent = val/(self.airval - self.waterval)
		percent = (1 - percent)*100
		percent = int(round(percent))
		return percent

ports = serial.tools.list_ports.comports()
port = ports[0].device
ser = serial.Serial(port, 9600)
waterval0 = 293
waterval1 = 300
waterval2 = 299
waterval3 = 296
airval0 = 590
airval1 = 592
airval2 = 600
airval3 = 596

while 1:
	print('loop running')
	# below code gets the settings from the webapp
	timenow = time.strftime('%H%M')
	timenow = int(timenow)
	LightOnTime = 600
	LightOffTime = 2200
	
	if timenow > LightOnTime and timenow < LightOffTime:
		requests.get('http://0.0.0.0:8000/7/on')
	else:
		requests.get('http://0.0.0.0:8000/7/off')

	wateringsetting = requests.get('http://0.0.0.0:8000/CWS')
	ws = json.loads(str(wateringsetting.text))
	wf = int(ws['frequency'])
	wd = float(ws['duration'])
	wd2 = wd + 10
	wz = int(ws['zone'])
	wateringtimes = []
	waterstarttime = 800
	waterendtime = 2000
	for x in range(wf):
		x = x+1
		wdiff = waterendtime - waterstarttime
		wspace = wdiff/(wf+1)
		watertime = ((x*wspace)+waterstarttime)
		wateringtimes.append(int(watertime))
	# this counts 30 sensor values and averages them
	x = 0
	val0 = 0
	val1 = 0
	val2 = 0
	val3 = 0
	while x < 30:
		print(ser.readline())
		try:
			moisturereading = ser.readline()
		except:
			moisturereading = 'no data from arduino'
			time.sleep(1)
		cm = moisturereading
		if len(cm) == 31 and cm[0:13] == 'Moisture Data':
			print(cm)
			value0 = float(cm[14:17])
			value1 = float(cm[18:21])
			value2 = float(cm[22:25])
			value3 = float(cm[26:29])
			val0 += value0
			val1 += value1
			val2 += value2
			val3 += value3
			dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print(dt)
			x += 1
			time.sleep(2)
		#This turns the valve on and the pump on still need to write this
		if (timenow in wateringtimes):
			wd2 = str(wd2) + '"\n"'
			ser.write(wd2)
			time.sleep(1)
			requests.get("127.0.0.1:8000/11/on")
			time.sleep(wd)
			requests.get("127.0.0.1:8000/11/off")
			wateringtimes.remove(timenow)
			
	percent0 = MoistureSensor(1, 295, 602).moisture_to_percent(val = val0)
	percent1 = MoistureSensor(1, 295, 602).moisture_to_percent(val = val1)
	percent2 = MoistureSensor(1, 295, 602).moisture_to_percent(val = val2)
	percent3 = MoistureSensor(1, 295, 602).moisture_to_percent(val = val3)
	print(percent0)
	
	sensordata = {'0' : percent0,'1' : percent1,'2' : percent2,'3' : percent3}
	data = {'sensordata': sensordata, 'datetime': dt}
	data = json.dumps(data)
	print(data)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	response = requests.post(url = 'http://127.0.0.1:8000/MoistureData', json=data, headers=headers)
	print(response.content)
