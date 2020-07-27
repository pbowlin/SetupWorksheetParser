from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import re
import time


## NEED TO HANDLE TIMES WHERE NO AM/PM IS ADDED TO END

class Nolde_Input_Manager:

	def __init__(self, data, username, password):
		self.data = data
		self.username = username
		self.password = password
		self.tech_name = "Michael Nolde"

	def input_events(self):

		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(1)

		
		for idx, event in enumerate(self.data):
			spaces_list, year_dropdown, month_dropdown, day_dropdown, setup_dropdown, event_start_dropdown, event_end_dropdown, breakdown_dropdown, category_dropdown, resource_list, technicians_list, comments_box = self.load_website()

			year, month, day, room, setup_start, setup_end, takedown_start, takedown_end, event_resources, event_category, comment = self.get_event_details(event)

			print("Inputting event with details:")
			print(f"'{idx}'")
			print(f"'{month} {day}, {year}'")
			print(f"'{comment}'")
			print(f"'{room}'")
			print(f"'{setup_start}'")
			print(f"'{setup_end}'")
			print(f"'{takedown_start}'")
			print(f"'{takedown_end}'")
			print(f"'{event_resources}'")
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
			for resource in event_resources:
				if resource != '':
					resource_list.select_by_visible_text(event_resources)

			technicians_list.select_by_visible_text(self.tech_name)

			## UNCOMMENT BELOW TO ALLOW COMMENTS TO BE ADDED TO EVENTS
			# if comment != "**":
			# 	comments_box.send_keys(comment)

			self.driver.find_element_by_name('Submit').click()
			self.driver.switch_to.alert.accept()
			time.sleep(1)

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


	def get_event_details(self, event):
		
		year, month, day = self.parse_date(event['Date'])
		room = "SPE 15: Remote Support"

		setup_start = self.format_time(event['Start Time'])

		if event['End Time'] == '':
			takedown_start = setup_start
		else:
			takedown_start = self.format_time(event['End Time'])

		setup_start, takedown_start = self.adjust_times(setup_start, takedown_start)

		setup_end = setup_start
		takedown_end = takedown_start

		event_resources = ['']

		event_category = "3: Clinical - UPHS"
		comment = "** " + event['Meeting']
		

		return year, month, day, room, setup_start, setup_end, takedown_start, takedown_end, event_resources, event_category, comment


	def format_time(self, time):
		times = time[:-2].split(':')
		if len(times) > 1: # Time is already in HH:MMam/pm format
			return time[:-2] + ":00 " + time[-2:].upper()
		else:
			return time[:-2] + ":00:00 " + time[-2:].upper()

	def adjust_times(self, start, end):

		start_hours, start_minutes, start_am_pm = self.round_time(start)

		if start == end:
			end_hours, end_minutes, end_am_pm = self.check_valid_time(start_hours, start_minutes + 15, start_am_pm)
		else:
			end_hours, end_minutes, end_am_pm = self.round_time(end)

		start_adjusted = str(start_hours) + ":" + str(f'{start_minutes:02}') + ":00 " + start_am_pm
		end_adjusted = str(end_hours) + ":" + str(f'{end_minutes:02}') + ":00 " + end_am_pm

		return start_adjusted, end_adjusted


	def round_time(self, time):
		time_split = time.split(':')
		hours = int(time_split[0])
		minutes = int(time_split[1])
		am_pm = time_split[2][-2:]

		round_value = minutes % 15
		if round_value < 7:
			minutes -= round_value
		else:
			minutes += 15 - round_value

		hours, minutes, am_pm = self.check_valid_time(hours, minutes, am_pm)

		return hours, minutes, am_pm

	def check_valid_time(self, hours, minutes, am_pm):
		if minutes >= 60:
			minutes = 0
			hours += 1

			if hours >= 12:
				hours = hours if hours == 12 else hours - 12
				am_pm = 'PM'

		return hours, minutes, am_pm

	def parse_date(self, date):
		date_split = date.split('/')

		months = ['','January', 'February', 'March', 'April','May', 'June', 'July', 'August', 'September', 'October','November','December']

		year = "20" + date_split[2]
		month = months[int(date_split[0])]
		day = date_split[1]

		return year, month, day






