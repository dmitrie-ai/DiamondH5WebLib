# General systems
import os
import sys
import argparse
import gzip
import numpy as np
import time

# Flask
from flask import Flask, jsonify, request, after_this_request, redirect, \
    session, escape
from flask_compress import Compress




# CORS
from flask_cors import cross_origin,CORS

# CAS authentication
import urllib

# json
import json

# gzipping output
import gzip
import functools
from io import StringIO as IO

# Local resources
import handle_object
import zlib

# favicon
from flask import send_from_directory


######################
# CREATE APPLICATION #
######################

app = Flask(__name__)
CORS(app, supports_credentials=True)
# Session related variables
app.SECRET_KEY = 'blahblahblah'
app.SESSION_COOKIE_SECURE = True


CONFIG_FILE="config.cfg"
DEMO_DATA_FOLDER='demo_data'
DEMO_FILE1="example-data.h5"


debug=False

@app.route('/')
@app.route('/<path:path>')
@cross_origin(headers=['Content-Type'], supports_credentials=[True])
def get_data(path=''):

    """
    The main function - it's used for getting lists of directory and file
    contents as well as dataset contents.

    Submitted path names are intended to be as simple as possible, eg:
        - Get everything in the base data directory (as defined in config.cfg):
            /

        - List the contents of a sub-directory:
            /biomax/

        - List the contents of an hdf5 file that is located in a sub-directory:
            /biomax/example-data.h5

        - Get dataset values and information about it:
            /biomax/example-data.h5/scan_1/data_1/image

    If the argument "treepath" is present, then the folder contents of all of
    the ancestors of the given data path are returned, not the data itself.
    """


    # The output variable for this function
    downsample=request.args.get("downsample")
    downsample=True if downsample=="true" else False
    output_dictionary = {}

    output_dictionary = \
            handle_object.get_object(path,debug,downsample=downsample)
    json_resp=jsonify(output_dictionary)
    #json_str = json.dumps(output_dictionary)
    #
    start = time.time()
    #bin_resp=json_str.encode("utf-8")
    compress_level=1
    #gzip_resp=gzip.compress(bin_resp,compresslevel=compress_level)
    #z_strat=zlib.Z_HOFFMAN_ONLY
    #zlib_comp_obj=zlib.compressobj(level=compress_level)
    #zlib_resp=zlib_comp_obj.compress(bin_resp)
    # print(time.time()-start)

    #output_object=handle_object.get_object(path,debug)
    if debug:
        pass
    # Convert the dictionary to json format and return
    #output_compressed=gzip.compress(output_object.flatten().tobytes())

    resp = app.make_response(json_resp)
    # resp.headers['Content-Type']="application/octet-stream"
    # resp.headers["Content-Encoding"]="gzip"
    # resp.headers["Accept-Ranges"] = "bytes"
    # return output_compressed
    return resp

def main(config_file):
    '''
    The main function - usage and help, argument parsing
    '''

    # Note location of app.py file, as resources are located relative to it
    global APP_DIR
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    print('APP_DIR:', APP_DIR)


    try:

        # Load configuration file
        config_path = os.path.join(APP_DIR + '\\' + config_file)
        print('config_path:', config_path)
        app.config.from_pyfile(config_path)
        handle_object.CONFIG_PATH = config_path


        app.run(host='0.0.0.0', port=app.config['PORT'], threaded=True)

    # Quit nicely with ctrl-c input
    except KeyboardInterrupt:
        app.logger.info('Exiting flask server')
        print('Exiting flask server')
        sys.exit()


#######################
# RUN THE APPLICATION #
#######################

if __name__ == '__main__':
    main(config_file=CONFIG_FILE)