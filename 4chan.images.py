#! /usr/bin/env python 
# 4chan.images.py
#
# Author: Richard Barajas
# Date: 17-10-2014

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
                    default='./', 
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
    """ Downloads images requested from imageList param and saves to files.
        Progress output is default, set quiet flag if not desired.
    """

    width = 40
    if not quiet:
        print str(len(imageList)), 'Images Found.'
        print 'Saving thread to:', path
        print '=='*width + '\n' + '=='*width

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

    if not quiet: print '=='*width + '\n' + '=='*width

def frontProgressText(filename, imageNumber):
    """ Function is solely a slave call from downloadImages.
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
    """ Should return a list of tuples of 4chan images with
        (sourceUrl, filename) format.
        Fail otherwise.
    """

    soup = BeautifulSoup(getThreadSource(threadUrl))
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

    if tuples is None or tuples == []:
        sys.stderr.write('No images found, now exiting.\n')
        sys.exit(0)

    return tuples

def getThreadNumber(url):
    """ Returns thread number if url is valid.
    """

    return validateThreadUrl(url)

def getThreadSource(url):
    """ Return html of requested thread.
        Fail otherwise.
    """

    try:
        return urllib2.urlopen(url).read()
    except (urllib2.HTTPError, urllib2.URLError), e:
        sys.stderr.write('\nError while making request for ' + threadUrl + '\n')
        if isinstance(e, urllib2.HTTPError):
            sys.stderr.write(str(e.code) + '\n' + e.reason + '\n')
        else:
            sys.stderr.write(e.reason + '\n')
        sys.exit(1)

def imageToFile(filename, url):
    """ Attempt to download image and store to file.
        Fail otherwise.
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
    threadNumber = getThreadNumber(threadUrl)
    fullPath = preparePath(args, threadNumber)

    quiet = args['quiet']
    if not quiet: print 'Searching for images...',
    downloadImages(getImageList(threadUrl), fullPath, quiet)

def preparePath(args, threadNumber):
    """ Return apporpiate path as determined by args.
        Fail if path invalid of failure to create directory.
    """

    fullPath = args['path']
    if fullPath != './' and  not os.path.isdir(fullPath):
            sys.stderr.write( "'"+ fullPath + "' path does not exist or invalid\n")
            sys.exit(3)
    if not args['nofolder']:
        threadFolder = threadNumber[0] if args['directory'] == '' else args['directory']
        fullPath = threadFolder if fullPath == '' else os.path.join(fullPath, threadFolder)
        if subprocess.call(['mkdir', '-p', fullPath]) != 0:
            sys.stderr.write('Failed to make target directory ' + fullPath + '\n')
            sys.exit(4)
    return fullPath


def validateThreadUrl(url):
    """ Checks url pattern; return thread number if possible.
        Fail otherwise.
    """

    threadNumber = re.findall(r'http://boards\S+/thread/(\d+\Z)', url)
    if threadNumber is None or threadNumber == []:
        sys.stderr.write('Thread not found, now exiting.\n')
        sys.exit(0)

    return threadNumber

if __name__ == '__main__':
    main()

