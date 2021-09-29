# twitchChatCtrl

Super simple python script and arduino sketch using Twitch chat to control
an arduino.

Using: socket, serial, time, and pygame

pip install socket (communicating with twitch chat)  
pip install pyserial (communication with your arduino)  
pip install pygame (playing sounds)  

The fastLED library is used in the arduino sketch.

The Python scripts checks the Chat for special keywords and if found sends specific data
to the arduino. 
If POKE! is found a mp3-file is played. POKE also has a cool down and can
only control the arduino every 10 seconds.

The arduino controls a relay and rgb led. The script and sketch should be easy enough to change
to suit other "needs".

An oauth token is needed for this script and can be generated at https://twitchapps.com/tmi/ .  
Set the "channel" variable to the channel you want chat messages from, and "username" to your own
username.

If pygame.mixer.music.load crashes the script and the problem is the file libmpg123-0.dll, find the file and copy it to "C:\Windows\system32".