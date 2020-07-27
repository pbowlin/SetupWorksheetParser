from Page import Page
from Event import Event
import copy
import re
import PyPDF2

#####################
## WORKSHEET PARSER
##
## This program will automatically parse the "Daily Resource Meeting by Bldg & Rm" setup worksheet
## from EMS and output a new PDF formatted in the appropriate manner for the MTP daily schedule.
##
## To run, it needs the worksheet to be exported as both a PDF and as a txt file and for those files
## to be placed inside the SetupWorksheetParser folder with the rest of the program's files.
## Those files must be named "Setup Worksheet.pdf" and "Setup Worksheet.txt" respectively, which
## are the default names of the exports.
#####################
print("\n\n\n\n")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+              Welcome to the Worksheet Parser                 +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

print('Opening text file for parsing...')
file = open("Setup Worksheet.txt", "r")
raw_text = file.readlines()

print('Parsing worksheet pages...')
# This array stores the page number that is associated with every line in the raw text file
page_numbers_of_raw_lines = [None] * len(raw_text)
page_numbers_of_raw_lines[0] = 0
page_numbers_of_raw_lines[1] = 0

pages = []
current_page_raw_lines = []
current_page_num = 1
for line in range(2,len(raw_text)):
	## Flow: Check for new line, if it is then create a new page with raw_text
	## empty raw_text array, increment page counter
	## What if the next page doesn't start with a space up top
		## Could happen when the next page starts with a new event (in which case the top line is a d,t,t,t string)
		## Could happen when the next page starts with the continuation of the previous event (in which case the top line is Date, Res Start, Evt start, etc)
			## So just check for both the above cases every time
	page_numbers_of_raw_lines[line] = current_page_num

	if (not raw_text[line].strip() and current_page_raw_lines[-1] == "University of Pennsylvania, Perelman School of ,Setup Worksheet\n") or line == len(raw_text)-1:
		
		# We have now stored all the raw text of a single page
		# First check to see if the page does not start with a room/building at the top:
		date_and_event_times_string = re.match('\\d{1,2}/\\d{1,2}/\\d{4},\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M', current_page_raw_lines[0])
		date_and_event_times_header = re.match('Date,Res Start,Evt Start,Evt End,Res End', current_page_raw_lines[0])

		if (date_and_event_times_string or date_and_event_times_header):
			# The page did not start with a space, so go to the previous page and use that space
			space = pages[-1].space
		else:
			space = current_page_raw_lines[0]

		page = Page(copy.deepcopy(current_page_raw_lines), current_page_num, space)
		current_page_num += 1
		current_page_raw_lines.clear()
		pages.append(page)

	else:
		current_page_raw_lines.append(raw_text[line])

# Comment block for testing page parse worked as expected
	# print('page info: ')
	# print(pages[0].room)
	# print(pages[0].building)
	# print(pages[0].page_number)

	# print('line 170 should be on page 9:')
	# print(page_numbers_of_raw_lines[178])

	# print(raw_text[178])

	# print("No header page:")
	# print(pages[-4].space)
	# print(pages[-4].raw_text)

	# for p in pages:
	# 	print('-----------------------')
	# 	print(p.raw_text[0])
	# 	print(p.raw_text[1])
	# 	print(p.raw_text[2])

	# print(len(raw_text))
	# print(raw_text[482])
	# print(raw_text[483])
	# print(raw_text[483].strip())
	# print("+++++++++++++")


	# print("page:")
	# print(pages[3])

	# print("page raw:")
	# print(pages[3].raw_text)

	# print("page number:")
	# print(pages[3].page_number)

	# print("page raw lines:")
	# for line in pages[-2].raw_text:
	# 	print(line)


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

