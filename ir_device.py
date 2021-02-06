# MIT License
#
# Copyright (c) 2020 Oli Wright <oli.wright.github@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class GenericIRDevice():
	def __init__(self, base_topic, short_name, device_name, config, input_friendly_names, ir_gateway):
		self.device_name = device_name
		self.base_topic = base_topic + "/" + short_name
		print("Creating " + self.base_topic)
		self.subscribe_topic = self.base_topic + "/#"
		self.remote_topic = self.base_topic + "/remote"
		self.set_state_topic = self.base_topic + "/set-state"
		self.status_topic = self.base_topic + "/status"
		self.config = config
		self.ir_gateway = ir_gateway
		self.protocol_name = config["ProtocolName"]
		self.power_on_before_input_select_code = config.get("PowerOnBeforeInputSelect")
		self.send_ir_even_if_same_state = config.get("SendIREvenIfSameState")
		if self.send_ir_even_if_same_state is None:
			self.send_ir_even_if_same_state = False
		self.friendly_name_to_input = {}
		if input_friendly_names is None:
			self.input_to_friendly_name = {}
		else:
			self.input_to_friendly_name = input_friendly_names
			# Create reverse mapping of friendly name to input
			for input, friendly_name in input_friendly_names.items():
				self.friendly_name_to_input[friendly_name] = input
		self.state_name = None
		self.state_friendly_name = None
		self.set_state(None, "Off")

	def publish_status(self, client):
		if client is not None:
			json = '{{"state":"{state}","friendly_name":"{friendly_name}"}}'.format(state = self.state_name, friendly_name = self.state_friendly_name)
			client.publish(self.status_topic, payload = json, retain = True)

	def send_remote(self, command):
		bits = 0
		hex = 0
		for code_bank in self.config["RemoteCodes"]:
			hex = code_bank["Codes"].get(command, None)
			if hex is not None:
				bits = code_bank["Bits"]
				break
		if (bits is None) or (bits == 0):
			print("Unknown command: " + command)
			return
		self.ir_gateway.enqueue(self.device_name, command, self.protocol_name, bits, hex)

	def set_state(self, client, state_name):
		# state_name might be an input name, or a friendly name
		remote_code = self.config["StateRemoteCodes"].get(state_name)
		if remote_code is None:
			input_name = self.friendly_name_to_input.get(state_name)
			if input_name is None:
				print("Unknown state : " + state_name)
				return
			# state_name was the friendly name
			state_friendly_name = state_name
			state_name = input_name
			remote_code = self.config["StateRemoteCodes"].get(state_name)
		else:
			# state_name was the input name
			state_friendly_name = self.input_to_friendly_name.get(state_name)
			if state_friendly_name is None:
				state_friendly_name = state_name
		if self.send_ir_even_if_same_state or state_name != self.state_name:
			# State is changing
			if self.state_name is not None:
				print("Switching state of {device_name} from {previous} to {current}".format(device_name = self.device_name, previous = self.state_friendly_name, current = state_friendly_name))
			power_was_off = (self.state_name == "Off")
			self.state_name = state_name
			self.state_friendly_name = state_friendly_name
			if client is not None:
				if remote_code is not None:
					if power_was_off and (self.power_on_before_input_select_code is not None):
						# Power on the device before selecting the input
						self.send_remote(self.power_on_before_input_select_code)
					self.send_remote(remote_code)
				self.publish_status(client)

	def on_message(self, client, userdata, msg, payload):
		if msg.topic == self.remote_topic:
			self.send_remote(payload)
		elif msg.topic == self.set_state_topic:
			self.set_state(client, payload)
		elif msg.topic == self.status_topic:
			pass
		else:
			print("Unknown topic: " + msg.topic)

	def on_connect(self, client, userdata, flags, rc):
		self.publish_status(client)

