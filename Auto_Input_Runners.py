from Runner_Input_Manager import Runner_Input_Manager


##########################
## TODO:
## Must clean the room names better so they match the schedule website's list
## Potentially also should rename some rooms in the schedule website list
##
## Can have the user modify text files with info that is difficult to get (category for non runner events) prior to running selenium.
##
##
## Check Page.py file for notes to finish cleaning room names for input.
##########################

############
## Add initial load test in runner input to make sure it can find all the spaces/names/etc it needs to, so if it can't it will 
## error out without adding anything.
############


print("\n\n\n\n")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+            Welcome to the Runner Input Program               +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

parser_run = input('Have you already run the worksheet parser for the day in question? You must do that before running this program. (Type "y" for yes, "n" for no) ')


if parser_run.lower() != 'y':
	print('The worksheet parser creates a few files containing runner lists for the day in question. These files are necessary for this program to run properly.')
	print('Please run the worksheet parser and then come back and run this program.')
else:
	runner_campus = input('Which runners would you like to input? (Type "m" for main campus, "j" for JMEC, or "s" for SCTR). ')

	if runner_campus != "m" and runner_campus != "j" and runner_campus != "s":
		print('Invalid input. Please enter either "m", "j", or "s"')
	else:

		if runner_campus == "m":
			runner_campus = "Main Campus"
		elif runner_campus == "j":
			runner_campus = "JMEC"
		elif runner_campus == "s":
			runner_campus = "SCTR"

		AM_runner = input('\nWho will be the AM runner? (Your input must exactly match how the name is written in the schedule website\'s technician list). ')
		AM_room = input('And what room will the AM runner need to open first? ')
		AM_time = input('And at what time must that room be opened? ')

		PM_runner = input('\nWho will be the PM runner? (Your input must exactly match how the name is written in the schedule website\'s technician list). ')
		PM_room = input('And what will be the last room the PM runner will need to close down? ')
		PM_time = input('And at what time must that room be locked up? ')

		manager = Runner_Input_Manager(runner_campus, AM_runner, AM_room, AM_time, PM_runner, PM_room, PM_time)
		manager.input_runners()

print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+          Thanks for using the Runner Input Program           +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("\n\n\n\n")