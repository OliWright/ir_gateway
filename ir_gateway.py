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

# ir_gateway.py - Provides IRGateway device class for mqtt-devices
#
# IRGateway manages a queue for transmitting IR commands through an
# OpenMQTTGateway device.
# It throttles the sending of IR commands so there is a 0.5s gap between
# them all, to increase the chances of them being received correctly.
# It will also wait until 0.5s after receiving any IR command on the
# same gateway before transmitting anything

import queue
import time

default_json_template = '{{"bits":{bits},"hex":"{hex}","protocol_name":"{protocol_name}"}}'
json_templates = {
	# In the current version of OpenMQTTGateway (0.94Beta),
	# SONY codes require explicit repeats to work correctly.
	"SONY" : '{{"bits":{bits},"hex":"{hex}","protocol_name":"{protocol_name}","repeat":3}}'
}

class Command():
	def __init__(self, device_name, command, protocol_name, bits, hex):
		self.device_name = device_name
		self.command = command
		self.protocol_name = protocol_name
		self.bits = bits
		self.hex = hex

class IRGateway():
	def __init__(self, base_topic):
		self.base_topic = base_topic + "/ir-gateway"
		self.subscribe_topic = self.base_topic + "/IRtoMQTT"
		self.ir_gateway_topic = self.base_topic + "/commands/MQTTtoIR"
		self.command_queue = queue.Queue()
		self.receiving_ir = False
		self.most_recent_ir_event_time = None

	def set_update_time(self):
		if self.command_queue.empty():
			# Our command queue is empty, so we don't need an update
			self.next_update_time = None
		else:
			# We have some commands we need to send.  Set the update time
			# to either now, or with an appropriate delay after the most
			# recent IR event happened
			now = time.monotonic()
			if self.most_recent_ir_event_time is not None:
				# We should leave 0.5s between ir events
				self.next_update_time = self.most_recent_ir_event_time + 0.5
				self.next_update_time = max(self.next_update_time, now)
			else:
				self.next_update_time = now

	def enqueue(self, device_name, command, protocol_name, bits, hex):
		# Queue an IR command for transmitting through the gateway
		self.command_queue.put( Command(device_name, command, protocol_name, bits, hex) )
		print("Queueing IR to {device_name}: {command}".format(device_name = device_name, command = command))
		self.set_update_time()

	def on_message(self, client, userdata, msg, payload):
		# Mark a bool to say that we're receiving some IR
		# This will in turn prevent us from immediately transmitting on our
		# first update
		self.most_recent_ir_event_time = time.monotonic()
		self.receiving_ir = True
		self.set_update_time()

	def on_update(self, client):
		if not self.command_queue.empty():
			# Transmit the IR command at the head of the queue
			command = self.command_queue.get()
			global json_templates
			global default_json_template
			json_template = json_templates.get(command.protocol_name)
			if json_template is None:
				json_template = default_json_template
			json = json_template.format(protocol_name = command.protocol_name, bits = command.bits, hex = command.hex)
			now = time.monotonic()
			print("Sending IR at {when:0.2f} to {device_name}: {command}".format(when = now, device_name = command.device_name, command = command.command))
			client.publish(self.ir_gateway_topic, payload = json)
			self.most_recent_ir_event_time = now
			self.set_update_time()
