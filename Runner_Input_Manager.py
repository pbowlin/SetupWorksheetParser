from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class Runner_Input_Manager:

	def __init__(self, runner_campus, AM_runner, AM_room, AM_time, PM_runner, PM_room, PM_time):
		self.runner_campus = runner_campus
		self.AM_runner = AM_runner
		self.AM_room = AM_room
		self.AM_time = AM_time
		self.PM_runner = PM_runner
		self.PM_room = PM_room
		self.PM_time = PM_time

	def input_runners(self):
		runners_file = open("Generated Files/" + self.runner_campus + " Runner List.txt", "r")

		runners = runners_file.readlines()

		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(1)

		# Get the date of the schedule from the runner list.
		date = runners[1].split(" ")
		year = date[1]
		month = date[2]
		day = date[3]

		room_list = self.get_room_list(runners)

		self.input_first_room_with_comment(room_list[0],year, month, day)
		self.input_remaining_runner_rooms(room_list[1:], year, month, day)

		print('Closing driver')
		self.driver.quit()

	def get_room_list(self, runners):
		room_list = set()
		runner_room_start_line = 2 #Line 0 and 1 of the file are the header and the date, respectively, so runners always start on line 2.

		# Get the rooms from the runner list
		for line_num in range(runner_room_start_line, len(runners)):
			room_list.add(runners[line_num][:-1]) # The reason for the [:-1] is to get rid of the new line character

		room_list = sorted(room_list) # converts the set to an ordered list
		return room_list

	def input_first_room_with_comment(self, room, year, month, day):
		spaces_list, year_dropdown, month_dropdown, day_dropdown, category_dropdown, technicians_list, comments_box = self.load_website()

		spaces_list.select_by_visible_text(room)

		year_dropdown.select_by_visible_text(year)
		month_dropdown.select_by_visible_text(month)
		day_dropdown.select_by_visible_text(day)

		if self.runner_campus == 'Main Campus':
			comment_campus = ''
			category_dropdown.select_by_value('23') ## Main campus runner (AM and PM)
		elif self.runner_campus == 'JMEC':
			comment_campus = 'JMEC'
			category_dropdown.select_by_value('26') ## SCTR and JMEC campus runner (AM and PM)
		elif self.runner_campus == 'SCTR':
			comment_campus = 'SCTR'
			category_dropdown.select_by_value('26') ## SCTR and JMEC campus runner (AM and PM)

		technicians_list.select_by_visible_text(self.AM_runner)
		technicians_list.select_by_visible_text(self.PM_runner)

		AM_initials, PM_initials = self.convert_name_to_initials()

		runner_comment = f'** AM {comment_campus} Runner {AM_initials} to unlock {self.AM_room} @ {self.AM_time} ** PM {comment_campus} Runner {PM_initials} to lock up {self.PM_room} @ {self.PM_time}'
		comments_box.send_keys(runner_comment)

		self.driver.find_element_by_name('Submit').click()
		self.driver.switch_to.alert.accept()

	def input_remaining_runner_rooms(self, room_list, year, month, day):
		spaces_list, year_dropdown, month_dropdown, day_dropdown, category_dropdown, technicians_list, comments_box = self.load_website()

		year_dropdown.select_by_visible_text(year)
		month_dropdown.select_by_visible_text(month)
		day_dropdown.select_by_visible_text(day)

		if self.runner_campus == 'Main Campus':
			category_dropdown.select_by_value('23') ## Main campus runner (AM and PM)
		else:
			category_dropdown.select_by_value('26') ## SCTR and JMEC campus runner (AM and PM)

		technicians_list.select_by_visible_text(self.AM_runner)
		technicians_list.select_by_visible_text(self.PM_runner)

		for room in room_list:
			spaces_list.select_by_visible_text(room)

		self.driver.find_element_by_name('Submit').click()
		self.driver.switch_to.alert.accept()

	def load_website(self):
		self.driver.get("https://hosting.med.upenn.edu/avs/index.php?page=runner")

		# Get all website elements that must be manipulated
		spaces_list = Select(self.driver.find_element_by_name('eventRooms[]'))
		year_dropdown = Select(self.driver.find_element_by_name('year'))
		month_dropdown = Select(self.driver.find_element_by_name('month'))
		day_dropdown = Select(self.driver.find_element_by_name('day'))
		category_dropdown = Select(self.driver.find_element_by_name('eventCategory'))
		technicians_list = Select(self.driver.find_element_by_name('eventTechnician[]'))
		comments_box = self.driver.find_element_by_name('eventCommentsNotes')

		return spaces_list, year_dropdown, month_dropdown, day_dropdown, category_dropdown, technicians_list, comments_box

	def convert_name_to_initials(self):
		AM_names = self.AM_runner.split(" ")
		AM_initials = ''

		PM_names = self.PM_runner.split(" ")
		PM_initials = ''

		for name in AM_names:
			AM_initials += name[0].upper()

		for name in PM_names:
			PM_initials += name[0].upper()

		return AM_initials, PM_initials



