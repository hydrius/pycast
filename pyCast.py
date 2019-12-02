#!/usr/bin/env python


#
#
# Modfied version of but for
#
#



from __future__ import print_function
import os, sys, getopt, mimetypes, datetime, urllib
import  xml.etree.cElementTree as ET
import urllib.parse

from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
from mutagen.mp3 import MP3



#replace with ladysue when serving 
dir = "/home/aquitard/Projects/pycast/test"

attrKeys = { 'kMDItemAlbum': 'Album'}

def getMeta( fileName ):
    print(fileName)
    audio = MP3(fileName)
    fileDets = {}
    if os.path.exists( fileName ):
        mp3 = MP3File(fileName)
        tags = mp3.get_tags()["ID3TagV1"]
        print(tags)

        for value in attrKeys.values():
            print(tags[value.lower()])
            fileDets[value] = tags[value.lower()]

        fileDets["Title"] = tags["song"] 
        fileDets["Summary"] = tags["song"] 
        fileDets["Summary"] = tags["song"] 
        fileDets["Authors"] = tags["artist"] 
        fileDets["Duration"] = audio.info.length
        fileDets["Size"] = audio.info.length
        fileDets["PubDate"] = None



    return fileDets

def genFeed( srcDir ):
    for fileFound in sorted(os.listdir( srcDir )):
        if fileFound.startswith( '.' ):
            continue
        yield fileFound

import urllib.parse
def main( argv = None ):
    if argv is None:
        argv = sys.argv
        
    optList, optArgs = getopt.getopt( argv[ 1: ], "w:d:h", [ '--web', '--dir', '--help' ] )
    webBase = None
    dirBase = None
    for clList, clArgs in optList:
        if clList in [ '-w', '--web' ]:
            webBase = clArgs
        elif clList in [ '-d', '--dir' ]:
            dirBase = clArgs

    if dirBase is None:
        print( 'Base Dir Not Specified!' )
        dirBase = dir
        return 1
                    
    for srcDir in os.listdir( dirBase ):
        if os.path.isfile( os.path.join( dirBase, srcDir ) ):
            continue
                        
        rssRoot = ET.Element( "rss" )
        rssChann = ET.SubElement( rssRoot, 'channel' )
        rssChann.attrib[ 'xmlns:itunes' ] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        rssChann.attrib[ 'version' ] = '2.0'
        
        castTitle = ET.SubElement( rssChann, 'title' )
        castLink = ET.SubElement( rssChann, 'link' )
        castDesc = ET.SubElement( rssChann, 'description' )
        castiTunesDesc = ET.SubElement( rssChann, 'itunes:summary' )
        castiTunesArtist = ET.SubElement( rssChann, 'itunes:author' )
        
        fullPath = os.path.join( dirBase, srcDir )
        for fileName in genFeed( fullPath ):
            relPath = os.path.join( srcDir, fileName ) 
            fullURL = os.path.join( webBase, urllib.parse.quote( relPath ) )
            metaInfo = getMeta( os.path.join( fullPath, fileName ) )
            if metaInfo[ 'Title' ] == '':
                metaInfo[ 'Title' ] = srcDir
             
            castTitle.text = metaInfo[ 'Album' ] 
            castLink.text = webBase
            castDesc.text = metaInfo[ 'Summary' ]
            castiTunesDesc.text = metaInfo[ 'Summary' ]
            castiTunesArtist.text = str( metaInfo[ 'Authors' ] )
            
            castItem = ET.SubElement( rssChann, 'item' )
            
            itemTitle = ET.SubElement( castItem, 'title' )
            itemTitle.text = metaInfo[ 'Title' ]
            
            itemEnc = ET.SubElement( castItem, 'enclosure' )
            itemEnc.attrib[ 'url' ] = str( fullURL )
            itemEnc.attrib[ 'length' ] = str( metaInfo[ 'Size' ] )
            mimeType = mimetypes.guess_type( fullURL )[ 0 ]
            if not mimeType is None:
                itemEnc.attrib[ 'type' ] =  mimetypes.guess_type( fullURL )[ 0 ]
            else:
                if fileName.endswith( 'm4b' ):
                    itemEnc.attrib[ 'type' ] = 'audio/x-m4b'
            
            itemPubDate = ET.SubElement( castItem, 'pubDate' )
            itemPubDate.text = str( metaInfo[ 'PubDate' ] )
            
            itemGUID = ET.SubElement( castItem, 'guid' )
            itemGUID.text = fullURL
            
            itemiTunesAuthor = ET.SubElement( castItem, 'itunes:author' )
            itemiTunesAuthor.text = str( metaInfo[ 'Authors' ] )
            
            itemiTunesSummary = ET.SubElement( castItem, 'itunes:summary' )
            itemiTunesSummary.text = str( metaInfo[ 'Summary' ] )
            
            itemiTunesSubtitle = ET.SubElement( castItem, 'itunes:subtitle' )
            itemiTunesSubtitle.text = str( metaInfo[ 'Summary' ] )

            itemiTunesDuration = ET.SubElement( castItem, 'itunes:duration' )
            stringDuration = str( datetime.timedelta( seconds=int( metaInfo[ 'Duration' ] ) ) )
            itemiTunesDuration.text = stringDuration
            
        fullXML = ET.ElementTree( rssRoot )
        ET.dump( fullXML )
        xmlPath = os.path.join( dirBase, '%s.xml' % srcDir )
        fullXML.write ( xmlPath  )            

if __name__ == '__main__':
    sys.exit( main() )
    
    
    
    
import urllib.parse