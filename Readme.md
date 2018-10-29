#YFDownload
###Yahoo Groups Files Downloader

I needed to download all the files in my yahoo group. There was a bunch of files distributed in several
directories and subdirectories. https://github.com/csaftoiu/yahoo-groups-backup wasn't working
for me and I just wanted the files mirrored in my filesystem so I made this script
which was inspired by it.

####How to use:

Create a virtual environment:

`python3 -m venv ~/pyton3-yfdownload` 

Install the dependencies:

`pip install -r requirements.txt`

Make your script executable:

`chmod +x ./yfdownload.sh`

For a public group:

`./yfdownload.py nameofthegroup`

Will create a directory with the group's name and replicate the file tree of the group locally

If the group is private create a `file.yaml` with:

```$xslt
login: youryahoologin
password: youryahoopassword
```

and invoke as:

`./yfdownload.py -c file.yaml nameofthegroup`


####DISCLAIMER:

This script was quickly put together by a rusty python developer, error management and command line
parsing is not very well thought of, use at your own risk.