from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


##########################
## TODO:
## Must clean the room names better so they match the schedule website's list
## Potentially also should rename some rooms in the schedule website list
##
## Can have the user modify text files with info that is difficult to get (category for non runner events) prior to running selenium.
##########################


parser_run = input('Have you already run the worksheet parser for the day in question? You must do that before running this program. (Type "y" for yes, "n" for no) ')


if parser_run.lower() != 'y':
	print('The worksheet parser creates a few files containing runner lists for the day in question. These files are necessary for this program to run properly.')
	print('Please run the worksheet parser and then come back and run this program.')
else:

	runner_type = input('Which runners would you like to input? (Type "m" for main campus, "j" for JMEC, or "s" for SCTR). ')

	if runner_type != "m" and runner_type != "j" and runner_type != "s":
		print('Invalid input. Please enter either "m", "j", or "s"')
	else:
		
		if runner_type == "m":
			runners_file = open("Main Campus Runner List.txt", "r")
		elif runner_type == "j":
			runners_file = open("JMEC Runner List.txt", "r")
		elif runner_type == "s":
			runners_file = open("SCTR Runner List.txt", "r")

		runners = runners_file.readlines()

		driver = webdriver.Firefox()
		driver.implicitly_wait(1)

		# Get the date of the schedule from the runner list.
		date = runners[1].split(" ")
		year = date[1]
		month = date[2]
		day = date[3]


		room_list = set(())
		runner_room_start_line = 4

		# Get the rooms from the runner list
		for line_num in range(runner_room_start_line, len(runners)):
			room_list.add(runners[line_num][:-1]) # The reason for the [:-1] is to get rid of the new line character

		# Input the rooms into the system
		for room in room_list:
			driver.get("https://hosting.med.upenn.edu/avs/index.php?page=runner")

			# Get all website elements that must be manipulated
			rooms_list = Select(driver.find_element_by_name('eventRooms[]'))
			year_dropdown = Select(driver.find_element_by_name('year'))
			month_dropdown = Select(driver.find_element_by_name('month'))
			day_dropdown = Select(driver.find_element_by_name('day'))
			category_dropdown = Select(driver.find_element_by_name('eventCategory'))
			technicians_list = Select(driver.find_element_by_name('eventTechnician[]'))
			comments_box = driver.find_element_by_name('eventCommentsNotes')

			rooms_list.select_by_visible_text(room)

			year_dropdown.select_by_visible_text(year)
			month_dropdown.select_by_visible_text(month)
			day_dropdown.select_by_visible_text(day)

			category_dropdown.select_by_value('23') ## Main campus runner (AM and PM)

			technicians_list.select_by_visible_text('Joseph Lavin')
			technicians_list.select_by_visible_text('Kyle Albasi')

			comments_box.send_keys('Test4')

			driver.find_element_by_name('Submit').click()
			driver.switch_to.alert.accept()

		print('Closing driver')
		driver.quit()