#! /usr/bin/env python 
# 4chan.images.py
#
# Author: Richard Barajas
# Date: 08-02-2013

import argparse
from BeautifulSoup import BeautifulSoup
import os
import re
import sys
import urllib2
import subprocess 

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory',
                    action='store',
                    default='', 
                    dest='directory',
                    help='Directory to save images. Default is thread number')
parser.add_argument('-f', '--filenames', 
                    action='store_true',
                    default=False, 
                    dest='filenames',
                    help='Save files to filenames seen on posting board if different than source link for image.')
parser.add_argument('-p', '--path', 
                    action='store',
                    default='', 
                    dest='path',
                    help='Path to save thread to. Default is ./')
parser.add_argument('-q', '--quiet', 
                    action='store_true',
                    default=False,
                    dest='quiet',
                    help='Suppress any output, excluding errors.')
parser.add_argument('-l', '--link',
                    action='store',
                    dest='link',
                    required=True,
                    help='Link to thread with desired images.')

def downloadImages(imageList, path, quiet):
    """Downloads images requested from imageList param and saves to files.
       Progress output is default, set quiet flag if not desired.
    """
    number = 0
    for image in imageList:
        number += 1
        fullFilename = os.path.join(path, image[1])
        if os.path.isfile(fullFilename): continue
        if not quiet: frontProgressText(image[1], number)
        imageToFile(fullFilename, image[0])
        if not quiet: sys.stdout.write('\tSaved.\n')

def frontProgressText(filename, imageNumber):
    """Function is solely a slave call from downloadImages.
       Prints the image number, filename, and Downloading text portions
       of the progress.
    """
    sys.stdout.write(str(imageNumber) + '. ' + filename)
    lengthOfText = len(filename) + len(str(imageNumber)) + 2
    if lengthOfText < 45:
        sys.stdout.write(' '*(45-lengthOfText) + 'Downloading...')
    else:
        sys.stdout.write('\n' + ' '*45 + 'Downloading...')
    sys.stdout.flush()

def getImageList(threadLink, filenameFlag):
    """ Should return a list of tuples of 4chan images with (sourceLink, filename)
        format.
    """

    # Attempt to get html for thread
    try:
        html = urllib2.urlopen(threadLink).read()
    except (urllib2.HTTPError, urllib2.URLError), e:
        sys.stderr.write('\nError while making request for ' + threadLink + '\n')
        if isinstance(e, urllib2.HTTPError):
            sys.stderr.write(str(e.code) + '\n' + e.reason + '\n')
        else:
            sys.stderr.write(e.reason + '\n')
        sys.exit(1)

    # Parse for images
    soup = BeautifulSoup(html)
    # Template for findAll
    # <div class="fileText" id="fT6816862">File: <a href="//i.4cdn.org/sci/1413436856754.jpg" target="_blank">black science man.jpg</a> (81 KB, 960x502)</div>
    data = soup.findAll('div', {'class' : 'fileText'})
    data = [post.find('a') for post in data]

    return [('http:' + anchor['href'], anchor.text) for anchor in data]

def imageToFile(filename, link):
    """Attempt to download image and store to file.
    """
    try:
        image = urllib2.urlopen(link).read()
        saveFile = open(filename, 'wb')
        saveFile.write(image)
        saveFile.close()
    except (urllib2.HTTPError, urllib2.URLError), e:
        sys.stderr.write('\nError while making request for ' + link + '\n')
        if isinstance(e, urllib2.HTTPError):
            sys.stderr.write(str(e.code) + '\n' + e.reason + '\n')
        else:
            sys.stderr.write(e.reason + '\n')
        sys.exit(1)
    except IOError:
        # remove file if possible, allowing chance for clean download later
        sys.stderr.write('\nFailed writing to file, ' + filename + '\n')
        saveFile.close()
        os.remove(filename)
        sys.exit(2)

def main():
    args = vars(parser.parse_args())

    threadLink = args['link']
    threadNumber = re.findall(r'http://boards\S+/thread/(\d+\Z)', threadLink)
    if threadNumber is None or threadNumber == []:
        sys.stderr.write('Thread not found, now exiting.\n')
        sys.exit(0)

    quiet = args['quiet']
    if not quiet: print 'Searching for images...'
    threadImages = getImageList(threadLink, args['filenames'])
    for i in threadImages:
        print i
    if threadImages is None or threadImages == []:
        sys.stderr.write('No images found, now exiting.\n')
        sys.exit(0)

    threadFolder = threadNumber[0] if args['directory'] == '' else args['directory']
    fullPath = threadFolder if args['path'] == '' else os.path.join(args['path'], threadFolder)
    if subprocess.call(['mkdir', '-p', fullPath]) != 0:
        sys.stderr.write('Failed to make target directory ' + fullPath + '\n')
        sys.exit(3)

    if not quiet:
        print str(len(threadImages)), "Images Found."
        print 'Saving thread to:', fullPath
        print "=="*36 + "\n" + "=="*36
    downloadImages(threadImages, fullPath, quiet)
    if not quiet: print "=="*30 + "\n" + "=="*30

if __name__ == "__main__":
    main()

