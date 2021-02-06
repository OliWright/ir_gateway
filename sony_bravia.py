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

from ir_gateway import GenericIRDevice

config = {
	"ProtocolName" : "SONY",
	"PowerOnBeforeInputSelect" : "PowerOn",
	"StateRemoteCodes" : {
		"Off"   : "PowerOff",
		"HDMI1" : "HDMI1",
		"HDMI2" : "HDMI2",
		"HDMI3" : "HDMI3",
		"HDMI4" : "HDMI4",
	},
	"RemoteCodes" : [
		{
			"Bits" : 12,
			"Codes" : {
				"Input"    : "0xA50",
				"Power"    : "0xA90",
				"AV1"      : "0x30",  # Scart
				"AV2"      : "0x830", # Component
				"PowerOn"  : "0x750",
				"PowerOff" : "0xF50",
			}
		},
		{
			"Bits" : 15,
			"Codes" : {
				"Sync"    : "0xD58",
				"Play"    : "0x2CE9",
				"Pause"   : "0x4CE9",
				"HDMI1"   : "0x2D58",
				"HDMI2"   : "0x6D58",
				"HDMI3"   : "0x1D58",
				"HDMI4"   : "0x5D58",
				"Back"    : "0x62E9",
				"Play"    : "0x2CE9",
				"Pause"	  : "0x4CE9",
				"Stop"    : "0xCE9",
				"Rewind"  : "0x6CE9",
				"FastForward":"0x1CE9",
				"Previous": "0x1EE9",
				"Next"	  : "0x5EE9",
				"Volume+" : "0x240C",
				"Volume-" : "0x640C",
				"Mute"    : "0x140C",	
			}
		},
	]
}

class SonyBravia(GenericIRDevice):
	def __init__(self, base_topic, short_name, device_name, input_friendly_names, ir_gateway):
		global config
		GenericIRDevice.__init__(self, base_topic, short_name, device_name, config, input_friendly_names, ir_gateway)

