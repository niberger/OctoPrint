# coding=utf-8

__author__ = "Nicolas Berger"
__author__ = "Gina Häußge <osd@foosel.net>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'

import serial
import time
import threading
import math

# singleton
_instance = None

def monitorManager():
	global _instance
	if _instance is None:
		_instance = MonitorManager()
	return _instance

class MonitorManager(object):
	"""
	Print events and status to the serial monitor
	"""
	def __init__(self):
		self._baud = 1200
		self._port = serial.Serial("/dev/ttyAMA0", baudrate=self._baud)

		self._eventLine1 = ""
		self._eventLine2 = ""
		self._eventStep = 0

		self._printer = None

		self._worker = threading.Thread(target=self._work)
		self._worker.daemon = True
		self._worker.start()

	def setPrinter(self, printer):
		self._printer = printer
 
	def printEvent(self, line1, line2 = ""):
		self._eventLine1 = line1
		self._eventLine2 = line2
		self._eventStep = 0

	def printMsg(self, line1, line2 = "", step = 0):
		offset = 0
		maxlen = 19
		if(len(line2) > maxlen):
			step_mod = step % (len(line2) + 6) - 3
			if(step_mod < 0):
				offset = 0
			elif(step_mod > len(line2) - maxlen):
				offset = len(line2) - maxlen
			else:			
				offset = step_mod
		
		line1cut = line1[ :maxlen]
		line2cut = line2[offset :maxlen + offset]

		serial_cmd = ""
		serial_cmd += chr(0x14) #cursor off
		serial_cmd += chr(0x10)+chr(0x00) #cursor at the begin
		serial_cmd += line1cut + " " * (maxlen - len(line1cut))
		serial_cmd += chr(0x10)+chr(0x14) #cursor at the 2nd line
		serial_cmd += line2cut + " " * (maxlen - len(line2cut)) #for now I cant control the last char without an unexpected newline

		#flush
		self._port.write(serial_cmd)

	def printStatus(self, step):
		if(self._printer != None):
			state = self._printer.getCurrentData()
			self.printMsg("",str(state))

	def _work(self):
		self._eventStep = 0
		while True:
			self._eventStep = self._eventStep + 1
			if(self._eventStep < 40):
				self.printMsg(self._eventLine1, self._eventLine2, self._eventStep)
			else:
				self.printStatus(self._eventStep)
			time.sleep(0.5)


#
#		self._serialMonitor.printMsg("Tmp: " + "{:.1f}".format(self._temp) + "/" + "{:.1f}".format(self._targetTemp), "Bed: " + "{:.1f}".format(self._bedTemp) + "/" + "{:.1f}".format(self._targetBedTemp))
#		self._stateMonitor.addTemperature({"currentTime": currentTimeUtc, "temp": self._temp, "bedTemp": self._bedTemp, "targetTemp": self._targetTemp, "targetBedTemp": self._targetBedTemp})
