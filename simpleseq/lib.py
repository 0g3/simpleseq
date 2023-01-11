import numpy as np
import pyaudio
import scipy
from enum import Enum

class NoteNameStyle(Enum):
	UNKNOWN = 0
	INTERNATIONAL = 1
	YAMAHA = 2

# グローバルな設定
SAMPLING_RATE = 48000
NOTE_NAME_STYLE = NoteNameStyle.YAMAHA
BPQN = 480

# 基本的な波形
def wave_sin(note, bpm, bpqn, sampling_rate, gain):
	return gain * np.sin(np.arange(int(note.time(bpm, bpqn)*sampling_rate))*2*np.pi*note.freq/sampling_rate)

def wave_square(note, bpm, bpqn, sampling_rate, gain):
	return gain * scipy.signal.square(np.arange(int(note.time(bpm, bpqn)*sampling_rate))*2*np.pi*note.freq/sampling_rate)

def wave_triangle(note, bpm, bpqn, sampling_rate, gain):
	return gain * scipy.signal.sawtooth(np.arange(int(note.time(bpm, bpqn)*sampling_rate))*2*np.pi*note.freq/sampling_rate, width=0.5)

class Sequencer:
	def __init__(self, tracks, bpm, bpqn=BPQN, sampling_rate=SAMPLING_RATE):
		self.sampling_rate = sampling_rate

		# 各トラックを波形に変換
		waves = []
		for t in tracks:
			waves.append(t.wave(bpm, bpqn, self.sampling_rate))

		# 最大のものに合わせるために0でパディングする
		lens = []
		for w in waves:
			lens.append(len(w))
		max_len = max(lens)
		for i, w in enumerate(waves):
			if len(w) < max_len:
				waves[i] = np.pad(w, (0, max_len-len(w)))

		self.waves = np.vstack(waves)

	def play(self):
		mixed = self.waves.mean(axis=0)
		pa = pyaudio.PyAudio()
		# print("default:", pa.get_default_output_device_info())
		# for index in range(0, pa.get_device_count()):
		# 	info = pa. get_device_info_by_index(index)
		# 	print(info["index"], info["name"])
		stream = pa.open(format=pyaudio.paFloat32, channels=1, rate=self.sampling_rate, frames_per_buffer=1024, output=True)
		stream.write(mixed.astype(np.float32).tobytes())
		stream.close()
		pa.terminate()
		
	
class Track:
	# TODO: gainをちゃんとdBにする
	def __init__(self, source, gain=1):
		self.source = source
		self.gain = gain
		self.notes = []
	
	def add(self, note):
		self.notes.append(note)
	
	def wave(self, bpm, bpqn, sampling_rate):
		wave = np.array([])
		for n in self.notes:
			wave = np.append(wave, self.source(n, bpm, bpqn, sampling_rate, self.gain))
		return wave
		

class Note:
	# num: ノートナンバー
	# value: 音価[tick]
	def __init__(self, name, value):
		npc = NotePitchConverter()
		self.freq = npc.name2freq(name)
		self.value = value
	
	def time(self, bpm, bpqn):
		return self.value/bpqn*60/bpm


class NotePitchConverter:
	def __init__(self, note_name_style=NOTE_NAME_STYLE):
		if note_name_style == NoteNameStyle.INTERNATIONAL:
			self.max_note_name_num = "9"
			self.min_note_name_num = "1"
			self.dlt = 1
		if note_name_style == NoteNameStyle.YAMAHA:
			self.max_note_name_num = "8"
			self.min_note_name_num = "2"
			self.dlt = 2
	
	def name2freq(self, x):
		if x == "R":
			return 0
		num = self.name2num(x)
		return self.num2freq(num)

	def name2num(self, x):
		pos = 0 
		num = 0
		if len(x) < 2 or len(x) > 4:
			raise ValueError("'{}' is invalid note name".format(x))

		# 最初はアルファベットから始まる
		if self._check_alphabet(x[0]):
			raise ValueError("'{}' is invalid note name".format(x))

		if len(x) == 2: # [A-G][0-8]
			if x[1] < '0' or x[1] > self.max_note_name_num:
				raise ValueError("'{}' is invalid note name".format(x))
			pos = self._pos(x[0])
			num = int(x[1])

		if len(x) == 3:
			if x[1] == '#': # [A-G][#][0-8]
				if x[0] in {'E', 'B'} or (x[2] < '0' or x[2] > self.max_note_name_num):
					raise ValueError("'{}' is invalid note name".format(x))
				pos = self._pos(x[:2])
				num = int(x[2])
			if x[1] == '-': # [A-G][-][12]
				if x[2] < '1' or x[2] > self.min_note_name_num:
					raise ValueError("'{}' is invalid note name".format(x))
				pos = self._pos(x[0])
				num = int(x[1:])

		if len(x) == 4: # [A-G][#][-][12]
			if x[1] != '#' or x[2] != '-' or x[0] in {'E', 'B'} or (x[3] < '1' or x[3] > self.min_note_name_num):
				raise ValueError("'{}' is invalid note name".format(x))
			pos = self._pos(x[:2])
			num = int(x[2:])

		return 12*(num+self.dlt) + pos

	def num2freq(self, x):
		return 440.0*2**((x-69)/12)

	def _check_alphabet(self, x):
		return x[0] < 'A' or x[0] > 'G'

	def _pos(self, x):
		if len(x) == 1:
			if x == "C": return 0
			if x == "D": return 2
			if x == "E": return 4
			if x == "F": return 5
			if x == "G": return 7
			if x == "A": return 9
			if x == "B": return 11
		if len(x) == 2:
			if x == "C#": return 1
			if x == "D#": return 3
			if x == "F#": return 6
			if x == "G#": return 8
			if x == "A#": return 10
		return 0
