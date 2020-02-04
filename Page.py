# Note that because the report is BY SPACE, each page can only refer to a single space

class Page:

	def __init__(self, raw_text, page_number, space):
		self.raw_text = raw_text
		self.page_number = page_number
		self.space = space
		self.events = []
		self.has_tech = False
		self.has_runner = False
		self.has_flags = False

		self.building, self.room = self.parse_space(space)
		self.campus = self.extract_campus_for_runners(self.building)
		self.room = self.clean_room_name(self.room)
		## Note that the room will actually be a list of "rooms" in order to accomodate pages that span
		## multiple sections of a room. i.e. JMEC 516EW will be [JMEC 516E, JMEC 516W] whereas BRB 252
		## will be just [BRB 252]

	def parse_space(self, space):
		space_info = space.split(",")

		if len(space_info) > 2:
			building = space_info[-1]
			room = ','.join(space_info[:-1])
		else:
			room = space_info[0]
			building = space_info[1]

		return building, room

	def clean_room_name(self,room):
		## Note that the room will actually be a list of "rooms" in order to accomodate pages that span
		## multiple sections of a room. i.e. JMEC 516EW will be [JMEC 516E, JMEC 516W] whereas BRB 252
		## will be just [BRB 252]

		## Need to clean JMEC 05M-AB rooms
		if room[-1] == '*' or room[-1] == '+':
			room = room[:-1]

		if self.campus == 'Main Campus' or self.campus == 'JMEC':
			room_info = room.split(" ")
			if len(room_info) == 2 and room_info[1][0] == '0':
				room_info[1] = room_info[1][1:]

			if self.campus == 'Main Campus':
				if self.building == 'Richards Building\n':
					room_info[0] = 'RCH'
					if len(room_info) == 2 and room_info[1] == 'B102AB':
						room_info[1] = 'B102A\nRCH B102B'
				
				if self.building == 'Blockley Hall\n':
					room_info[0] = 'Blockley'

				if self.building == 'John Morgan Building\n':
					if len(room_info) == 3 and room_info[1] == 'WOOD':
						room_info[1] = 'Woodroom'
						room_info = room_info[:-1]

				if self.building == 'Stemmler Hall\n':
					if len(room_info) == 2 and room_info[1] == '416-417':
						room_info[1] = '416\nSTM 417'

			elif self.campus == 'JMEC':
				# Handle room specific cases: 5M-A & B, 5-104
				if room_info[1] == '5M-A':
					room_info[1]= '5M-11 Study Lounge A'
				elif room_info[1] == '5M-B':
					room_info[1]= '5M-12 Study Lounge B'
				elif room_info[1] == '05-104':
					room_info[1]= '5-104 Conf A'
				elif len(room_info) == 2 and room_info[1][-2:] == 'EW':
					room_info[1] = f"{room_info[1][:4]}\nJMEC {room_info[1][:3]}W"

			room = ""
			for i in range(len(room_info)):
				room += room_info[i]
				if i < len(room_info)-1:
					room += " "

		elif self.campus == 'SCTR':
			if room[-2:] == 'AB':
				room = room[:-2]

		room = room.split('\n')
		## If a single event spans multiple sections of a room we have cleaned it to be on two lines at this point

		return room

	def check_for_techs_and_runners_and_flags(self):

		for event in self.events:
			if event.has_tech:
				self.has_tech = True

			if event.has_runner:
				self.has_runner = True

		if not self.has_tech and not self.has_runner:
			self.check_for_flags()

	# If an event has neither a tech nor a runner (i.e. it will be deleted) we must first check to make sure that the event has not been poorly assigned in EMS
	# by looking for certain common flags that indicate the page may want to be kept and that the appropriate resources have not been assigned to it.
	def check_for_flags(self):
		for event in self.events:
			flag = event.check_for_event_flags()

			if flag:
				self.has_flags = True

	def extract_campus_for_runners(self,building):
		main_campus = ['Anatomy-Chemistry\n','Biomedical Research Building\n','Blockley Hall\n', 'Clinical Research Building\n','John Morgan Building\n','Richards Building\n','Stellar-Chance Laboratories\n','Stemmler Hall\n']
		JMEC_campus = ['Jordan Medical Education Center\n']
		SCTR_campus = ['Smilow Center for Translational Research\n']
		campus = None

		if building in main_campus:
			campus = 'Main Campus'
		elif building in JMEC_campus:
			campus = 'JMEC'
		elif building in SCTR_campus:
			campus = 'SCTR'
		else:
			campus = 'Need human input'

		return campus






