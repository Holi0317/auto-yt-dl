# auto-yt-dl
Automate all the things.

## Description
Because I am lazy.

 > Because... whatever -- Reika

This script is, in fact, full of bugs and stupidly ugly code, even it is written in python.

I don't border to maintain this. Unless youtube have v4 api or youtube-dl updated and broke backward compatibility.

## Usage
Install python3, virtualenv to your system first.

Then create new project from [Google developer console](console.developers.google.com). Enable Youtube API and create a Credential from `Credentials` page. A `OAuth2 client ID` is required.

Then select `web application` as application type. Fill in `http://localhost:8080/` as `Authorized redirect URIs`.

Download the JSON credential file and save as `client_id.json` in this directory.

Then run the following commands 

```bash
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirement.txt
$ deactivate
$ ./start.sh
```

Make a systemd unit or cron script for invoking start.sh. It will auto source environment, run script and update youtube-dl.

## License
MIT
