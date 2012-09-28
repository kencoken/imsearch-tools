Google Image Downloader Tool
============================================

Author: Ken Chatfield, University of Oxford (ken@robots.ox.ac.uk)

Copyright 2010-2012, all rights reserved.

Usage Instructions
------------------
 + Import both the `gimage_query` and `gimage_download` modules
 + Call either `gimage_query.dowebquery` (recommended) or `gimage_query.doapiquery`
   with the text string for which you require the Google Image search results
 + An object containing the URLs of the images in the results will be returned. Pass
   this to `gimage_download.downimages` to download the images to a given directory
   