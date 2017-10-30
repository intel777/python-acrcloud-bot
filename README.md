# python-acrcloud-bot
Simple [ACRCloud](http://www.acrcloud.com) bot<br>
You are currently in "VK" branch.<br>
You can choose "Telegram" if that what are you searching for. I have plans to merege two bots in one branch so both bots can be started by one file.

Bot works by simply getting received audio message and send it for recognition to ACRCloud, then if song found, trying to search it in vk.com audio database and send it to user.

## Screenshot
![Screenshot](https://raw.githubusercontent.com/intel777/python-acrcloud-bot/vk/screenshot/chrome_2017-10-30_21-13-37.png)

## Depends on 
* [VK](https://github.com/dimka665/vk) - wrapper to work with vk<br>
Can be easily installed by `pip3 install vk`

## Variables
So, you wanna create you own recognition bot, what you need to change before starting it up?

* **token** - variable with vk.com token which has access to audio.* methods, this needed to send audio with a response.
* **com_token** - variable with vk.com token of group in which you want bot to run.
* **acr_*** - variables with data that you can get by registering at [ACRCloud](http://www.acrcloud.com)(!IMPORTANT!).
* **audio_maxlength** - variable with maximum amount of seconds that will be processed
* **message_err** - variable with text that will be sended if user give not supported type of media or just text.
* **message_err_long** - variable with text that will be sended if user give too long audiofile
* **message_err_notfound** - variable with text that will be sended if audio won't be recognized 
* **message_err_notaudiomessage** - variable with text that will be sended if user give document but not an audiomessage or audio
* **message_err_linknotfound** - variable with text that will be sended if link cannot be found in VK response data

## How to 
To start bot just execute `python3 main.py` if all settings is OK you can test it by sending an audiomessage with some song to your group's messages.

## Licensing
Licensed under WTFPL(Do What The Fuck You Want To Public License)