print('Parsing worksheet events...')
# Now iterate through the raw text again and extract event information
events_per_space = {}
current_event_raw_lines = []
event_start_line = 4
current_event_raw_lines.append(raw_text[event_start_line])
for line in range(event_start_line + 1,len(raw_text)):
	event_start_tag = re.match('\\d{1,2}/\\d{1,2}/\\d{4},\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M', raw_text[line])
	if event_start_tag or line == len(raw_text) - 1:
		# We are at the start of the next event, so take all the copied info for the current event and create and create a new event with it.

		# First figure out if the new event is at the top of a new page -- this affects the previous event's end line (which affects the pages that event is on)
		if re.match('Date,Res Start,Evt Start,Evt End,Res End', raw_text[line - 1]):
			# New event is at the start of the page (in the typical format with the full page header)
			event_end_line = line - 3
		else:
			# New event is either in the middle of a page, or it is at the start of a new page with the atpycal header that doesn't have the
			# building/space or the "Date, res start, event start, etc" lines at the top.
			# In the second case its fine to just subtract one as well, because that will bring us to the page break blank line, which is part of the previous page.
			event_end_line = line - 1

		building = pages[page_numbers_of_raw_lines[event_start_line]-1].building
		room = pages[page_numbers_of_raw_lines[event_start_line]-1].room
		event = Event(copy.deepcopy(current_event_raw_lines), building, room)

		#Add the new event to its corresponding page's list of events (single events can span multiple pages)
		num_pages = page_numbers_of_raw_lines[event_end_line] - page_numbers_of_raw_lines[event_start_line]
		for page_range in range(num_pages + 1):
			pages[page_numbers_of_raw_lines[event_start_line] - 1 + page_range].events.append(event)

		current_event_raw_lines.clear()
		event_start_line = line

		if event.has_tech:
			if events_per_space.get(event.room[0]):
				## Room is already in the dictionary so just add the new event to the rooms list of events
				events_per_space.get(event.room[0]).append(event)
			else: ## Room is not in the dictionary so create a new entry with this event
				events_per_space[event.room[0]] = [event]


	current_event_raw_lines.append(raw_text[line])


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print('Marking pages with techs/runners/flags...')
for page in pages:
	page.check_for_techs_and_runners_and_flags()

# Comment block for testing that events are properly assigned to pages
	# print('test events on page: ')

	# counter = 0
	# for page in pages:
	# 	counter += 1
	# 	print(f'Page number : {counter}, events: {len(page.events)} ')

	# print(pages[-2].events[0].raw_text)

	# for event in pages[-2].events:
	# 	print('-----------------------------')
	# 	print(event.raw_text)

# Comment block for testing line stripping and Regex
	# current_page_num = 1
	# for line in range(2,len(raw_text)-1):
	# 	if not raw_text[line].strip():
	# 		current_page_num += 1

	# test = raw_text[4].split(",")
	# for x in test:
	# 	print(x)

	# test = raw_text[13].split(",")
	# for x in test:
	# 	print(x)


	# m = re.match('\\d{1,2}/\\d{1,2}/\\d{4}', '01/13/2009,12/1/2019, hjdkhfjkds, 3/09/2013')
	# if m:
	# 	print(m.group())

	# # Match on a string with Date,time,time,time,time  --- Which will correspond to the date, SU, start, end, BD of a single event.
	# m = re.match('\\d{1,2}/\\d{1,2}/\\d{4},\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M,\\d{1,2}:\\d{1,2} (A|P)M', raw_text[4])
	# if m:
	# 	print(m.group())

# Comment Block for testing event info parsing works correctly.
	# print(pages[0].events[0].building)
	# print(pages[0].events[0].room)
	# print(pages[0].events[0].date)
	# print(pages[0].events[0].reservation_start)
	# print(pages[0].events[0].event_start)
	# print(pages[0].events[0].event_end)
	# print(pages[0].events[0].reservation_end)
	# print(pages[0].events[0].event_title)

	# for page in pages:
	# 	page.check_for_keep_or_duplicate()
	# 	print(page.keep_page)
	# 	print(page.duplicate_page)
	# 	print(page.page_has_flags)
	# 	print()


# Now we have the entire worksheet parsed by page and event. We have marked which pages to keep, so now we must create a new PDF file with only those pages.
# I think really what I should do is pre-organize the file by creating a new array of page numbers, then just loop through that with the PDF writer and add
# all the pages based on those numbers.
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print('Re-ordering pages and creating event/runner list files...')
tech_event_pages = []
main_campus_runners = []
jmec_runners = []
sctr_runners = []
undetermined_runners = []
flagged_pages = []

date_day = pages[0].events[0].date.strftime("%-d")
date_month = pages[0].events[0].date.strftime("%B")
date_year = pages[0].events[0].date.strftime("%Y")

events_list_file = open('Generated Files/Events List.txt','w')
events_list_file.write(f'Events listed by space for {date_year} {date_month} {date_day} \n')
events_list_file.write('Note that you MUST check this file over to ensure the information in it is correct before running the auto input program. \n')
# events_list_file.write('When you have done this, delete the safety lock below and the auto input program will then be able to run. \n')
# events_list_file.write('\n')
# events_list_file.write('*** PROGRAM LOCK - AFTER CHECKING THIS FILE, DELETE THIS LINE TO ALLOW THE EVENT INPUT PROGRAM TO RUN ***\n')
events_list_file.write('\n')

