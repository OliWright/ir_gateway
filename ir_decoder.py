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

import json
import time

class IRDecoder():
	def __init__(self, base_topic, config):
		self.base_topic = base_topic + "/ir-gateway/IRtoMQTT"
		self.subscribe_topic = self.base_topic
		self.config = config
		self.most_recent_code = None
		self.most_recent_code_time = None

	def on_message(self, client, userdata, msg, payload):
		try:
			ir = json.loads(payload)
		except:
			print("Exception while trying to json parse: " + payload)
			return

		print("Attempting to decode " + str(ir))
		codes = self.config.get(ir["protocol_name"])
		if codes is not None:
			code = codes.get(ir["hex"])
			if code is not None:
				# Have we just sent this recently?
				now = time.time()
				if self.most_recent_code == code:
					elapsed_time = now - self.most_recent_code_time
					if elapsed_time < 0.5:
						# Too soon
						self.most_recent_code_time = now
						return

				self.most_recent_code_time = now
				self.most_recent_code = code

				if isinstance(code, list):
					# Multiple codes
					for c in code:
						topic = c["topic"]
						payload = c.get("payload")
						if payload is None:
							payload = ""
						retain = c.get("retain")
						if retain is None:
							retain = False
						#print("Re-publishing as {0}, payload {1}".format(topic, payload))
						client.publish(topic, payload, retain)
				else:
					# Individual code
					topic = code["topic"]
					payload = code.get("payload")
					if payload is None:
						payload = ""
					retain = code.get("retain")
					if retain is None:
						retain = False
					#print("Re-publishing as {0}, payload {1}".format(topic, payload))
					client.publish(topic, payload, retain)
