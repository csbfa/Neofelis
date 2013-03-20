
import re
import sys

class ProgressBar:
	"""
	A 3-line progress bar, which looks like::

		 Neofelis Header
		 20% [===========----------------------------------]
		 file

	The progress bar is colored, if the terminal supports color
	output; and adjusts to the width of the terminal.
	"""

	BAR = '%3d%% ${GREEN}[${BOLD}%s%s${NORMAL}${GREEN}]${NORMAL}\n'
	HEADER = '${BOLD}${CYAN}%s${NORMAL}\n\n'
	MESSAGE = "\nNeofelis Pipeline\n\tProcessing: %d queries\n\tElapsed time: %d" \
			  " hours, %d minutes, %d seconds\n\tCompleted %d\n\tFailed %d"

	def __init__(self, term, quantities):
		self.term = term
		if not (self.term.CLEAR_EOL and self.term.UP and self.term.BOL):
			raise ValueError("Terminal cannot support formatted progress. Using simple progress")
		self.width = 75
		self.bar = term.render(self.BAR)
		self.quantities = quantities
		self.header = self.MESSAGE
		self.header = self.term.render(self.HEADER % self.header)
		self.cleared = 1  # : true if we haven't drawn the bar yet.

	def __print__(self, hours, minutes, seconds, completed, failed):
		if self.cleared:
			sys.stdout.write(str(self.term.BOL, 'ascii') + str(self.term.CLEAR_EOL, 'ascii') + self.header % 
							  (self.quantities, hours, minutes, seconds, completed, failed) + str(self.term.CLEAR_EOL, 'ascii'))
			self.cleared = 0
			sys.stdout.write("\n\n")

	def __update__(self, percent, message):
		self.percent = float(percent) * 0.1
		n = int((self.width - 10) * self.percent)
		sys.stdout.write(str(self.term.BOL, 'ascii') + str(self.term.CLEAR_EOL, 'ascii') + message + "\n" + 
						  (self.bar % (100 * self.percent, '=' * n, '-' * (self.width - 10 - n))) + str(self.term.CLEAR_EOL, 'ascii'))
		self.cleared = 0
		sys.stdout.write("\n\n")

	def __clear__(self):
		if not self.cleared:
			sys.stdout.buffer.write(self.term.BOL)
			sys.stdout.buffer.write(self.term.CLEAR_EOL)
			sys.stdout.buffer.write(self.term.UP)
			sys.stdout.buffer.write(self.term.CLEAR_EOL)
			sys.stdout.buffer.write(self.term.UP)
			sys.stdout.buffer.write(self.term.CLEAR_EOL)
			self.cleared = 1

