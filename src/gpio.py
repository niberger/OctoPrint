# coding=utf-8

__author__ = "Nicolas Berger"
__author__ = "Gina Häußge <osd@foosel.net>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'

import wiringpi2 as wiringpi
import time
import threading

from octoprint.events import eventManager

# singleton
_instance = None

def gpioManager():
	global _instance
	if _instance is None:
		_instance = GpioManager()
	return _instance

class GpioManager(object):
	"""
	Fire GPIO events to the event manager
	"""
	_printer = None

	def __init__(self):
		wiringpi.wiringPiSetupSys()
		self._power_on_pin = 5
		self._btn_1_pin = 7
		self._btn_2_pin = 8
		self._btn_3_pin = 25
		self._last_value_1 = 0
		self._last_value_2 = 0
		self._last_value_3 = 0

		self._worker = threading.Thread(target=self._work)
		self._worker.daemon = True
		self._worker.start()

	def setPrinter(self, printer):
		self._printer = printer

	def _work(self):
		while True:
			value_1 = wiringpi.digitalRead(self._btn_1_pin)
			if(value_1 == 0 and self._last_value_1 == 1):
				if(self._printer != None):
					self._printer.command("G28") #Home
			self._last_value_1 = value_1


			value_2 = wiringpi.digitalRead(self._btn_2_pin)
			if(value_2 == 0 and self._last_value_2 == 1):
				if(self._printer != None):
					self._printer.commands(["M104 S180","M140 S55"])
			self._last_value_2 = value_2


			value_3 = wiringpi.digitalRead(self._btn_3_pin)
			if(value_3 == 0 and self._last_value_3 == 1):
				if(self._printer != None):
					self._printer.togglePausePrint()
			self._last_value_3 = value_3

			time.sleep(0.01)