for space in events_per_space:
	print(space)
	if len(space) >= 6 and space[:6] != "NO MTP":
		for e in events_per_space[space]:
			print(f'	{e.event_title}')
			events_list_file.write(f'------------------------------------------------------------\n')
			events_list_file.write(f'{space} \n')		
			events_list_file.write(f'{e.event_title} \n')
			events_list_file.write(f'	Setup Start:	{e.setup_start.strftime("%I:%M %p").lstrip("0")} \n')
			events_list_file.write(f'	Setup End:	{e.setup_end.strftime("%I:%M %p").lstrip("0")} \n')
			events_list_file.write(f'	Takedown Start:	{e.takedown_start.strftime("%I:%M %p").lstrip("0")} \n')
			events_list_file.write(f'	Takedown End:	{e.takedown_end.strftime("%I:%M %p").lstrip("0")} \n')
			events_list_file.write(f'	Event Resources: \n')
			events_list_file.write(f'	Event Category: \n')
			events_list_file.write(f'	Comments: ** {e.comment} \n')
			events_list_file.write(f'	Event Reviewed: No \n')
			# events_list_file.write(f'\n')


mc_runner_list = open('Generated Files/Main Campus Runner List.txt','w')
mc_runner_list.write('Main Campus Runners:\n')
mc_runner_list.write("Date: " + date_year + " " + date_month + " " + date_day + " \n")

jmec_runner_list = open('Generated Files/JMEC Runner List.txt','w')
jmec_runner_list.write('JMEC Runners:\n')
jmec_runner_list.write("Date: " + date_year + " " + date_month + " " + date_day + " \n")

sctr_runner_list = open('Generated Files/SCTR Runner List.txt','w')
sctr_runner_list.write('SCTR Runners:\n')
sctr_runner_list.write("Date: " + date_year + " " + date_month + " " + date_day + " \n")

for page_num in range(len(pages)):
	current_page = pages[page_num]
	
	if len(current_page.raw_text) > 2: # Eliminate "blank" pages (they are two lines cause they have only the footer on the page.)
		if current_page.has_tech:
			# print(f'"{current_page.building}"')
			# print(len(current_page.building))
			if current_page.building.rstrip() != "No Assignment":
				tech_event_pages.append(page_num)

		if current_page.has_runner:
			if current_page.campus == 'Main Campus':
				main_campus_runners.append(page_num)
				for room in current_page.room:
					mc_runner_list.write(room + "\n")
			elif current_page.campus == 'JMEC':
				jmec_runners.append(page_num)
				for room in current_page.room:
					jmec_runner_list.write(room + "\n")
			elif current_page.campus == 'SCTR':
				sctr_runners.append(page_num)
				for room in current_page.room:
					sctr_runner_list.write(room + "\n")
			else:
				undetermined_runners.append(page_num)

		if current_page.has_flags:
			flagged_pages.append(page_num)

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print('Creating final PDF...')

date_formatted = pages[0].events[0].date.strftime("%m.%d.%y")
output_PDF_title = date_formatted + " AV Schedule.pdf"

undoctored_PDF = open('Setup Worksheet.pdf','rb')
utility_PDF = open('UtilityPages.pdf','rb')
output_PDF = open("Generated Files/" + output_PDF_title,'wb')

worksheet_reader = PyPDF2.PdfFileReader(undoctored_PDF)
utility_reader = PyPDF2.PdfFileReader(utility_PDF) 
pdf_writer = PyPDF2.PdfFileWriter()

# Add all pages with tech events
for p in tech_event_pages:
	pdf_writer.addPage(worksheet_reader.getPage(p))

pdf_writer.addPage(utility_reader.getPage(0)) # Add the main campus runner header page

# Add all pages with main campus runners
for p in main_campus_runners:
	pdf_writer.addPage(worksheet_reader.getPage(p))

pdf_writer.addPage(utility_reader.getPage(1)) # Add the JMEC runner header page

# Add all pages with JMEC runners
for p in jmec_runners:
	pdf_writer.addPage(worksheet_reader.getPage(p))

pdf_writer.addPage(utility_reader.getPage(2)) # Add the SCTR runner header page

# Add all pages with SCTR runners
for p in sctr_runners:
	pdf_writer.addPage(worksheet_reader.getPage(p))

if len(undetermined_runners) > 0:
	pdf_writer.addPage(utility_reader.getPage(3)) # Add the undetermined runners header page

	# Add all pages with undetermined runners
	for p in undetermined_runners:
		pdf_writer.addPage(worksheet_reader.getPage(p))

# Write the final PDF
pdf_writer.write(output_PDF)

# print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# print('Creating runner list file...')

# runner_list = open('Runner Lists.txt','w')
# runner_list.write('Main Campus Runners:')

# for page in pages:
# 	for event in page.events:


# for runner in main_campus_runners:
# 	runner_list.write(runner)

print('Done! The formatted PDF schedule is called "[Date] AV Schedule.pdf" where [Date] is the date of events in the schedule.')
print("The file is located in the 'Generated Files' sub folder of the folder that houses all the rest of the program's files.")

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+            Thanks for using the Worksheet Parser             +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("\n\n\n\n")



