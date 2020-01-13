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

	def parse_space(self, space):
		space_info = space.split(",")

		if len(space_info) > 2:
			building = space_info[-1]
			room = ','.join(space_info[:-1])
		else:
			room = space_info[0]
			building = space_info[1]

		room = self.clean_room_name(room)

		return building, room

	def clean_room_name(self,room):
		if room[-1] == '*' or room[-1] == '+':
			room = room[:-1]

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






