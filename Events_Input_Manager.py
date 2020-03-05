from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import re

#######
# Need to change authentication to work with anyone
#######

class Events_Input_Manager:

	def __init__(self, raw_text, username, password):
		self.raw_text = raw_text
		self.username = username
		self.password = password
		self.num_events, self.event_start_line = self.count_events(raw_text)
		self.num_lines_per_event = 10

	def input_events(self):
	
		date = self.raw_text[0].rstrip().split(" ")
		year = date[-3]
		month = date[-2]
		day = date[-1]

		categories_file = open("Event Categories Index.txt", "r")
		category_options = categories_file.readlines()
		resources_file = open("Event Resources Index.txt", "r")
		resources_options = resources_file.readlines()

		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(1)

		
		for event_num in range(self.num_events):
			spaces_list, year_dropdown, month_dropdown, day_dropdown, setup_dropdown, event_start_dropdown, event_end_dropdown, breakdown_dropdown, category_dropdown, resource_list, technicians_list, comments_box = self.load_website()

			current_event_start_line = self.event_start_line + (event_num * self.num_lines_per_event)
			room, setup_start, setup_end, takedown_start, takedown_end, event_resources, event_category, comment = self.get_event_details(current_event_start_line)

			spaces_list.select_by_visible_text(room)

			year_dropdown.select_by_visible_text(year)
			month_dropdown.select_by_visible_text(month)
			day_dropdown.select_by_visible_text(day)

			setup_dropdown.select_by_visible_text(setup_start)
			event_start_dropdown.select_by_visible_text(setup_end)
			event_end_dropdown.select_by_visible_text(takedown_start)
			breakdown_dropdown.select_by_visible_text(takedown_end)

			category_dropdown.select_by_visible_text(self.select_options(category_options, event_category))
			for resource in event_resources:
				resource_list.select_by_visible_text(self.select_options(resources_options, resource))

			if comment != "**":
				comments_box.send_keys(comment)

			self.driver.find_element_by_name('Submit').click()
			self.driver.switch_to.alert.accept()

		print('Closing driver')
		self.driver.quit()

	def load_website(self):
		self.driver.get(f"https://{self.username}:{self.password}@hosting.med.upenn.edu/avs/index.php?page=addevent")

		# Get all website elements that must be manipulated
		spaces_list = Select(self.driver.find_element_by_name('avsRoom'))

		year_dropdown = Select(self.driver.find_element_by_name('year'))
		month_dropdown = Select(self.driver.find_element_by_name('month'))
		day_dropdown = Select(self.driver.find_element_by_name('day'))

		setup_dropdown = Select(self.driver.find_element_by_name('eventSetupStartTime'))
		event_start_dropdown = Select(self.driver.find_element_by_name('eventStartTime'))
		event_end_dropdown = Select(self.driver.find_element_by_name('eventEndTime'))
		breakdown_dropdown = Select(self.driver.find_element_by_name('eventBreakdownEndTime'))

		category_dropdown = Select(self.driver.find_element_by_name('eventCategory'))
		resource_list = Select(self.driver.find_element_by_name('eventResources[]'))
		technicians_list = Select(self.driver.find_element_by_name('eventTechnician[]'))

		comments_box = self.driver.find_element_by_name('eventCommentsNotes')

		return spaces_list, year_dropdown, month_dropdown, day_dropdown, setup_dropdown, event_start_dropdown, event_end_dropdown, breakdown_dropdown, category_dropdown, resource_list, technicians_list, comments_box

	def count_events(self,raw_text):
		event_count = 0
		first_event_found = False
		for line in range(len(raw_text)):
			if raw_text[line] == '------------------------------------------------------------\n': 
				event_count += 1
				if not first_event_found:
					first_event_found = True
					event_start_line = line + 1

		return event_count, event_start_line

	def get_event_details(self, current_event_start_line):
		room = self.raw_text[current_event_start_line].rstrip()

		setup_start = self.format_time(self.raw_text[current_event_start_line + 2].rstrip().split('\t')[2])
		setup_end = self.format_time(self.raw_text[current_event_start_line + 3].rstrip().split('\t')[2])
		takedown_start = self.format_time(self.raw_text[current_event_start_line + 4].rstrip().split('\t')[2])
		takedown_end = self.format_time(self.raw_text[current_event_start_line + 5].rstrip().split('\t')[2])

		event_resources = self.raw_text[current_event_start_line + 6].rstrip()[17:].split(',')
		for idx,resource in enumerate(event_resources):
			event_resources[idx] = resource.lstrip().rstrip()

		event_category = self.raw_text[current_event_start_line + 7][16:].rstrip().lstrip()
		comment = self.raw_text[current_event_start_line + 8][11:].rstrip()
		
		print("Inputting event with details:")
		print(f"'{room}'")
		print(f"'{setup_start}'")
		print(f"'{setup_end}'")
		print(f"'{takedown_start}'")
		print(f"'{takedown_end}'")
		print(f"'{event_resources}'")
		print(f"'{event_category}'")
		print(f"'{comment}'")
		print()

		return room, setup_start, setup_end, takedown_start, takedown_end, event_resources, event_category, comment

	def select_options(self, options, selector):
		for line in options:
			if line[0:2] == selector:
				return line[3:].rstrip() 

	def format_time(self, time):
		return time[:-3] + ":00" + time[-3:]

