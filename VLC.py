from __future__ import print_function
import vlc
from math import floor
from time import sleep

class VLC:
	def __init__(self):
		self.instance = vlc.Instance()
		self.queue = []
		self.player = None
		self.path = None
		self.file = None
		self.default_subs = None
		self.default_audio = None
		self.prev_subs = []
		self.prev_audio = []
		
	def play(self, path, *_):
		self.stop()
		if self.player == None:
			self.player = self.instance.media_player_new()
		
		self.player.set_media(self.instance.media_new(path))
		self.player.play()
		self.player.set_pause(True)

		self.path = path
		self.file = path[path.rfind('/')+1:]

		spus = []
		while spus == []:
			sleep(0.25)
			spus = self.player.video_get_spu_description()
		if self.default_subs is None or self.prev_subs != spus:
			for (k, v) in spus:
				if "english" in v.decode('utf-8').lower() and "songs" not in v.decode('utf-8').lower():
					self.default_subs = int(k)
			if self.default_subs is not None:
				self.player.video_set_spu(self.default_subs)
		self.prev_subs = spus
		
		audios = []
		while audios == []:
			sleep(0.25)
			audios = self.player.audio_get_track_description()
		if self.default_audio is None or self.prev_audio != audios:
			for (k, v) in audios:
				if "japanese" in v.decode('utf-8').lower():
					self.default_audio = int(k)
			if self.default_audio is not None:
				self.player.audio_set_track(self.default_audio)
		self.prev_audio = audios

		print(self.default_audio, self.default_subs, audios, spus)
		self.player.set_pause(False)

	def pause(self, *_):
		if self.player:
			self.player.set_pause(True)

	def resume(self, *_):
		if self.player:
			self.player.set_pause(False)
		
	def stop(self, *_):
		if self.player:
			self.player.stop()

	def seek(self, pos, *_):
		self.player.set_time(min(floor(float(pos))*1000, self.get_length() - 3000))

	def get_playing(self, *_):
		return self.player.is_playing() if self.player else None

	def get_title(self, *_):
		return self.file

	def get_length(self, *_):
		return self.player.get_length() if self.player else 0

	def get_time(self, *_):
		return self.player.get_time() if self.player else 0

	def seek_by(self, seconds, *_):
		self.player.set_time(max(0, min(self.get_time() + floor(float(seconds))*1000, self.get_length() - 3000)))

	def get_tracks(self, *_):
		if self.path is None:
			return {"subs": [], "audio": []}

		return {
			"subs": self.player.video_get_spu_description(),
			"audio": self.player.audio_get_track_description()
		}

	def set_tracks(self, subs, audio, *_):
		if self.player is None:
			return

		if self.default_subs is None:
			self.default_subs = self.player.video_get_spu()
		if self.default_audio is None:
			self.default_audio = self.player.audio_get_track()
		
		print("spu:", self.player.video_set_spu(self.default_subs if subs == "default" else int(subs)))
		print("audio:", self.player.audio_set_track(self.default_audio if audio == "default" else int(audio)))
