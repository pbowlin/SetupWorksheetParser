from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import re
import time



class Supervisor_Support_Input_Manager:

	def __init__(self, data, username, password):
		self.data = data
		self.username = username
		self.password = password
		self.room = 'Admin/Manager Time'
		self.daily_time_keeper = {}
		self.day_start_time = 8.0
		self.categories = {'Academic Programs': '1.a: Academic Programs','Biomedical Graduate Studies': '1.b: Biomedical Graduate Studies','CCEB': '1.c: CCEB','Public Health': '1.d: Public Health','BioEthics': '1.e: BioEthics','Research': '2: Research','Clinical - UPHS': '3: Clinical - UPHS','MTP Administration': '5.a: MTP Administration','Administration': '5: Administration'}
		self.names = {'RR': 'Ray Rollins', 'JL': 'Joseph Lavin', 'PB': 'Peter Bowlin', 'BA': 'Beth Albasi', 'KF': 'Kevin Flanigan','EC': 'Eric Capozzoli'}

	def input_events(self):

		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(1)
		
		year = '2020'
		month = 'January'
		day = '1'

		for idx, entry in enumerate(self.data):

			if entry['Name'] != "" and len(entry['Name'].split()) == 4: ## New Day

				year, month, day  = self.parse_date(entry['Name'])
				
				## Reset times to beginning of the day (8am)
				keys = self.daily_time_keeper.keys()
				for key in keys:
					self.daily_time_keeper[key] = self.day_start_time

			elif entry['Name'] != "" and entry['Category'] != "" and entry['Hours'] != "": ## Valid entry
				entry['Name'] = entry['Name'].upper()

				spaces_list, year_dropdown, month_dropdown, day_dropdown, setup_dropdown, event_start_dropdown, event_end_dropdown, breakdown_dropdown, category_dropdown, resource_list, technicians_list, comments_box = self.load_website()

				setup_start, setup_end, takedown_start, takedown_end, event_category, supervisor = self.get_entry_details(entry)

				room = self.room


				print("Inputting entry with details:")
				print(f"CSV Row Number: {idx + 2}")
				print(f"'{month} {day}, {year}'")
				print(f"'{supervisor}'")
				print(f"'{room}'")
				print(f"'{setup_start}'")
				print(f"'{setup_end}'")
				print(f"'{takedown_start}'")
				print(f"'{takedown_end}'")
				print(f"'{event_category}'")
				print("-------------------------------------")

				spaces_list.select_by_visible_text(room)

				year_dropdown.select_by_visible_text(year)
				month_dropdown.select_by_visible_text(month)
				day_dropdown.select_by_visible_text(day)

				setup_dropdown.select_by_visible_text(setup_start)
				event_start_dropdown.select_by_visible_text(setup_end)
				event_end_dropdown.select_by_visible_text(takedown_start)
				breakdown_dropdown.select_by_visible_text(takedown_end)

				category_dropdown.select_by_visible_text(event_category)

				technicians_list.select_by_visible_text(supervisor)

				self.driver.find_element_by_name('Submit').click()
				self.driver.switch_to.alert.accept()
				time.sleep(1)
			else: ## Invalid entry -- do nothing
				pass

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


	def get_entry_details(self, entry):

		if entry['Name'] not in self.daily_time_keeper:
			self.daily_time_keeper[entry['Name']] = self.day_start_time
		
		setup_time = self.daily_time_keeper[entry['Name']]
		setup_start = setup_end = self.format_time_for_entry(setup_time)

		self.update_time(entry)

		takedown_time = self.daily_time_keeper[entry['Name']]
		takedown_start = takedown_end = self.format_time_for_entry(takedown_time)

		event_category = self.categories[entry['Category']]

		supervisor = self.names[entry['Name']]
	
		return setup_start, setup_end, takedown_start, takedown_end, event_category, supervisor

	def update_time(self, entry):
		self.daily_time_keeper[entry['Name']] = self.round_to_half(self.daily_time_keeper[entry['Name']] + float(entry['Hours']))

	def round_to_half(self, time):
		return round(time * 2)/2

	def format_time_for_entry(self, time):
		am_pm = "AM"
		if time >= 12.0:
			am_pm = "PM"

		if time >= 13.0:
			time -= 12

		time_string = str(time)
		hour, minute = time_string.split('.')

		return f"{hour}:{'30' if minute == '5' else '00'}:00 {am_pm}"

	def parse_date(self, date):
		date_split = date.split(' ')

		month = date_split[1]
		day = date_split[2][:-1]
		year = date_split[3]

		return year, month, day






