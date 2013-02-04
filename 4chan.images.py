#! /usr/bin/python 
# 4chan.images.py
# 
# Author: Richard Barajas
# Date: 02-02-2013
#

import argparse
import os
import re
import sys
import urllib
import subprocess 

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', action='store', default='', dest='directory', help='Directory/path to save images. Default is ./')
parser.add_argument('-f', '--filenames', action='store_true', default=False, dest='filenames', help='Save files to filenames seen on posting board if different than source link for image.')
parser.add_argument('-q', '--quiet', action='store_true', default=False, dest='quiet', help='Suppress any output, excluding errors.')
parser.add_argument('-l', '--link', action='store', dest='link', required=True, help='Link to thread with desired images.')

def downloadImages(imageList, directory, quiet):
    """Downloads images requested from imageList param and saves to files.
       Progress output is default, set quiet flag if not desired.
    """
    number = 0
    for image in imageList:
        number += 1
        filename = os.path.join(directory, image[1])
        if os.path.isfile(filename): continue
        if not quiet : 
            sys.stdout.write(str(number) + '. ' + image[1] + '\t\tDownloading...')
            sys.stdout.flush()
        saveFile = open(filename, 'wb')
        saveFile.write(urllib.urlopen('http://' + image[0]).read())
        saveFile.close()
        if not quiet: sys.stdout.write('\tSaved.\n')

def getImageList(html, filenameFlag):
    """ Should return a list of tuples of 4chan images with (sourceLink, filename) format.
    """
    if not filenameFlag:
        return re.findall(r'<a \S+ href="//(\S+/src/(\S+))"', html)

    results = re.findall(r'"((?P<subname>[^"]+)[^"]*(?P<format>\.[a-z]{3,4}))">(?P=subname)(\(\.\.\.\))?(?P=format)\S+ \S+ href="//(\S+)"', html)
    if results is not None:
        for i in range(0, len(results)):
            results[i] = (results[i][4], results[i][0])
    return results

def main():
    args = vars(parser.parse_args())

    threadLink = args['link']
    threadNumber = re.findall(r'org/\S+/res/(\d+\Z)', threadLink)
    if threadNumber is None or threadNumber == []:
        sys.stderr.write('Thread not found, now exiting.\n')
        sys.exit(0)

    quiet = args['quiet']
    if not quiet:
        print "Thread to Download: " + threadLink
        print 'Searching for images...'
    threadBody = urllib.urlopen(threadLink).read()
    threadImages = getImageList(threadBody, args['filenames'])
    if threadImages is None or threadImages == []:
        sys.stderr.write('No images found, now exiting.\n')
        sys.exit(0)
    
    if not quiet: 
        print str(len(threadImages)) + " Images Found."
        print "=="*30 + "\n" + "=="*30

    targetDir = threadNumber[0] if args['directory'] == '' else os.path.join(args['directory'], threadNumber[0])
    mkdir(targetDir)
    downloadImages(threadImages, targetDir, quiet)
    if not quiet: print "=="*30 + "\n" + "=="*30

def mkdir(targetDir):
    subprocess.call(['mkdir', '-p', targetDir])

if __name__ == "__main__":
	main()

