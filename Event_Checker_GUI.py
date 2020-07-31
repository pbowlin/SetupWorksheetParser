import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
# import time


class Event_Checker_GUI:

	def __init__(self, filepath, username, password):

		events_file = open(filepath, "r")
		self.raw_text = events_file.readlines()
		events_file.close()

		self.username = username
		self.password = password

		self.HEIGHT = 1200
		self.WIDTH = 800
		self.events = []
		self.current_event_displayed = 0

		date = self.raw_text[0].split(" ")
		self.date_year = date[-4]
		self.date_month = date[-3]
		self.date_day = date[-2]

		self.all_events_reviewed = False
		self.closed_with_x = False
		self.run_event_input = False

	def parse_events(self):
		num_lines_per_event = 11
		first_event_found = False
		num_events = 0
		for idx, line in enumerate(self.raw_text):
			if line == "------------------------------------------------------------\n":
				if not first_event_found:
					first_event_found = True
					event_start_line = idx + 1
				num_events += 1

		
		for e_num in range(num_events):
			room = self.raw_text[event_start_line + e_num * num_lines_per_event].strip()
			title = self.raw_text[event_start_line + e_num * num_lines_per_event + 1].strip()
			setup = self.raw_text[event_start_line + e_num * num_lines_per_event + 2][14:].strip()
			e_start = self.raw_text[event_start_line + e_num * num_lines_per_event + 3][12:].strip()
			e_end = self.raw_text[event_start_line + e_num * num_lines_per_event + 4][17:].strip()
			takedown = self.raw_text[event_start_line + e_num * num_lines_per_event + 5][15:].strip()
			
			resources = []
			for r in self.raw_text[event_start_line + e_num * num_lines_per_event + 6][18:].split(","):
				resources.append(r.strip())

			category = 	self.raw_text[event_start_line + e_num * num_lines_per_event + 7][17:].strip()
			comments = self.raw_text[event_start_line + e_num * num_lines_per_event + 8][11:].strip()
			reviewed = self.raw_text[event_start_line + e_num * num_lines_per_event + 9][17:].strip()

			event_details = {"room":room, "title":title, "setup":setup, "start":e_start, "end":e_end, "takedown":takedown, "resources":resources, "category":category, "comments":comments, "reviewed": reviewed}
			self.events.append(event_details)

		# for e in self.events:
		# 	print(e)

	def run_checker_GUI(self):
		self.parse_events()

		def on_key_release(event):
			# get text from entry
			# room.event_generate('<Down>') # This automatically shows the list when the user types, but it loses focus on the text field so the user can't type T-T
			users_letters = event.widget.get()
			users_letters = users_letters.strip().lower()
			perform_autocomplete(users_letters)

		def perform_autocomplete(users_letters):
			# get text from entry
			# users_letters = event.widget.get()
			# users_letters = users_letters.strip().lower()
			print(f'user letters : {users_letters}')
			
			# get autocomplete suggestions from room_options
			if users_letters == '':
				suggested_rooms = self.room_options
			else:
				suggested_rooms = []
				for room in self.room_options:
					if users_letters in room.lower():
						suggested_rooms.append(room)                

			# update data in listbox
			listbox_update(suggested_rooms)

		def listbox_update(suggested_rooms):
			print('in listbox update')
			# delete previous data
			####### room_autocomplete.delete(0, 'end')

			# put new data
			####### for room in suggested_rooms:
				####### room_autocomplete.insert('end', room)

			room['value'] = suggested_rooms

		def on_select(event):
			print('in select')
			print(event)
			# display element selected on list
			print('(event) previous:', event.widget.get('active'))
			print('(event)  current:', event.widget.get(event.widget.curselection()))
			print('---')
			print(event.widget.curselection())
			print(event.widget.get(event.widget.curselection()))
			room_name.set(event.widget.get(event.widget.curselection()))
			hide_autocomplete_form(None)

		def show_autocomplete_form(event):
			print('in show')
			print(event)
			room_autocomplete_frame.place(relwidth=0.8, relheight=0.5, relx=0.1, rely=0.4)
			room_autocomplete.place(relwidth=1, relheight=1)
			# listbox_update(self.room_options)
			perform_autocomplete(room_name.get().lower())

		def hide_autocomplete_form(event):
			print('in hide')
			print(event)
			# room_autocomplete.place_forget()
			# room_autocomplete_frame.place_forget()
			room_autocomplete.place_remove()
			room_autocomplete_frame.place_remove()
			root.focus()

		def close_with_x():
			if messagebox.askokcancel("Quit", "Are you sure you'd like to exit the program?\n(If you do so without clicking the Save & Exit button at the bottom of the window then you will lose all changes you've made.)", icon='warning'):
				self.closed_with_x = True
				root.destroy()

		root = tk.Tk()
		root.title('Event Checker')

		canvas = tk.Canvas(root, height=self.HEIGHT, width=self.WIDTH)
		canvas.pack()

		############
		## EVENT INFO (ROOM AND TITLE)
		############

		# font=("Helvetica", "36", "bold")
		info_frame = tk.Frame(root, bg='#80a1aa', bd=5)
		info_frame.place(relwidth=0.95, relheight=0.1, relx=0.025, rely=0.0125)

		room_name = tk.StringVar()
		# room_name.set("Room goes here")

		self.room_options = self.get_rooms_from_website()
		displayed_options = self.room_options

		room_label = tk.Label(info_frame, text="Room:", bg='#80a1aa', bd=5)
		####### room = tk.Entry(info_frame, justify="center", textvariable=room_name, font=("Helvetica", "24", "bold"))
		####### room.bind('<KeyRelease>', on_key_release)
		####### room.bind('<FocusIn>', show_autocomplete_form)
		####### room.bind('<FocusOut>', hide_autocomplete_form)
		room = ttk.Combobox(info_frame, justify="center", value=displayed_options, textvariable=room_name, font=("Helvetica", "20", "bold"))
		room.bind('<KeyRelease>', on_key_release)
		event_title_label = tk.Label(info_frame, text="Event Title:", bg='#80a1aa', bd=5)
		event_title = tk.Label(info_frame, text = "Title goes here", font=("Helvetica", "18"), bg='#80a1aa', bd=5)

		####### room_autocomplete_frame = tk.Frame(info_frame, bg='#80c1ff')
		# room_autocomplete_frame.place(relwidth=0.8, relheight=0.5, relx=0.1, rely=0.4)

		# scrollbar = tk.Scrollbar(room_autocomplete_frame)
		# scrollbar.pack(side='right', fill='y')
		# scrollbar.place(relwidth=0.1, relheight=1)

		# room_autocomplete = tk.Listbox(room_autocomplete_frame, yscrollcommand=scrollbar.set)
		####### room_autocomplete = tk.Listbox(room_autocomplete_frame)
		# room_autocomplete.pack(side='left', expand=True)
		# room_autocomplete.pack(side='left', fill='both')
		# room_autocomplete.place(relwidth=1, relheight=1)

		####### room_autocomplete.bind('<<ListboxSelect>>', on_select)
		# listbox_update(self.room_options)

		# room_autocomplete_frame.place_forget()
		
		# scrollbar.config(command=room_autocomplete.yview)

		# for r in self.room_options:
		# 	room_autocomplete.insert('end', r)

		room_label.place(relwidth=1, relheight=.15)
		room.place(relwidth=0.8, relheight=0.3, relx=0.1, rely=0.15)
		event_title_label.place(relwidth=1, relheight=.1, rely=0.6)
		event_title.place(relwidth=1, relheight=.4, rely=0.7)

		############
		## EVENT TIMES
		############
		event_time_frame = tk.Frame(root, bg='#80c1ff')
		event_time_frame.place(relwidth=0.95, relheight=0.05,relx=0.025, rely=0.125)

		# Labels
		setup_label = tk.Label(event_time_frame, text="Setup Time", bg='#80c1ff')
		estart_label = tk.Label(event_time_frame, text="Event Start Time", bg='#80c1ff')
		eend_label = tk.Label(event_time_frame, text="Event End Time", bg='#80c1ff')
		takedown_label = tk.Label(event_time_frame, text="Takedown Time", bg='#80c1ff')

		setup_label.place(relwidth=.2, relheight=.5, relx=0.04)
		estart_label.place(relwidth=.2, relheight=.5, relx=0.28)
		eend_label.place(relwidth=.2, relheight=.5, relx=0.52)
		takedown_label.place(relwidth=.2, relheight=.5, relx=0.76)

		# Variables that are bound to each entry field
		setup_time = tk.StringVar()
		# setup_time.set("12:00pm")
		estart_time = tk.StringVar()
		# estart_time.set("12:00pm")
		eend_time = tk.StringVar()
		# eend_time.set("12:00pm")
		takedown_time = tk.StringVar()
		# takedown_time.set("12:00pm")

		time_entry_vars = [setup_time, estart_time, eend_time, takedown_time]

		
		self.time_options = self.generate_time_options()

		# Entry fields
		# setup_entry = tk.Entry(event_time_frame, justify="center", textvariable=setup_time)
		setup_entry = ttk.Combobox(event_time_frame, justify="center", value=self.time_options, textvariable=setup_time)
		setup_entry.place(relwidth=.2, relheight=.5, relx=0.04, rely=0.4)

		estart_entry = ttk.Combobox(event_time_frame, justify="center", value=self.time_options, textvariable=estart_time)
		estart_entry.place(relwidth=.2, relheight=.5, relx=0.28, rely=0.4)

		eend_entry = ttk.Combobox(event_time_frame, justify="center", value=self.time_options, textvariable=eend_time)
		eend_entry.place(relwidth=.2, relheight=.5, relx=0.52, rely=0.4)

		takedown_entry = ttk.Combobox(event_time_frame, justify="center", value=self.time_options, textvariable=takedown_time)
		takedown_entry.place(relwidth=.2, relheight=.5, relx=0.76, rely=0.4)


		############
		## EVENT RESOURCES
		############

		'''
		00 ARS
		01 Audio Teleconference
		02 Harvey Doll
		03 Internet Connection
		04 IP Video Conference
		05 ISDN Video Conference
		06 Mediasite Recording
		07 Penn Video Network
		08 Prompter
		09 Sim Man
		10 Video Production/Post-Production
		11 Voip Teleconferencing
		'''

		resources_title = tk.Label(root, bg='#80a1aa', text="Event Resources", font=("Helvetica", "20", "bold"))
		resources_title.place(relheight=.03, relwidth=0.45,relx=0.025, rely=0.1875)
		resources_title_details = tk.Label(root, bg='#80a1aa', text="(Select All Applicable Resources)")
		resources_title_details.place(relheight=.02, relwidth=0.45,relx=0.025, rely=0.2175)

		resources_frame = tk.Frame(root, bg='#80c1ff')
		resources_frame.place(relheight=.5, relwidth=0.45,relx=0.025, rely=0.2375)

		# Variables that are bound to each checkbox
		ARS = tk.IntVar()
		audio_teleconference = tk.IntVar()
		harvey_doll = tk.IntVar()
		internet_connection = tk.IntVar()
		IP_video_conference = tk.IntVar()
		ISDN_video_conference = tk.IntVar()
		mediasite_recording = tk.IntVar()
		penn_video_network = tk.IntVar()
		prompter = tk.IntVar()
		sim_man = tk.IntVar()
		video_production = tk.IntVar()
		voip_teleconferencing = tk.IntVar()

		resource_vars = [ARS, audio_teleconference, harvey_doll, internet_connection, IP_video_conference, ISDN_video_conference, mediasite_recording, 
			penn_video_network, prompter, sim_man, video_production, voip_teleconferencing]

		# Checkboxes
		ARS_checkbox = tk.Checkbutton(resources_frame, text="ARS", bg='#80c1ff', variable=ARS)
		audio_teleconference_checkbox = tk.Checkbutton(resources_frame, text="Audio Teleconference", bg='#80c1ff', variable=audio_teleconference)
		harvey_doll_checkbox = tk.Checkbutton(resources_frame, text="Harvey Doll", bg='#80c1ff', variable=harvey_doll)
		internet_connection_checkbox = tk.Checkbutton(resources_frame, text="Internet Connection", bg='#80c1ff', variable=internet_connection)
		IP_video_conference_checkbox = tk.Checkbutton(resources_frame, text="IP Video Conference", bg='#80c1ff', variable=IP_video_conference)
		ISDN_video_conference_checkbox = tk.Checkbutton(resources_frame, text="ISDN Video Conference", bg='#80c1ff', variable=ISDN_video_conference)
		mediasite_recording_checkbox = tk.Checkbutton(resources_frame, text="Mediasite Recording", bg='#80c1ff', variable=mediasite_recording)
		penn_video_network_checkbox = tk.Checkbutton(resources_frame, text="Penn Video Network", bg='#80c1ff', variable=penn_video_network)
		prompter_checkbox = tk.Checkbutton(resources_frame, text="Prompter", bg='#80c1ff', variable=prompter)
		sim_man_checkbox = tk.Checkbutton(resources_frame, text="Sim Man", bg='#80c1ff', variable=sim_man)
		video_production_checkbox = tk.Checkbutton(resources_frame, text="Video Production/Post-Production", bg='#80c1ff', variable=video_production)
		voip_teleconferencing_checkbox = tk.Checkbutton(resources_frame, text="VoIP Teleconferencing", bg='#80c1ff', variable=voip_teleconferencing)

		checkbox_relwidth=0.95
		checkbox_relheight=0.06
		checkbox_relx=0.025
		checkbox_rely=0.02

		ARS_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=checkbox_rely)
		audio_teleconference_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=2*checkbox_rely + 1*checkbox_relheight)
		harvey_doll_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=3*checkbox_rely + 2*checkbox_relheight)
		internet_connection_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=4*checkbox_rely + 3*checkbox_relheight)
		IP_video_conference_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=5*checkbox_rely + 4*checkbox_relheight)
		ISDN_video_conference_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=6*checkbox_rely + 5*checkbox_relheight)
		mediasite_recording_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=7*checkbox_rely + 6*checkbox_relheight)
		penn_video_network_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=8*checkbox_rely + 7*checkbox_relheight)
		prompter_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=9*checkbox_rely + 8*checkbox_relheight)
		sim_man_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=10*checkbox_rely + 9*checkbox_relheight)
		video_production_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=11*checkbox_rely + 10*checkbox_relheight)
		voip_teleconferencing_checkbox.place(relwidth=checkbox_relwidth, relheight=checkbox_relheight, relx=checkbox_relx, rely=12*checkbox_rely + 11*checkbox_relheight)
		

		############
		## EVENT CATEGORIES
		############

		'''
		00 0.a: Control Room Operator
		07 1.a: Academic Programs
		08 1.b: Biomedical Graduate Studies
		09 1.c: CCEB
		10 1.d: Public Health
		11 1.e: BioEthics
		12 2: Research
		14 3.b.i: Video Production - SOM
		15 3.b.ii: Video Production - UPHS
		17 3: Clinical - UPHS
		20 5.a: MTP Administration
		21 5: Administration
		24 8. Simulation
		25 9. Standardized Patient
		'''

		categories_title = tk.Label(root, bg='#80a1aa', text="Event Category", font=("Helvetica", "20", "bold"))
		categories_title.place(relheight=.03, relwidth=0.45,relx=0.525, rely=0.1875)
		categories_title_details = tk.Label(root, bg='#80a1aa', text="(Select One)")
		categories_title_details.place(relheight=.02, relwidth=0.45,relx=0.525, rely=0.2175)

		categories_frame = tk.Frame(root, bg='#80c1ff')
		categories_frame.place(relheight=.5, relwidth=0.45,relx=0.525, rely=0.2375)

		# Variable that is bound to the selected radio button
		category_var = tk.StringVar()

		# Radio Buttons
		control_rm_op_rbutton = tk.Radiobutton(categories_frame, text="Control Room Operator", variable=category_var, value="00", bg='#80c1ff')
		AP_rbutton = tk.Radiobutton(categories_frame, text="Academic Programs", variable=category_var, value="07", bg='#80c1ff')
		BGS_rbutton = tk.Radiobutton(categories_frame, text="Biomedical Graduate Studies", variable=category_var, value="08", bg='#80c1ff')
		CCEB_rbutton = tk.Radiobutton(categories_frame, text="CCEB", variable=category_var, value="09", bg='#80c1ff')
		PUBH_rbutton = tk.Radiobutton(categories_frame, text="Public Health", variable=category_var, value="10", bg='#80c1ff')
		bioE_rbutton = tk.Radiobutton(categories_frame, text="BioEthics", variable=category_var, value="11", bg='#80c1ff')
		research_rbutton = tk.Radiobutton(categories_frame, text="Research", variable=category_var, value="12", bg='#80c1ff')
		vidProd_SOM_rbutton = tk.Radiobutton(categories_frame, text="Video Production - SOM", variable=category_var, value="14", bg='#80c1ff')
		vidProd_UPHS_rbutton = tk.Radiobutton(categories_frame, text="Video Production - UPHS", variable=category_var, value="15", bg='#80c1ff')
		clinical_UPHS_rbutton = tk.Radiobutton(categories_frame, text="Clinical - UPHS", variable=category_var, value="17", bg='#80c1ff')
		MTP_admin_rbutton = tk.Radiobutton(categories_frame, text="MTP Administration", variable=category_var, value="20", bg='#80c1ff')
		admin_rbutton = tk.Radiobutton(categories_frame, text="Administration", variable=category_var, value="21", bg='#80c1ff')
		simulation_rbutton = tk.Radiobutton(categories_frame, text="Simulation", variable=category_var, value="24", bg='#80c1ff')
		standardized_patient_rbutton = tk.Radiobutton(categories_frame, text="Standardized Patient", variable=category_var, value="25", bg='#80c1ff')

		rbutton_relwidth=0.95
		rbutton_relheight=0.06
		rbutton_relx=0.025
		rbutton_rely=0.01

		control_rm_op_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=1*rbutton_rely + 0*rbutton_relheight)
		AP_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=2*rbutton_rely + 1*rbutton_relheight)
		BGS_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=3*rbutton_rely + 2*rbutton_relheight)
		CCEB_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=4*rbutton_rely + 3*rbutton_relheight)
		PUBH_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=5*rbutton_rely + 4*rbutton_relheight)
		bioE_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=6*rbutton_rely + 5*rbutton_relheight)
		research_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=7*rbutton_rely + 6*rbutton_relheight)
		vidProd_SOM_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=8*rbutton_rely + 7*rbutton_relheight)
		vidProd_UPHS_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=9*rbutton_rely + 8*rbutton_relheight)
		clinical_UPHS_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=10*rbutton_rely + 9*rbutton_relheight)
		MTP_admin_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=11*rbutton_rely + 10*rbutton_relheight)
		admin_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=12*rbutton_rely + 11*rbutton_relheight)
		simulation_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=13*rbutton_rely + 12*rbutton_relheight)
		standardized_patient_rbutton.place(relwidth=rbutton_relwidth, relheight=rbutton_relheight, relx=rbutton_relx, rely=14*rbutton_rely + 13*rbutton_relheight)


		############
		## EVENT COMMENTS
		############
		comments_frame = tk.Frame(root, bg='#80c1ff', bd=5)
		comments_frame.place(relwidth=0.95, relheight=0.075,relx=0.025, rely=0.75)

		comment_label = tk.Label(comments_frame, text="Comments:", bg='#80a1aa')
		comment_label.place(relheight=0.3, relx=0, rely=0)

		comments_var = tk.StringVar()
		comments_entry = tk.Entry(comments_frame, textvariable=comments_var)
		comments_entry.place(relheight=0.7, relwidth=1, relx=0, rely=0.3)


		##########

		reviewed_var = tk.IntVar()
		self.reviewed_checkbox = tk.Checkbutton(root, text="Reviewed", variable=reviewed_var, fg='red', command=lambda:self.check_reviewed_status(reviewed_var, category_var, clicked=True, room_name=room_name, time_vars=time_entry_vars))
		self.reviewed_checkbox.place(relheight=.025, relwidth=0.1, relx=.45, rely=0.85)

		self.prev_event_button=tk.Button(root, text='Previous Event', command=lambda: self.change_event(room_name, event_title, time_entry_vars, resource_vars, category_var, comments_var, reviewed_var, next_event=False))
		self.prev_event_button.place(relheight=.025, relwidth=0.2, relx=0.2, rely=0.9)

		self.page_indicator = tk.Label(root)
		self.page_indicator.place(relheight=.025, relwidth=0.1, relx=.45, rely=0.9)

		self.next_event_button=tk.Button(root, text='Next Event', command=lambda: self.change_event(room_name, event_title, time_entry_vars, resource_vars, category_var, comments_var, reviewed_var, next_event=True))
		self.next_event_button.place(relheight=.025, relwidth=0.2, relx=0.6, rely=0.9)

		save_exit_button = tk.Button(root, text='Save & Exit', command=lambda: self.save_and_exit_GUI(root, room_name, event_title, time_entry_vars, resource_vars, category_var, comments_var, reviewed_var))
		save_exit_button.place(relheight=0.025, relwidth=0.2, relx=0.4, rely=0.95)

		date_label = tk.Label(root, text=f'{self.date_month} {self.date_day}, {self.date_year}')
		date_label.place(relheight=0.025, relwidth=0.2, relx=0.75, rely=0.95)

		self.load_info(room_name, event_title, time_entry_vars, resource_vars, category_var, comments_var, reviewed_var)
		

		root.protocol("WM_DELETE_WINDOW", close_with_x)

		# nextEventButton=tk.Button(canvas, text='Next Event', font=40, command=lambda: self.get_next_event())
		# ## Must use lambda function in the above code because otherwise it will run the code beforehand and then
		# ## will not re-run the code when the button is clicked (because we passed in a function to run i.e. foo() not foo). 
		# ## So we must use the lambda function because it is temporary and will redefine the function on every button press. 
		# nextEventButton.place(relx=0.7, relheight=1, relwidth=0.3)
		root.mainloop()

	def generate_time_options(self):
		times = []
		
		for hour in range(5, 24):
			am_pm = 'AM' if hour < 12 else 'PM'
			if hour > 12:
				hour -= 12
			for minute in range(0, 60, 15):
				times.append(f'{hour}:{minute:02} {am_pm}')

		times.append('12:00 AM')

		return times

	def get_rooms_from_website(self):
		print("Fetching info from AVS website...")

		options = Options()
		options.headless = True

		driver = webdriver.Firefox(options=options)
		driver.implicitly_wait(1)

		driver.get(f"https://{self.username}:{self.password}@hosting.med.upenn.edu/avs/index.php?page=addevent")
		# Get all website elements that must be manipulated
		spaces_list = Select(driver.find_element_by_name('avsRoom'))

		# print("Sleep")
		# time.sleep(1)
		# driver.quit()
	
		spaces_options = []
		for space in spaces_list.options:
			spaces_options.append(space.text)


		return spaces_options

		


	def change_event(self, room, title, times, resources, category, comments, reviewed, next_event):
		event_number_modifier = 1
		if not next_event:
			event_number_modifier = -1

		if reviewed.get() == 1:
			if not self.check_reviewed_status(reviewed, category, clicked=True, room_name=room, time_vars=times):
				return

		self.save_current_event_details(room, title, times, resources, category, comments, reviewed)

		self.current_event_displayed += event_number_modifier
		self.clear_resources_and_category(resources, category)
		self.load_info(room, title, times, resources, category, comments, reviewed)


	def load_info(self, room, title, times, resources, category, comments, reviewed):
		room.set(self.events[self.current_event_displayed]['room'])
		title['text'] = self.events[self.current_event_displayed]['title']
		times[0].set(self.events[self.current_event_displayed]['setup']) # Setup start
		times[1].set(self.events[self.current_event_displayed]['start']) # Event start
		times[2].set(self.events[self.current_event_displayed]['end']) # Event end
		times[3].set(self.events[self.current_event_displayed]['takedown']) # Takedown end

		for resource in range(len(resources)):
			if f'{resource:02}' in self.events[self.current_event_displayed]['resources']:
				resources[resource].set(1)

		if self.events[self.current_event_displayed]['category'] != '':
			category.set(self.events[self.current_event_displayed]['category'])

		comments.set(self.events[self.current_event_displayed]['comments'])

		reviewed.set(1 if self.events[self.current_event_displayed]['reviewed'] == "Yes" else 0)
		self.check_reviewed_status(reviewed, category)

		self.prev_event_button['state'] = 'disabled' if self.current_event_displayed == 0 else 'normal'
		self.next_event_button['state'] = 'disabled' if self.current_event_displayed == len(self.events) - 1 else 'normal'
		self.page_indicator['text'] = f'Page: {self.current_event_displayed + 1}/{len(self.events)}'


	def clear_resources_and_category(self, resources, category):
		for resource in resources:
			resource.set(0)

		category.set("")

	def save_current_event_details(self, room, title, times, resources, category, comments, reviewed):
		self.events[self.current_event_displayed]['room'] = room.get()
		self.events[self.current_event_displayed]['title'] = title['text']
		self.events[self.current_event_displayed]['setup'] = times[0].get()
		self.events[self.current_event_displayed]['start'] = times[1].get()
		self.events[self.current_event_displayed]['end'] = times[2].get()
		self.events[self.current_event_displayed]['takedown'] = times[3].get()

		resource_list = []
		for resource in range(len(resources)):
			if resources[resource].get() == 1:
				resource_list.append(f'{resource:02}')

		self.events[self.current_event_displayed]['resources'] = resource_list
		self.events[self.current_event_displayed]['category'] = category.get()
		self.events[self.current_event_displayed]['comments'] = comments.get()
		self.events[self.current_event_displayed]['reviewed'] = "Yes" if reviewed.get() == 1 else "No"

	def save_and_exit_GUI(self, root, room, title, times, resources, category, comments, reviewed):
		self.save_current_event_details(room, title, times, resources, category, comments, reviewed)

		events_list_file = open('Generated Files/Events List.txt','w')
		events_list_file.write(f'Events listed by space for {self.date_year} {self.date_month} {self.date_day} \n')
		events_list_file.write('Note that you MUST check this file over to ensure the information in it is correct before running the auto input program. \n')

		num_reviewed_events = 0
		for event in self.events:
			if event['reviewed'] == 'Yes':
				num_reviewed_events += 1

			resource_string = ""
			for resource in range(len(event['resources'])):
				if resource != len(event['resources']) - 1:
					resource_string += f"{event['resources'][resource]}, "
				else: 
					resource_string += f"{event['resources'][resource]}"

			print(f"	writing event details: {event['title']}")
			events_list_file.write(f"------------------------------------------------------------\n")
			events_list_file.write(f"{event['room'].strip()} \n")		
			events_list_file.write(f"{event['title'].strip()} \n")
			events_list_file.write(f"	Setup Start:	{event['setup']} \n")
			events_list_file.write(f"	Setup End:	{event['start']} \n")
			events_list_file.write(f"	Takedown Start:	{event['end']} \n")
			events_list_file.write(f"	Takedown End:	{event['takedown']} \n")
			events_list_file.write(f"	Event Resources: {resource_string}\n")
			events_list_file.write(f"	Event Category: {event['category']}\n")
			events_list_file.write(f"	Comments: {event['comments']} \n")
			events_list_file.write(f"	Event Reviewed: {event['reviewed']} \n")


		self.all_events_reviewed = True if num_reviewed_events == len(self.events) else False

		events_list_file.close()
		root.destroy()

	def check_reviewed_status(self, reviewed, category, clicked=False, room_name=None, time_vars=None):

		if clicked:
			if room_name.get() not in self.room_options:
				messagebox.showwarning(title='Room Warning', message=f'Invalid room entered. The room must be an EXACT match to one of the rooms in the list (capitalization/punctuation/etc all matters).')
				reviewed.set(0)
				self.reviewed_checkbox['fg'] = 'red'
				return False

			time_labels = ['setup', 'event start', 'event end', 'takedown']
			for idx, time in enumerate(time_vars):
				if time.get().upper() not in self.time_options:
					messagebox.showwarning(title='Time Entry Warning', message=f'Invalid {time_labels[idx]} time entered. Please use the format HH:MM AM/PM.')
					reviewed.set(0)
					self.reviewed_checkbox['fg'] = 'red'
					return False

			if category.get() == '':
				messagebox.showwarning(title='Category Warning', message='A category must be selected before an event can be marked as reviewed.')
				reviewed.set(0)
				self.reviewed_checkbox['fg'] = 'red'
				return False
		
		self.reviewed_checkbox['fg'] = 'green' if reviewed.get() == 1 else 'red'
		return True

	def follow_up_event_checker_GUI(self):
		root = tk.Tk()
		root_width = 800
		root_height = 300

		window_x = root.winfo_screenwidth()//2 - root_width//2
		window_y = root.winfo_screenheight()//2 - root_height//2

		root.geometry(f'{root_width}x{root_height}+{window_x}+{window_y}')

		if self.all_events_reviewed:
			root.title('Run Event Inputter?')
			message = tk.Label(root, text=f'Would you like to automatically input the events for {self.date_month} {self.date_day}, {self.date_year}?')
			yes_button = tk.Button(root, text='Yes', command=lambda: self.close_follow_up(root, button='Yes'))
			no_button = tk.Button(root, text='No', command=lambda: self.close_follow_up(root, button='No'))

			yes_button.place(relwidth=0.2, relheight=0.1, relx=0.2, rely=.55)
			no_button.place(relwidth=0.2, relheight=0.1, relx=0.6, rely=.55)
		else:
			root.title('Must Review Events Before Continueing.')
			message = tk.Label(root, text=f'There are still unreviewed events in the worksheet, so you are unable to run the auto event inputter at this time.')
			exit_button = tk.Button(root, text='Exit', command=lambda: self.close_follow_up(root, button='Exit'))
			exit_button.place(relwidth=0.2, relheight=0.1, relx=0.4, rely=.55)
			

		message.place(relwidth=1, relheight=.1, rely=.25)

		root.mainloop()

	def close_follow_up(self, root, button):
		if button == 'Yes':
			self.run_event_input = True
	
		root.destroy()




			
