# auto-yt-dl
Automate all the things.

## Description
Because I am lazy.

 > Because... whatever -- Reika

This script is, in fact, full of bugs and stupidly ugly code, even it is written in python.

I don't border to maintain this. Unless youtube have v4 api or youtube-dl updated and broke backward compatibility.

## Usage
Install python3, virtualenv.

`$ virtualenv env`

`$ source env/bin/activate`

`$ pip install -r requirement.txt`

`$ ./start.sh`

Make a systemd unit or cron script for invoking start.sh. It will auto source environment, run script and update youtube-dl.

## License
MIT