class TerminalController:
	"""
	A class that can be used to portably generate formatted output to
	a terminal.

	`TerminalController` defines a set of instance variables whose
	values are initialized to the control sequence necessary to
	perform a given action.  These can be simply included in normal
	output to the terminal:

		>>> term = TerminalController()
		>>> print 'This is '+term.GREEN+'green'+term.NORMAL

	Alternatively, the `render()` method can used, which replaces
	'${action}' with the string required to perform 'action':

		>>> term = TerminalController()
		>>> print term.render('This is ${GREEN}green${NORMAL}')

	If the terminal doesn't support a given action, then the value of
	the corresponding instance variable will be set to ''.  As a
	result, the above code will still work on terminals that do not
	support color, except that their output will not be colored.
	Also, this means that you can test whether the terminal supports a
	given action by simply testing the truth value of the
	corresponding instance variable:

		>>> term = TerminalController()
		>>> if term.CLEAR_SCREEN:
		...	 print 'This terminal supports clearing the screen.'

	Finally, if the width and height of the terminal are known, then
	they will be stored in the `COLS` and `LINES` attributes.
	"""
	# Cursor movement:
	BOL = ''  # : Move the cursor to the beginning of the line
	UP = ''  # : Move the cursor up one line
	DOWN = ''  # : Move the cursor down one line
	LEFT = ''  # : Move the cursor left one char
	RIGHT = ''  # : Move the cursor right one char

	# Deletion:
	CLEAR_SCREEN = ''  # : Clear the screen and move to home position
	CLEAR_EOL = ''  # : Clear to the end of the line.
	CLEAR_BOL = ''  # : Clear to the beginning of the line.
	CLEAR_EOS = ''  # : Clear to the end of the screen

	# Output modes:
	BOLD = ''  # : Turn on bold mode
	BLINK = ''  # : Turn on blink mode
	DIM = ''  # : Turn on half-bright mode
	REVERSE = ''  # : Turn on reverse-video mode
	NORMAL = ''  # : Turn off all modes

	# Cursor display:
	HIDE_CURSOR = ''  # : Make the cursor invisible
	SHOW_CURSOR = ''  # : Make the cursor visible

	# Terminal size:
	COLS = None  # : Width of the terminal (None for unknown)
	LINES = None  # : Height of the terminal (None for unknown)

	# Foreground colors:
	BLACK = BLUE = GREEN = CYAN = RED = MAGENTA = YELLOW = WHITE = ''

	# Background colors:
	BG_BLACK = BG_BLUE = BG_GREEN = BG_CYAN = ''
	BG_RED = BG_MAGENTA = BG_YELLOW = BG_WHITE = ''

	_STRING_CAPABILITIES = """
	BOL=cr UP=cuu1 DOWN=cud1 LEFT=cub1 RIGHT=cuf1
	CLEAR_SCREEN=clear CLEAR_EOL=el CLEAR_BOL=el1 CLEAR_EOS=ed BOLD=bold
	BLINK=blink DIM=dim REVERSE=rev UNDERLINE=smul NORMAL=sgr0
	HIDE_CURSOR=cinvis SHOW_CURSOR=cnorm""".split()
	_COLORS = """BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE""".split()
	_ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()

	def __init__(self, term_stream=sys.stdout):
		"""
		Create a `TerminalController` and initialize its attributes
		with appropriate values for the current terminal.
		`term_stream` is the stream that will be used for terminal
		output; if this stream is not a tty, then the terminal is
		assumed to be a dumb terminal (i.e., have no capabilities).
		"""

		# Curses isn't available on all platforms
		try: import curses
		except Exception as e: 
			raise e
		
		# If the stream isn't a tty, then assume it has no capabilities.
		if not term_stream.isatty(): 		
				raise Exception

		# Check the terminal type.  If we fail, then assume that the
		# terminal has no capabilities.
		try: curses.setupterm()
		except Exception as e: 
			raise e

		# Look up numeric capabilities.
		self.COLS = curses.tigetnum('cols')
		self.LINES = curses.tigetnum('lines')

		# Look up string capabilities.
		for capability in self._STRING_CAPABILITIES:
			(attrib, cap_name) = capability.split('=')
			setattr(self, attrib, self._tigetstr(cap_name) or '')

		# Colors
		set_fg = self._tigetstr('setf')
		if set_fg:
			for i, color in zip(range(len(self._COLORS)), self._COLORS):
				setattr(self, color, curses.tparm(set_fg, i) or '')
		set_fg_ansi = self._tigetstr('setaf')
		if set_fg_ansi:
			for i, color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
				setattr(self, color, curses.tparm(set_fg_ansi, i) or '')
		set_bg = self._tigetstr('setb')
		if set_bg:
			for i, color in zip(range(len(self._COLORS)), self._COLORS):
				setattr(self, 'BG_' + color, curses.tparm(set_bg, i) or '')
		set_bg_ansi = self._tigetstr('setab')
		if set_bg_ansi:
			for i, color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
				setattr(self, 'BG_' + color, curses.tparm(set_bg_ansi, i) or '')

		"""
		print("BOL ", self.BOL)
		print("UP ", self.UP)
		print("DOWN ", self.DOWN)
		print("LEFT ", self.LEFT)
		print("RIGHT ", self.RIGHT)
		print("CLEAR_SCREEN ", self.CLEAR_SCREEN)
		print("CLEAR_EOL ", self.CLEAR_EOL)
		print("CLEAR_BOL ", self.CLEAR_BOL)
		print("CLEAR_EOS ", self.CLEAR_EOS)
		"""

	def _tigetstr(self, cap_name):

		# String capabilities can include "delays" of the form "$<2>".
		# For any modern terminal, we should be able to just ignore
		# these, so strip them out.

		import curses
		cap = curses.tigetstr(cap_name) or ''
		if isinstance(cap, str):
			regex = re.compile('\$<\d+>[/*]?')
		else:
			regex = re.compile(b'\$<\d+>[/*]?')
		return regex.sub('', cap)

	def render(self, template):
		"""
		Replace each $-substitutions in the given template string with
		the corresponding terminal control string (if it's defined) or
		'' (if it's not).
		"""

		result = re.sub(r"\$\$|\${\w+}", self._render_sub, template)
		return result

	def _render_sub(self, m):
		s = list(m.group())
		s = "".join(s)
		if s == '$$': return s
		else:
			t = getattr(self, "".join(s[2:-1]))
			return str(t, 'ascii')
