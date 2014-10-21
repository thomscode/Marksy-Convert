import sys
import os
import subprocess
import sublime
import sublime_plugin

import threading

import json

global is_py3
is_py3 = sys.version_info >= (3, 0)


if is_py3:
	from urllib.request import Request, urlopen
	from urllib.error import URLError
else:
	from urllib2 import Request, urlopen, URLError

global input_formats
global output_formats
global ext

input_formats = ['markdown', 'github', 'rst', 'textile', 'html', 'mediawiki', 'jira']
output_formats = ['markdown', 'rst', 'textile', 'html', 'mediawiki', 'jira', 'googlecode', 'jspwiki', 'moinmoin', 'trac']
ext = {'markdown': 'md','rst': 'rst','textile': 'textile','html': 'html','mediawiki': 'mwiki','jira': 'jira','googlecode': 'google','jspwiki': 'jwiki','moinmoin': 'moin','trac': 'trac'}

def display_message(message):
	sublime.status_message(message)
	sublime.active_window().run_command('sub_notify', {'title': "Marksy",'msg': message,'sound': False})

################################################################################
# Get the IO formats
################################################################################
class MarksyPromptCommand(sublime_plugin.WindowCommand):
	i_format = None
	o_format = None

	def run(self, o_format):
		self.o_format = o_format

		inputs = ['Markdown','Github Flavored Markdown (GFM)','reStructuredText','Textile','HTML','Mediawiki','Jira (Confluence)']
		input_list = []
		text = 'Convert from: {0}'
		for i in inputs:
			input_list.append(text.format(i))

		index = self.get_syntax(self.window.active_view())

		if int(sublime.version()) >= 3000:
			self.window.show_quick_panel(input_list, self.on_done, selected_index=index)
		else:
			self.window.show_quick_panel(input_list, self.on_done)


	def on_done(self, i):
		if i == -1:
			print('Canceled')
			return

		self.i_format = input_formats[i]

		self.window.active_view().run_command('marksy', {
			'i_format':self.i_format,
			'o_format':self.o_format
		})

	def get_syntax(self, view):
		syntax = {
			'markdown':['markdown','mdown','mkdn','md','mkd','mdwn','mdtxt','mdtext','text'],
			'github':['github','gfm'],
			'rst': ['rst'],
			'textile': ['textile'],
			'html': ['html','htm'],
			'mediawiki': ['mwiki','wiki','mediawiki'],
			'jira': ['jira','confluence'],
		}
		file_name = view.file_name()
		if file_name == None:
			return 0

		ext = file_name.split('.')[-1]
		for s in syntax:
			if ext in s:
				return input_formats.index(s)

		return 0


################################################################################
# Begin the conversion
################################################################################
class MarksyCommand(sublime_plugin.TextCommand):
	""" Use Marksy API to convert between various markup languages """

	def run(self, edit, i_format, o_format):
		settings = sublime.load_settings("Marksy.sublime-settings")
		filename = self.get_file_name(self.view)
		title = '{0}.{1}'.format(filename, ext[o_format])
		contents = self.view.substr(sublime.Region(0, self.view.size()))

		# Run the following in a new thread
		t1 = MarksyApiCall({'input': i_format, 'output': o_format}, contents)
		t1.start()

		# Handle the thread
		self.launch(edit, t1, title)

	def get_file_name(self, view):
		file_name = view.file_name()
		if file_name == None:
			return 'Untitled'
		else:
			split_char = '/' if sublime.platform() != 'windows' else '\\'
			return file_name.split(split_char)[-1].split('.')[0]

	def launch(self, edit, thread, title, i=0, direction=1):
		if not thread.is_alive():
			self.view.erase_status('marksy')
			if thread.result == False:
				display_message("There was an error converting the text.")
			else:
				self.view.run_command('marksy_launch', {'title': title, 'text':thread.result})

		else:
			before = i % 8
			after = (7) - before
			if not after:
				direction = -1
			if not before:
				direction = 1
			i += direction

			self.view.set_status("marksy", "Marksy Convert [%s=%s]" % (' ' * before, ' ' * after))
			sublime.set_timeout(lambda: self.launch(edit, thread, title, i, direction), 100)


################################################################################
# Load the result in a new window
################################################################################
class MarksyLaunchCommand(sublime_plugin.TextCommand):
	""" Launch the Marksy converted text in a new window """
	def run(self, edit, title, text):
		new_view = self.view.window().new_file()
		new_view.set_name(title)
		new_view.insert(edit, 0, text)
		display_message('Text has been converted successfully.')

################################################################################
# Talk to the API to convert the text
################################################################################
class MarksyApiCall(threading.Thread):
	def __init__(self, formats, contents):
		self.error = False
		self.result = None
		self.input = formats['input']
		self.output = formats['output']
		self.text = contents
		threading.Thread.__init__(self)

	def run(self):
		if self.input not in input_formats:
			display_message('Invalid Input format')
			return
		elif self.output not in output_formats:
			display_message('Invalid Output format')
			return

		url = 'http://marksy.arc90.com/convert'
		payload = {
			'input': self.input,
			'output': self.output,
			'text': self.text
		}

		# Convert to json
		data = json.dumps(payload)

		# Setup HTTP headers
		headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		}

		# Encode the data
		data = data.encode('utf-8')

		# Create and send the request
		r = Request(url, data, headers)
		try:
			response = urlopen(r)

			if is_py3:
				self.result = json.loads(response.read().decode('utf-8'))
			else:
				self.result = json.loads(response.read())

			self.result = self.result['payload']
			return
		except URLError as e:
			self.result = False
			self.error = e.reason
			return
		except:
			self.result = False
			self.error = True
			raise
