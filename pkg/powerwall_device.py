
from gateway_addon import Device, Property
from tesla_powerwall import Powerwall

import threading
import time



_POLL_INTERVAL = 5


class PowerwallDev(Device):
	def __init__(self, adapter, powerwall, _id=-1):
		Device.__init__(self, adapter, _id)

		self.powerwall = powerwall
		meters = self.powerwall.get_meters()

		self.description = "Powerwall"
		self._type = ['EnergyMonitor']

		# self.properties['charge'] = Property(
		# 		self,
		# 		'charge',
		# 		{
		# 			'@type': 'LevelProperty',
		# 			'title': 'Battery Charge',
		# 			'type': 'integer',
		# 			'unit': 'percent',
		# 			'minimum': 0,
		# 			'maximum': 100,
		# 		}
		# 	)
		self.properties['charge'] = Property(
				self,
				'charge',
				{
					'@type': 'InstantaneousPowerProperty',
					'title': 'Battery Charge',
					'type': 'number',
					'unit': 'percent',
				}
			)
		self.properties['batteryFlow'] = Property(
				self,
				'batteryFlow',
				{
					'@type': 'InstantaneousPowerProperty',
					'title': 'Battery Power',
					'type': 'number',
					'unit': 'watt',
				}
			)
		self.properties['loadFlow'] = Property(
				self,
				'loadFlow',
				{
					'@type': 'InstantaneousPowerProperty',
					'title': 'Load Power',
					'type': 'number',
					'unit': 'watt',
				}
			)
		self.properties['gridFlow'] = Property(
				self,
				'gridFlow',
				{
					'@type': 'InstantaneousPowerProperty',
					'title': 'Grid Power',
					'type': 'number',
					'unit': 'watt',
				}
			)
		self.properties['solarFlow'] = Property(
				self,
				'solarFlow',
				{
					'@type': 'InstantaneousPowerProperty',
					'title': 'Solar Power',
					'type': 'number',
					'unit': 'watt',
				}
			)

		t = threading.Thread(target=self.poll)
		t.daemon = True
		t.start()

	
	def poll(self):
		"""Poll the device for changes."""
		while True:
			try:
				meters = self.powerwall.get_meters()
				self.properties['batteryFlow'].set_cached_value(meters.battery.get_power()*1000)
				self.properties['gridFlow'].set_cached_value(meters.site.get_power()*1000)
				self.properties['loadFlow'].set_cached_value(meters.load.get_power()*1000)
				self.properties['solarFlow'].set_cached_value(meters.solar.get_power()*1000)
				self.properties['charge'].set_cached_value(self.powerwall.get_charge())

				for prop in self.properties.values():
					self.notify_property_changed(prop)

			except SmartDeviceException:
				print("Device exception during polling")
				continue
			except:
				print("Unknown exception during polling")
				continue

			print("Sleeping for " + str(_POLL_INTERVAL))
			time.sleep(_POLL_INTERVAL)