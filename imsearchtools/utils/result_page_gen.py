#!/usr/bin/env python

"""Retrieve ranking lists from Google Image search

Uses either the Google AJAX API:
http://code.google.com/apis/imagesearch/v1/
or direct page scraping to retrieve a ranked list of images returned
from Google Image search for a given text query.

Date created: 15 Oct 2012
"""

import os.path

RESULT_PAGE_HTML = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Search Result Visualization</title>
<style>
  #result_container {

  }
  #result_container:after {
    content: ".";
    display: block;
    height: 0;
    clear: both;
    visibility: hidden;
  }
  .result {
    float: left;
                padding: 5px;
  }
  .result img {
    height: 130px;
  }
</style>
</head>

<body>
  <dl>
    <dt>Generator:</dt>
    <dd><!-- GENERATOR --></dd>
    <dt>Images returned:</dt>
    <dd><!-- IMAGE_COUNT --></dd>
  </dl>
  <div id="result_container">
    <!-- RESULTS -->
  </div>
</body>
</html>
'''

RESULT_HTML = '''
    <div class="result">
      <img src="<!-- RESULT_URL -->" alt="<!-- RESULT_TITLE -->" />
    </div>
'''

COMBINED_RESULT_PAGE_HTML = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Search Result Visualization</title>
<style>
  #result_frames_container {

  }
  #result_frames_container>div {
    display: block;
    float: left;
    width: 200px;
    padding: 5px;
    border: 1px solid black;
  }
  #result_frames_container:after {
    content: ".";
    display: block;
    height: 0;
    clear: both;
    visibility: hidden;
  }
  .result_img_container {
    height: 250px;
  }
  .result_img {
    max-width: 190px;
    max-height: 200px;
  }
</style>
<script src="http://code.jquery.com/jquery-latest.js"></script>
</head>

<body>
  <div id="result_frames_container">
    <!-- RESULT_FRAMES -->
  </div>
</body>
</html>
'''

RESULT_FRAME_HTML = '''
    <div>
      <!-- RESULT_FRAME_HEADER -->
      <!-- RESULTS -->
    </div>
'''

RESULT_FRAME_HEADER_HTML = '''
      <dl>
        <dt>Generator:</dt>
        <dd><!-- GENERATOR --></dd>
        <dt>Images returned:</dt>
        <dd><!-- IMAGE_COUNT --></dd>
      </dl>
'''

RESULT_IN_FRAME_HTML = '''
      <div class="result_img_container">
        <!-- RESULT_IDX -->
        <img class="result_img" src="<!-- RESULT_URL -->" alt="<!-- RESULT_TITLE -->" />
      </div>
'''

def gen_results_page(results, generator_name, output_filename, show_in_browser=True):
    result_page = RESULT_PAGE_HTML
    result_page = result_page.replace('<!-- GENERATOR -->', generator_name)
    result_page = result_page.replace('<!-- IMAGE_COUNT -->', str(len(results)))

    result_grid_code = ''
    for result in results:
        single_res_code = RESULT_HTML
        single_res_code = single_res_code.replace('<!-- RESULT_URL -->', result['url'])
        if result.has_key('title'):
            single_res_code = single_res_code.replace('<!-- RESULT_TITLE -->', result['title'])
        else:
            single_res_code = single_res_code.replace('<!-- RESULT_TITLE -->', result['image_id'])
        result_grid_code += single_res_code

    result_page = result_page.replace('<!-- RESULTS -->', result_grid_code)

    output = open(output_filename, 'w')
    output.write(result_page.encode('UTF-8'))
    output.close()

    if show_in_browser:
        import webbrowser
        webbrowser.open('file:///' + os.path.abspath(output_filename))


def combine_results_pages(results_arr, generator_name_arr, output_filename, show_in_browser=True):
    combined_page = COMBINED_RESULT_PAGE_HTML

    frames_code = ''

    for res_idx in range(len(results_arr)):
        frame_code = RESULT_FRAME_HTML

        results = results_arr[res_idx]
        generator_name = generator_name_arr[res_idx]

        result_grid_code = ''
        for res_idx, result in enumerate(results):
            single_res_code = RESULT_IN_FRAME_HTML
            single_res_code = single_res_code.replace('<!-- RESULT_IDX -->', str(res_idx+1))
            single_res_code = single_res_code.replace('<!-- RESULT_URL -->', result['url'])
            if result.has_key('title'):
                single_res_code = single_res_code.replace('<!-- RESULT_TITLE -->', result['title'])
            else:
                single_res_code = single_res_code.replace('<!-- RESULT_TITLE -->', result['image_id'])
            result_grid_code += single_res_code

        result_frame_header_code = RESULT_FRAME_HEADER_HTML
        result_frame_header_code = result_frame_header_code.replace('<!-- GENERATOR -->', generator_name)
        result_frame_header_code = result_frame_header_code.replace('<!-- IMAGE_COUNT -->', str(len(results)))

        frame_code = frame_code.replace('<!-- RESULT_FRAME_HEADER -->', result_frame_header_code)
        frame_code = frame_code.replace('<!-- RESULTS -->', result_grid_code)

        frames_code += frame_code

    combined_page = combined_page.replace('<!-- RESULT_FRAMES -->', frames_code)

    output = open(output_filename, 'w')
    output.write(combined_page.encode('UTF-8'))
    output.close()

    if show_in_browser:
        import webbrowser
        webbrowser.open('file:///' + os.path.abspath(output_filename))
