"""Tesla Powerwall adapter for Mozilla WebThings Gateway."""

from gateway_addon import Adapter, Database
from .powerwall_device import PowerwallDev
from tesla_powerwall import Powerwall

_TIMEOUT = 3


class PowerwallAdapter(Adapter):
	
	def __init__(self, verbose=False):
		print("Powerwall adapter constructor")
		self.name = self.__class__.__name__
		Adapter.__init__(self,
										'powerwall-adapter',
										'powerwall-adapter',
										verbose=verbose)

		self.pairing = False
		self.start_pairing(_TIMEOUT)

	def _add_from_config(self):
		"""Attempt to add all configured devices."""
		database = Database('powerwall-adapter')
		if not database.open():
			return

		config = database.load_config()
		database.close()

		if not config or 'addresses' not in config:
			return

		id = 0
		for address in config['addresses']:
			try:
					print("Powerwall adapter trying to connect to " + address)
					dev = Powerwall(address)
			except (OSError, UnboundLocalError) as e:
					print('Powerwall adapter failed to connect to {}: {}'.format(address, e))
					continue

			if dev:
				id += 1
				self._add_device(dev, id)

							
	def start_pairing(self, timeout):
		"""
		Start the pairing process.

		timeout -- Timeout in seconds at which to quit pairing
		"""
		if self.pairing:
			return

		self.pairing = True

		self._add_from_config()

		""" No discovery functionality yet. Devices must be added in the settings """

		self.pairing = False
		print("Powerwall adapter pairing complete")

	def _add_device(self, dev, id):
		device = PowerwallDev(self, dev, id)
		self.handle_device_added(device)

	def cancel_pairing(self):
		"""Cancel the pairing process."""
		self.pairing = False