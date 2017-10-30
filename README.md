# python-acrcloud-bot
Simple [ACRCloud](http://www.acrcloud.com) bot<br>
You are currently in "Telegram" branch.<br>
You can choose "VK" if that what are you searching for. I have plans to merege two bots in one branch so both bots can be started by one file.

## Screenshot
![Screenshot](https://raw.githubusercontent.com/intel777/python-acrcloud-bot/telegram/screenshots/Telegram_2017-10-30_21-28-27.png)

## Depends on 
* [VK](https://github.com/dimka665/vk) - wrapper to work with vk<br>
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
Can be easily installed by `pip3 install vk python-telegram-bot`

## Variables
So, you wanna create you own recognition bot, what you need to change before starting it up?

* **tg_token** - telegram token that [Botfather](https://t.me/botfather) had gived to you.
* **vk_token** - variable with vk.com token which has access to audio.* methods, this needed to send audio with a response.
* **acr_*** - variables with data that you can get by registering at [ACRCloud](http://www.acrcloud.com)(!IMPORTANT!).

Well, yeah, there is less variables that in VK version, but all can be changed right in code, may be someday I will make variable for every text, but for now it like it is.

## How to 
To start bot just execute `python3 main.py` if all settings is OK you can test it by sending an audiomessage with some song to your bot's messages.

## Licensing
Licensed under WTFPL(Do What The Fuck You Want To Public License)
