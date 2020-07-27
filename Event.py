from datetime import datetime, date, time, timedelta
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

		self.has_setup_tech = False
		self.has_takedown_tech = False
		self.has_entire_event_tech = False

		self.find_techs()

		if self.has_runner == True:
			extra_rooms = self.check_description_for_rooms()
			for room in extra_rooms:
				self.room.append(room)

		if self.has_tech == True:
			self.get_tech_setup_and_breakdown_times()

		# print(f'{self.event_title} rooms: {self.room}')


	def parse_event_info(self):
		event_info = self.raw_text[0].split(",")
		self.date = datetime.strptime(event_info[0], "%m/%d/%Y").date()
		self.reservation_start = datetime.strptime(event_info[1], "%I:%M %p").time()
		self.setup_start = self.reservation_start
		self.event_start = datetime.strptime(event_info[2], "%I:%M %p").time()
		self.setup_end = self.event_start
		self.event_end = datetime.strptime(event_info[3], "%I:%M %p").time()
		self.takedown_start = self.event_end
		self.reservation_end = datetime.strptime(event_info[4], "%I:%M %p").time()
		self.takedown_end = self.reservation_end
		self.event_title = event_info[5]
		self.event_category = event_info[7]
		self.comment = ""

		if self.building == 'AV Rental Center\n':
			self.comment = f'Location: {self.room[0][5:]}'
			self.room = ['Rental Requests']

			print(self.comment)
			print(self.room)

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


	def get_tech_setup_and_breakdown_times(self):
		all_found_times = []

		for line_num in range(len(self.raw_text)):
			if re.match('MTP Tech - Setup',self.raw_text[line_num]):
				self.has_setup_tech = True
				from_time , to_time = self.extract_times_from_text(line_num, all_found_times)
			if re.match('MTP Tech - Takedown',self.raw_text[line_num]):
				self.has_takedown_tech = True
				from_time , to_time = self.extract_times_from_text(line_num, all_found_times)
			if re.match('MTP Tech - Entire',self.raw_text[line_num]):
				self.has_entire_event_tech = True
				from_time , to_time = self.extract_times_from_text(line_num, all_found_times)

		from_time = min(all_found_times)
		to_time = max(all_found_times)

		########## STILL HAVE LOTS OF WORK TO DO TO MAKE THIS RIGHT WITH EVENT TIME
		########## FOR INSTANCE, CHECK 02/10/20 BRB AUD EVENT, AS OF NOW EVENT END IS AFTER TAKEDOWN END (NOT GOOD!!)

		if self.has_setup_tech or self.has_entire_event_tech:
			self.setup_start = from_time
		# if to_time != datetime.strptime('8:00 AM', "%I:%M %p").time():
		# 	self.event_start = to_time
		if abs(timedelta(hours = self.event_start.hour, minutes = self.event_start.minute) - timedelta(hours = from_time.hour, minutes = from_time.minute)) < timedelta(minutes = 30):
			if self.event_start.minute - 30 < 0:
				new_minutes = 30 + (self.event_start.minute)
				self.setup_start = self.event_end.replace(hour = self.event_start.hour - 1, minute = new_minutes)
			else:
				self.setup_start = self.event_start.replace(minute = self.event_start.minute - 30)

		if self.has_takedown_tech or self.has_entire_event_tech:
			self.takedown_end = to_time
		# if from_time != datetime.strptime('5:00 PM', "%I:%M %p").time():
		# 	self.event_end = from_time
		if abs(timedelta(hours = to_time.hour, minutes = to_time.minute) - timedelta(hours = self.event_end.hour, minutes = self.event_end.minute)) < timedelta(minutes = 30):
			if self.event_end.minute + 30 > 59:
				new_minutes = 30 - (60 - self.event_end.minute)
				self.takedown_end = self.event_end.replace(hour = self.event_end.hour + 1, minute = new_minutes)
			else:
				self.takedown_end = self.event_end.replace(minute = self.event_end.minute + 30)


		print('@@@@@@@@@@@@@@@@@')
		print(self.room[0])
		print(self.event_title)
		print(f'Res start: {self.reservation_start.strftime("%I:%M %p")} su start: {self.setup_start.strftime("%I:%M %p")} ev start: {self.event_start.strftime("%I:%M %p")} ev end: {self.event_end.strftime("%I:%M %p")} td end: {self.takedown_end.strftime("%I:%M %p")} res end: {self.reservation_end.strftime("%I:%M %p")}')
		print('@@@@@@@@@@@@@@@@@\n\n')

	def extract_times_from_text(self, line_num, all_found_times):
		times = self.raw_text[line_num].split(' from ')[1].split(' to ')
		from_time = datetime.strptime(times[0], "%I:%M %p").time()
		to_time = datetime.strptime(times[1][:-1], "%I:%M %p").time()

		all_found_times.extend([from_time,to_time])
		return from_time, to_time


