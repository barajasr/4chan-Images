#! /usr/bin/env python 
# 4chan.images.py
#
# Author: Richard Barajas
# Date: 16-10-2014

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
parser.add_argument('-n', '--nofolder',
                    action='store_true',
                    dest='nofolder',
                    help='Do not create a folder to group media resources in.')
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
parser.add_argument('url',
                    help='Url to thread with desired images.')

def downloadImages(imageList, path, quiet):
    """Downloads images requested from imageList param and saves to files.
       Progress output is default, set quiet flag if not desired.
    """

    number = 0
    for image in imageList:
        number += 1
        fullFilename = os.path.join(path, image[1])
        downloaded = os.path.isfile(fullFilename)
        if not quiet: frontProgressText(image[1], number)
        imageToFile(fullFilename, image[0])
        if not quiet: 
            message = '\tSaved.\n' if not downloaded else '\tAlready Exists.\n'
            sys.stdout.write(message)

def frontProgressText(filename, imageNumber):
    """Function is solely a slave call from downloadImages.
       Prints the image number, filename, and Downloading text portions
       of the progress.
    """

    sys.stdout.write(str(imageNumber) + '. ' + filename)
    lengthOfText = len(filename) + len(str(imageNumber)) + 2
    if lengthOfText < 45:
        sys.stdout.write(' '*(45-lengthOfText) + 'Progress...')
    else:
        sys.stdout.write('\n' + ' '*45 + 'Progress...')
    sys.stdout.flush()

def getImageList(threadUrl):
    """ Should return a list of tuples of 4chan images with (sourceUrl, filename)
        format.
    """

    try:
        html = urllib2.urlopen(threadUrl).read()
    except (urllib2.HTTPError, urllib2.URLError), e:
        sys.stderr.write('\nError while making request for ' + threadUrl + '\n')
        if isinstance(e, urllib2.HTTPError):
            sys.stderr.write(str(e.code) + '\n' + e.reason + '\n')
        else:
            sys.stderr.write(e.reason + '\n')
        sys.exit(1)

    soup = BeautifulSoup(html)
    # Expected entry example for findAll result
    # <div class="fileText" id="fT6816862">File: <a href="//i.4cdn.org/sci/1413436856754.jpg" target="_blank">black science man.jpg</a> (81 KB, 960x502)</div>
    data = soup.findAll('div', {'class' : 'fileText'})
    data = [post.find('a') for post in data]

    tuples = []
    for anchor in data:
        filename = anchor.text
        if anchor.has_key('title'): # Filename has '(...)' pattern in it
            filename = anchor['title']
        tuples.append(('http:'+ anchor['href'], filename))
    return tuples

def imageToFile(filename, url):
    """Attempt to download image and store to file.
    """

    try:
        image = urllib2.urlopen(url).read()
        saveFile = open(filename, 'wb')
        saveFile.write(image)
        saveFile.close()
    except (urllib2.HTTPError, urllib2.URLError), e:
        sys.stderr.write('\nError while making request for ' + url + '\n')
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

    threadUrl = args['url']
    threadNumber = re.findall(r'http://boards\S+/thread/(\d+\Z)', threadUrl)
    if threadNumber is None or threadNumber == []:
        sys.stderr.write('Thread not found, now exiting.\n')
        sys.exit(0)

    quiet = args['quiet']
    if not quiet: print 'Searching for images...',
    threadImages = getImageList(threadUrl)
    if threadImages is None or threadImages == []:
        sys.stderr.write('No images found, now exiting.\n')
        sys.exit(0)

    fullPath = args['path']
    if fullPath != '' and  not os.path.isdir(fullPath):
            sys.stderr.write( "'"+ fullPath + "' path does not exist or invalid\n")
            sys.exit(3)
    if not args['nofolder']:
        threadFolder = threadNumber[0] if args['directory'] == '' else args['directory']
        fullPath = threadFolder if fullPath == '' else os.path.join(fullPath, threadFolder)
        if subprocess.call(['mkdir', '-p', fullPath]) != 0:
            sys.stderr.write('Failed to make target directory ' + fullPath + '\n')
            sys.exit(4)

    width = 40
    if not quiet:
        print str(len(threadImages)), "Images Found."
        print 'Saving thread to:', fullPath
        print "=="*width + "\n" + "=="*width
    downloadImages(threadImages, fullPath, quiet)
    if not quiet: print "=="*width + "\n" + "=="*width

if __name__ == "__main__":
    main()

