import importlib
import logging
import os

from endcord import peripherals

support_media = (
    importlib.util.find_spec("PIL") is not None and
    importlib.util.find_spec("av") is not None and
    importlib.util.find_spec("nacl") is not None
)
assert support_media, "This extension doesn't work with endcord-lite"

EXT_NAME = "Play Audio"
EXT_VERSION = "0.1.1"
EXT_ENDCORD_VERSION = "1.5.0"
EXT_DESCRIPTION = "An extension that adds commands for playing audio files in voice call and as voice message"
EXT_SOURCE = "https://github.com/sparklost/endcord-play-audio"
EXT_COMMAND_ASSIST = (
    ("send_audio_file_message [path] - send audio file as voice message", "send_audio_file_message"),
    ("voice_play_audio_file *[path] - play audio file while in voice call or stop playback", "voice_play_audio_file"),
    ("voice_play_audio_file_nomix *[path] - play audio file while in voice call with pausing microphone audio", "voice_play_audio_file_nomix"),
)
logger = logging.getLogger(__name__)


def convert_to_ogg_opus(input_path, output_path):
    """Using pyav, convert any audio file to ogg opus"""
    import av
    in_container = av.open(input_path)
    in_stream = next(s for s in in_container.streams if s.type == "audio")

    out_container = av.open(output_path, mode="w", format="ogg")
    out_stream = out_container.add_stream("opus", rate=48000)
    out_stream.layout = "stereo"

    resampler = av.audio.resampler.AudioResampler(format="fltp", layout="stereo", rate=48000)
    for frame in in_container.decode(in_stream):
        for new_frame in resampler.resample(frame):
            new_frame.pts = None
            for packet in out_stream.encode(new_frame):
                out_container.mux(packet)

    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    in_container.close()


class Extension:
    """Main extension class"""

    def __init__(self, app):
        self.app = app
        self.base_path = app.config.get("ext_play_audio_media_path", None)
        self.patterns = []


    def on_execute_command(self, command_text, chat_sel, tree_sel):   # noqa
        """Handle commands"""
        if command_text.startswith("send_audio_file_message"):
            path = command_text[24:]
            path = os.path.expanduser(path)
            if self.base_path and not os.path.exists(path):
                path = os.path.join(self.base_path, path)
            if not os.path.exists(path):
                self.app.update_extra_line(f"Specified file not found: {path}")
                return True
            self.app.update_extra_line("Converting audio file")
            save_path = os.path.join(os.path.expanduser(peripherals.temp_path), "send-audio-message.ogg")
            import soundfile
            if "OGG" in soundfile.available_formats() and "OPUS" in soundfile.available_subtypes("OGG"):
                try:
                    data, _ = soundfile.read(path)
                    soundfile.write(save_path, data, 48000, format="OGG", subtype="OPUS")
                except soundfile.LibsndfileError:
                    convert_to_ogg_opus(path, save_path)
            else:
                convert_to_ogg_opus(path, save_path)
            self.app.update_extra_line("Uploading audio file")
            success = self.app.discord.send_voice_message(
                self.app.active_channel["channel_id"],
                save_path,
                reply_id=self.app.replying["id"],
                reply_channel_id=self.app.active_channel["channel_id"],
                reply_guild_id=self.app.active_channel["guild_id"],
                reply_ping=self.app.replying["mention"],
            )
            if success is None:
                self.app.gateway.set_offline()
                self.app.update_extra_line("Network error.")
            if os.path.exists(save_path):
                os.remove(save_path)
            return True

        if command_text.startswith("voice_play_audio_file_nomix"):
            if not (self.app.voice_gateway and self.app.in_call):
                return True
            path = command_text[28:]
            path = os.path.expanduser(path)
            if not path:
                self.app.voice_gateway.stop_file_playback()
                return True
            if self.base_path and not os.path.exists(path):
                path = os.path.join(self.base_path, path)
            if not os.path.exists(path):
                self.app.update_extra_line(f"Specified file not found: {path}")
                return True
            self.app.voice_gateway.play_audio_file(path, mix=False)
            return True

        if command_text.startswith("voice_play_audio_file"):
            if not (self.app.voice_gateway and self.app.in_call):
                return True
            path = command_text[22:]
            path = os.path.expanduser(path)
            if not path:
                self.app.voice_gateway.stop_file_playback()
                return True
            if self.base_path and not os.path.exists(path):
                path = os.path.join(self.base_path, path)
            if not os.path.exists(path):
                self.app.update_extra_line(f"Specified file not found: {path}")
                return True
            self.app.voice_gateway.play_audio_file(path, mix=True)
            return True

        return False
