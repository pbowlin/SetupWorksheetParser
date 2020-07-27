from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import re
import time



class Past_Weeks_Tech_Time_Input_Manager:

	def __init__(self, data, username, password):
		self.data = data
		self.username = username
		self.password = password

	def input_events(self):

		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(1)

		count = 0
		
		for idx, event in enumerate(self.data):
			# print()
			# print(event)
			if event['Add'] == "x": ## For some reason the UTF-8 encoding gets tagged onto the first column header?
				spaces_list, year_dropdown, month_dropdown, day_dropdown, setup_dropdown, event_start_dropdown, event_end_dropdown, breakdown_dropdown, category_dropdown, resource_list, technicians_list, comments_box = self.load_website()

				year, month, day, setup_start, setup_end, takedown_start, takedown_end, event_resources, event_category, tech, comment = self.get_event_details(event)


				if count % 6 < 2:
					room = "Remote Support Log 1"
				elif count % 6 < 4:
					room = "Remote Support Log 2"
				elif count % 6 == 4:
					room = "Remote Support Log 3"
				else:
					room = "Remote Support Log 4"

				count += 1


				print("Inputting event with details:")
				print(f"CSV Row Number: {idx + 2}")
				print(f"'{month} {day}, {year}'")
				print(f"'{tech}'")
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

				technicians_list.select_by_visible_text(tech)

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

		setup_start = self.format_time(event['Start'])

		if event['End'] == '':
			takedown_start = setup_start
		else:
			takedown_start = self.format_time(event['End'])

		## If there was originally no AM or PM on the time we had to guess if it was AM or PM. I do so below by setting anything that is 12, 1, 2, 3, 4, 5, and 6 to PM.
		## This assumption can create errors in when the start and end times are taken in tandem that result in invalid start/end times. There are two cases of bad times. Examples:
		##	1. Original start/end was 4/8... both should be PM but the guess would make it 4pm/8am which is invalid.
		##	2. Original start/end was 10/8... it should be 10am/8pm but the guess would make it 10am/8am which is invalid.
		## So we must correct for these scenarios.
		## Note that it could get the times wrong in other scenarios (ie the times could be 8(pm)/9(pm) but the guess would make it 8am/9am) but the resulting start/end times are not INVALID 
		## so it doesn't really matter because they will still enter into the system without issue.
		setup_start, takedown_start = self.fix_invalid_am_pm(setup_start, takedown_start)

		setup_start, takedown_start = self.adjust_times(setup_start, takedown_start)

		setup_end = setup_start
		takedown_end = takedown_start

		event_resources = ['']

		event_category = event['Category']

		tech = event['Technician']

		comment = f"** {event['Assignment']}: {event['Details']}"
		
		return year, month, day, setup_start, setup_end, takedown_start, takedown_end, event_resources, event_category, tech, comment


	def format_time(self, time):
		time = time.rstrip()

		# First check to ensure the time is labeled with AM or PM, Three cases:
		#	1. Last character in time is "M" (Time is correctly labeled with AM or PM)
		#	2. Last character in time is "A" or "P" (Add in the "M")
		#	3. Last Last character in time is none of the above (Add "AM" or "PM" based on time value)
		am_pm = time[-1:].upper()

		if am_pm == "A" or am_pm == "P":
			time = time + "M"
			am_pm = "M"

		if am_pm != "M":
			time = self.add_am_pm(time)

		times = time[:-2].split(':')
		if len(times) > 1: # Time is already in HH:MMam/pm format
			return time[:-2] + ":00 " + time[-2:].upper()
		else:
			return time[:-2] + ":00:00 " + time[-2:].upper()


	def add_am_pm(self, time):
		hour = int(time.split(':')[0])
		if hour == 12 or hour < 7:
			return f"{time} PM"
		else:
			return f"{time} AM"

	def fix_invalid_am_pm(self, start, end):
		if start[-2:] == "PM" and end[-2:] == "AM":
			return start, f"{end[:-2]}PM"

		if start[-2:] == "PM" and end[-2:] == "PM":
			start_hour = int(start.split(':')[0])
			end_hour = int(end.split(':')[0])
			if start_hour == 12:
				start_hour = 0
			if end_hour == 12:
				end_hour = 0
			if start_hour > end_hour:
				return f"{start[:-2]}AM", end

		return start, end


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
		# print(time)
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
		date_split = date.split(' ')

		year = date_split[2]
		month = date_split[0]
		day = date_split[1]

		return year, month, day






