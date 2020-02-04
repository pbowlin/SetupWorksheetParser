from datetime import datetime, date, time
import re

class Event:

	def __init__(self, raw_text, building, room):
		self.raw_text = raw_text
		self.building = building
		self.room = room
		## Note that the room will actually be a list of "rooms" in order to accomodate pages that span
		## multiple sections of a room. i.e. JMEC 516EW will be [JMEC 516E, JMEC 516W] whereas BRB 252
		## will be just [BRB 252]. Then we can also search this specific event's descriptions in to check
		## if the event itself spans multiple rooms (as JMEC runners so often do).
		## i.e. [JMEC 501] might turn into [JMEC 501, JMEC 502, JMEC 503, JMEC 504] here.
		self.parse_event_info()

		self.has_tech = False
		self.has_runner = False

		self.find_techs()

		if self.has_runner == True:
			extra_rooms = self.check_description_for_rooms()
			for room in extra_rooms:
				self.room.append(room)

		# print(f'{self.event_title} rooms: {self.room}')


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

	def check_description_for_rooms(self):
		extra_rooms = []
		for line_num in range(len(self.raw_text)):
			if re.match('Event Description',self.raw_text[line_num]):
				extra_rooms = self.extract_rooms_from_text(line_num)
		extra_rooms = self.clean_extra_room_names(extra_rooms)
		#print('extra rooms: ', extra_rooms)

		return extra_rooms


	def extract_rooms_from_text(self, start_line_num):
		extra_rooms = []
		groups = re.findall('(5[01][1234][ ]*[-][ ]*5[01][1234])|((5[01][123456])[ eEWw]+[andAND ]+\\3[ eEWw]+)|(5[01][123456][ eE&WwandAND]*[eEwW])|(5[01][123456])', self.raw_text[start_line_num+1])
		for group in groups:
			for entry in group:
				if entry != '':
					extra_rooms.append(entry)

		return extra_rooms

	def clean_extra_room_names(self, extra_rooms):
		cleaned_rooms = []
		for room in extra_rooms:
			## Handle cases like: 501-504
			if len(room.split('-')) == 2:
				room_to_add = int(room[:3])
				
				while room_to_add <= int(room[-3:]):
					cleaned_rooms.append(f'JMEC {room_to_add}')
					room_to_add += 1
			## Handle cases like: 505E&W, or 505E and W, or 505E and 505W
			elif len(room.split('&')) == 2 or len(room.lower().split('and')) == 2:
				cleaned_rooms.append(f'JMEC {room[:3]}E')
				cleaned_rooms.append(f'JMEC {room[:3]}W')
			## Handle cases like: 505EW
			elif room[-2:].lower() == 'ew':
				cleaned_rooms.append(f'JMEC {room[:3]}E')
				cleaned_rooms.append(f'JMEC {room[:3]}W')
			## Handle solo room cases like: 506 or 505e or 505 E
			else:
				room = room.translate({ord(i): None for i in ' andAND'}) # Remove spaces for case like 505 E ('andAND' characters in there for good measure due to RegEx but super likely are unecessary.)
				cleaned_rooms.append(f'JMEC {room.upper()}')

		return cleaned_rooms





