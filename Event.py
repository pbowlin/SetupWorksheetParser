from datetime import datetime, date, time
import re

class Event:

	def __init__(self, raw_text, building, room):
		self.raw_text = raw_text
		self.building = building
		self.room = room
		self.parse_event_info()

		self.has_tech = False
		self.has_runner = False

		self.find_techs()


	def parse_event_info(self):
		event_info = self.raw_text[0].split(",")
		self.date = datetime.strptime(event_info[0], "%m/%d/%Y").date()
		self.reservation_start = datetime.strptime(event_info[1], "%I:%M %p").time()
		self.event_start = datetime.strptime(event_info[2], "%I:%M %p").time()
		self.event_end = datetime.strptime(event_info[3], "%I:%M %p").time()
		self.reservation_end = datetime.strptime(event_info[4], "%I:%M %p").time()
		self.event_title = event_info[5]

	def find_techs(self):
		# Regex to match on MTP techs, but not runners:
		# (MTP Tech\n|MTP Tech - (?!Runner))

		for line in self.raw_text:
			if re.search('(MTP Tech\n|MTP Tech - (?!Runner|Setup|Takedown|Entire))', line):
				self.has_tech = True
			elif re.search('MTP Tech - Runner', line):
				self.has_runner = True

	def check_for_event_flags(self):
		## TODO: Implement checking for flags
		pass

