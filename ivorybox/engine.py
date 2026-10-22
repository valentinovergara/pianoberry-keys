"""Small, explicitly typed FluidSynth binding. Audio never crosses Python."""
import ctypes as C
from ctypes.util import find_library
from .presets import PRESETS, GENERATORS

class Synth:
    def __init__(self, soundfont, device="default", gain=0.5, period=128, preset="piano", audio=True):
        library = find_library("fluidsynth")
        if not library:
            raise RuntimeError("Missing libfluidsynth3; run scripts/install.sh")
        self.lib = C.CDLL(library)
        self.settings = self.synth = self.audio = None
        specs = {
            "new_fluid_settings": (C.c_void_p, []),
            "fluid_settings_setstr": (C.c_int, [C.c_void_p, C.c_char_p, C.c_char_p]),
            "fluid_settings_setnum": (C.c_int, [C.c_void_p, C.c_char_p, C.c_double]),
            "fluid_settings_setint": (C.c_int, [C.c_void_p, C.c_char_p, C.c_int]),
            "new_fluid_synth": (C.c_void_p, [C.c_void_p]),
            "fluid_synth_sfload": (C.c_int, [C.c_void_p, C.c_char_p, C.c_int]),
            "fluid_synth_program_select": (C.c_int, [C.c_void_p, C.c_int, C.c_uint, C.c_uint, C.c_uint]),
            "new_fluid_audio_driver": (C.c_void_p, [C.c_void_p, C.c_void_p]),
            "fluid_synth_set_gen": (C.c_int, [C.c_void_p, C.c_int, C.c_int, C.c_float]),
            "fluid_synth_all_sounds_off": (C.c_int, [C.c_void_p, C.c_int]),
        }
        for name, count in (("noteon", 3), ("noteoff", 2), ("cc", 3), ("pitch_bend", 2), ("channel_pressure", 2)):
            specs["fluid_synth_" + name] = (C.c_int, [C.c_void_p] + [C.c_int] * count)
        for kind in ("audio_driver", "synth", "settings"):
            specs["delete_fluid_" + kind] = (None, [C.c_void_p])
        for name, (result, args) in specs.items():
            fn = getattr(self.lib, name)
            fn.restype, fn.argtypes = result, args
        try:
            self.settings = self.lib.new_fluid_settings()
            if not self.settings:
                raise RuntimeError("Could not create audio settings")
            for key, value in (("audio.driver", "alsa"), ("audio.alsa.device", device)):
                if self.lib.fluid_settings_setstr(self.settings, key.encode(), value.encode()) < 0:
                    raise RuntimeError("Unsupported setting: " + key)
            self.lib.fluid_settings_setnum(self.settings, b"synth.gain", gain)
            self.lib.fluid_settings_setnum(self.settings, b"synth.sample-rate", 48000.0)
            self.lib.fluid_settings_setint(self.settings, b"audio.period-size", period)
            self.lib.fluid_settings_setint(self.settings, b"audio.periods", 3)
            self.lib.fluid_settings_setint(self.settings, b"synth.polyphony", 128)
            self.lib.fluid_settings_setint(self.settings, b"synth.midi-channels", 32)
            self.synth = self.lib.new_fluid_synth(self.settings)
            if not self.synth:
                raise RuntimeError("Could not create synthesizer")
            sfid = self.lib.fluid_synth_sfload(self.synth, str(soundfont).encode(), 0)
            if sfid < 0:
                raise RuntimeError("Could not load SoundFont: " + str(soundfont))
            self.sfid = sfid
            self.layered = False
            self.preset = preset
            self.select_preset(preset)
            if audio:
                self.audio = self.lib.new_fluid_audio_driver(self.settings, self.synth)
                if not self.audio:
                    raise RuntimeError("Could not open ALSA: " + device)
        except BaseException:
            self.close()
            raise

    def apply_effects(self):
        voice = PRESETS[self.preset]
        for name, value in (("synth.reverb.room-size", voice['room']),
                            ("synth.reverb.level", voice['level']),
                            ("synth.chorus.level", .8)):
            self.lib.fluid_settings_setnum(self.settings, name.encode(), value)
        channels = 32 if getattr(self, "layered", False) else 16
        for channel in range(channels):
            self._send("cc", channel, 91, voice['reverb'])
            self._send("cc", channel, 93, voice['chorus'])
            offsets = voice.get('layer', {}).get('generators', {}) if channel >= 16 else voice.get('generators', {})
            for generator in GENERATORS:
                self.lib.fluid_synth_set_gen(self.synth, channel, generator, offsets.get(generator, 0.0))

    def select_preset(self, preset):
        voice = PRESETS[preset]
        self.panic()
        for channel in range(16):
            if self.lib.fluid_synth_program_select(self.synth, channel, self.sfid, 0, voice['program']) < 0:
                raise RuntimeError("SoundFont missing program for " + preset)
        self.layered = 'layer' in voice
        if self.layered:
            for channel in range(16, 32):
                if self.lib.fluid_synth_program_select(self.synth, channel, self.sfid, 0, voice['layer']['program']) < 0:
                    raise RuntimeError("SoundFont missing layer for " + preset)
        self.preset = preset
        self.apply_effects()

    def _send(self, method, *args):
        getattr(self.lib, "fluid_synth_" + method)(self.synth, *args)

    def send(self, method, *args):
        channel = args[0]
        if method == "noteon" and PRESETS[self.preset].get('mono'):
            self.lib.fluid_synth_all_sounds_off(self.synth, channel)
        self._send(method, *args)
        if getattr(self, "layered", False) and channel < 16:
            self._send(method, channel + 16, *args[1:])

    def panic(self):
        channels = 32 if getattr(self, "layered", False) else 16
        for channel in range(channels):
            self._send("cc", channel, 64, 0)
            self._send("cc", channel, 120, 0)
            self._send("cc", channel, 121, 0)
            self._send("pitch_bend", channel, 8192)
        if hasattr(self, "preset"):
            self.apply_effects()

    def close(self):
        for attr, kind in (("audio", "audio_driver"), ("synth", "synth"), ("settings", "settings")):
            value = getattr(self, attr, None)
            if value:
                getattr(self.lib, "delete_fluid_" + kind)(value)
                setattr(self, attr, None)
