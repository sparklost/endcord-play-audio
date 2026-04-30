# endcord-play-audio
An extension for [endcord](https://github.com/sparklost/endcord) discord TUI client, that adds commands for playing audio files in voice call and as voice message.  
Commands:
- `send_audio_file_message [path]` - send audio file as voice message.
- `voice_play_audio_file *[path]` - play audio file while in voice call or stop playback if path is not provided. Multiple sounds can be mixed.
- `voice_play_audio_file_nomix *[path]` - play audio file while in voice call with pausing microphone audio.

## Installing
See [official extensions documentation](https://github.com/sparklost/endcord/blob/main/extensions.md#installing-extensions) for installing instructions.
Available options:
- Git clone into `Extensions` directory located in endcord config directory.
- Run `endcord -i https://github.com/sparklost/endcord-play-audio`
- Or use endcord client-side command `install_extension sparklost/endcord-play-audio`

## Configuration
All extension options are under `[main]` section in endcord config. This extension options are always prepended with `ext_play_audio_`.

### Settings options
- `ext_play_audio_media_path = None`  
    Base path where audio files are searched. THis path is prepended to provided path in commands, only if file at provided path is not existing.


## Disclaimer
> [!WARNING]
> Using third-party client is against Discord's Terms of Service and may cause your account to be banned!  
> **Use endcord and/or this extension at your own risk!**  
> If this extension is modified, it may be used for harmful or unintended purposes.  
> **The developer is not responsible for any misuse or for actions taken by users.**  
