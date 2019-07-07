
# Hocuspucus 

Asmall and extensible webserver for controlling key Linux
apps remotely via a browser. This means you can adjust the audio volume,
change playlists, etc. from any browser, including the one in your mobile
phone or tablet.

The UI is style so it can be used from mobile devices.

Besides regualar desktop system, hocuspocus is also suitable for
headless system.

## Supported Plugins

* Quodlibet (audio player) control
* VLC (audio and movie player) control
* Pulse sound system
* Alarm Clock
* Chrome
* Audio and video Playlists
* Webcam monitoring
* Various textual system monitoring tools.
* Userdefined non-interactive shell scripts

The plugins can be  configured by editing `hocuspocus.conf`

## Developement

Code:     http://code.google.com/p/hocuspocus/


Hocuspocus is written in Python 3 and its only hard prerequisite is 
the tornado webserver library. Optionally it can also be controlled 
via mqtt messages in which case you also need paho-mqtt library


Additional dependencies are introduced by the various plugins
and will be reported upon program start.

Invocation: `./hocuspocus.py`

## Screenshots

![main](/Screenshots/main.png?raw=true)
