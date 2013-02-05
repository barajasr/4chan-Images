#! /usr/bin/python 
# 4chan.images.py
# 
# Author: Richard Barajas
# Date: 05-02-2013
#

import argparse
import os
import re
import sys
import urllib
import subprocess 

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', action='store', default='', dest='directory', help='Directory to save images. Default is thread number')
parser.add_argument('-f', '--filenames', action='store_true', default=False, dest='filenames', help='Save files to filenames seen on posting board if different than source link for image.')
parser.add_argument('-p', '--path', action='store', default='', dest='path', help='Path to save thread to. Default is ./')
parser.add_argument('-q', '--quiet', action='store_true', default=False, dest='quiet', help='Suppress any output, excluding errors.')
parser.add_argument('-l', '--link', action='store', dest='link', required=True, help='Link to thread with desired images.')

def downloadImages(imageList, path, quiet):
    """Downloads images requested from imageList param and saves to files.
       Progress output is default, set quiet flag if not desired.
    """
    number = 0
    for image in imageList:
        number += 1
        filename = os.path.join(path, image[1])
        if os.path.isfile(filename): continue
        if not quiet : 
            sys.stdout.write(str(number) + '. ' + image[1] + '\t\tDownloading...')
            sys.stdout.flush()
        saveFile = open(filename, 'wb')
        saveFile.write(urllib.urlopen('http://' + image[0]).read())
        saveFile.close()
        if not quiet: sys.stdout.write('\tSaved.\n')

def getImageList(threadLink, filenameFlag):
    """ Should return a list of tuples of 4chan images with (sourceLink, filename) format.
    """
    html = urllib.urlopen(threadLink).read()
    if not filenameFlag:
        return re.findall(r'<a \S+ href="//(\S+/src/(\S+))"', html)

    results = re.findall(r'"((?P<subname>[^"]+)[^"]*(?P<format>[a-z.]{4,5}))">(?P=subname)(\(\.\.\.\))?(?P=format)\S+ \S+ href="//(\S+)"', html)
    if results is not None:
        for i in range(0, len(results)):
            results[i] = (results[i][4], results[i][0])
    return results

def main():
    args = vars(parser.parse_args())

    threadLink = args['link']
    threadNumber = re.findall(r'http://boards\S+/res/(\d+\Z)', threadLink)
    if threadNumber is None or threadNumber == []:
        sys.stderr.write('Thread not found, now exiting.\n')
        sys.exit(0)

    quiet = args['quiet']
    if not quiet: print 'Searching for images...'
    threadImages = getImageList(threadLink, args['filenames'])
    if threadImages is None or threadImages == []:
        sys.stderr.write('No images found, now exiting.\n')
        sys.exit(0)
    
    threadFolder = threadNumber[0] if args['directory'] == '' else args['directory']
    fullPath = threadFolder if args['path'] == '' else os.path.join(args['path'], threadFolder)
    subprocess.call(['mkdir', '-p', fullPath])

    if not quiet:
        print str(len(threadImages)), "Images Found."
        print 'Savinag thread to:', fullPath
        print "=="*30 + "\n" + "=="*30
    downloadImages(threadImages, fullPath, quiet)
    if not quiet: print "=="*30 + "\n" + "=="*30

if __name__ == "__main__":
	main()

