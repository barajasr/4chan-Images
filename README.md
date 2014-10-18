4chan-Images
============

Download 4chan media resources from a given thread.

usage: 4chan.images.py [-h] [-d DIRECTORY] [-n] [-p PATH] [-q] url

positional arguments:
  url                   Url to thread with desired images.

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory to save images. Default is thread number
  -n, --nofolder        Do not create a folder to group media resources in.
  -p PATH, --path PATH  Path to save thread to. Default is ./
  -q, --quiet           Suppress any output, excluding errors.
