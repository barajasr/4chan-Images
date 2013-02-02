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
parser.add_argument('-d', '--directory', action='store', default='./', dest='directory', help='Directory/path to save images. Default is ./')
parser.add_argument('-f', '--filenames', action='store_true', default=False, dest='filenames', help='Save files to filenames seen on posting board if changed; files shown with (...) is overlooked.')
parser.add_argument('-q', '--quiet', action='store_true', default=False, dest='quiet', help='Suppress any output, excluding errors.')
parser.add_argument('-l', '--link', action='store', dest='link', required=True, help='Link to thread with desired images.')

def downloadImages(imageList, directory, quiet):
    for image in imageList:
        if not quiet : print image[0], '\tDownloading...'   # Would prefer suppressing newline, but blocks
        saveFile = open(directory + '/' + image[0], 'wb')
        saveFile.write(urllib.urlopen('http://' + image[1]).read())
        saveFile.close()
        if not quiet: print '\t\t\tSaved.'

def getImageList(html, filenameFlag):
    """ Should return a list of tuples of 4chan images with (filename, Source) format.
    """
    if filenameFlag:
        return re.findall(r'title="(?P<title>[\S ]+)">(?P=title)\S+ \S+ href="//(\S+)"', html)

    results = re.findall(r'<a \S+ href="//(\S+/src/(\S+))"', html)
    if results is not None:
        for i in range(0, len(results)):
            results[i] = (results[i][1], results[i][0])
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

    targetDir =  './' + threadNumber[0] if args['directory'] == './' else os.path.join(args['directory'], threadNumber[0])
    mkdir(targetDir)
    downloadImages(threadImages, targetDir, quiet)
    if not quiet: print "=="*30 + "\n" + "=="*30

def mkdir(targetDir):
    if not os.path.isdir(targetDir):
        subprocess.call(['mkdir', '-p', targetDir])

if __name__ == "__main__":
	main()

