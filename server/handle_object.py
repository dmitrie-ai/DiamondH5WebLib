import os
import h5py
import handle_images
import gzip
import numpy as np
#import handle_scalars
from skimage.measure import block_reduce

SIZE_LIMIT=1.6e5
downsample_block_size=(4,4)

CONFIG_FILE="config.cfg"
def parse_object_path(input_string):

    """
    This function figures out what is in the given input string:
        - A folder
        - An hdf5 file
        - A dataset within an hdf5 file
        - A folder within an hdf5 file
    """
    object_type = file_path = h5_path = slice_par = False

    # Strip possible trailing characters
    input_string = input_string.rstrip('/ \\')

    # Possible hdf5 file name extensions
    hdf5_file_extensions = ['.h5', '.hdf5', '.hdf', '.nxs', '.nx5']

    # Check if this is a file or folder that should be ignored


    # Check if this string ends with an hdf5 file name
    if input_string.endswith(tuple(hdf5_file_extensions)):

        object_type = 'h5_file'
        file_path = input_string

    else:

        # Now see if it contains a file name plus some object path
        for ext in hdf5_file_extensions:

            # Split the string on the extension plus trailing slash
            delim = ext + '/'
            if delim in input_string:

                split_string = input_string.split(delim, 1)

                # The file path is the first piece
                file_path = split_string[0] + ext

                # The path within the file is the rest
                h5_path = '/' + split_string[1]

                object_type = 'h5_object'

        # If there was no file extension in the string, then this is
        # probably a simple folder path
        if not object_type:

            object_type = 'folder'
            file_path = input_string

        # Check if there is image slice notation in the h5_path, if so,
        # save to a list - there must be a smarter way to do this :)
        if h5_path:

            # The slice notation should be enclosed by brackets
            if '[' and ']' in h5_path:
                # Look for the slice notation
                slice_string = \
                    h5_path[h5_path.find("[")+1:h5_path.find("]")]

                # Split at commas
                split_string = slice_string.split(',')
                # Create a list into which the split parameter will be
                # saved
                slice_par=[int(x) for x in split_string]
                # slice_par = [None]*(len(split_string)*2)
                #
                # for i, elem in enumerate(split_string):
                #
                #     # Look for colons separating slice parameters
                #     split_par = elem.split(':')
                #     # Save each slice parameter
                #     slice_par[i*2] = int(split_par[0])
                #     slice_par[i*2 + 1] = int(split_par[1])

                # Remove the slice notation from h5_path
                split_string = h5_path.split('[', 1)
                h5_path = split_string[0]


    return object_type, file_path, h5_path, slice_par

def does_object_exist(object_type, file_path, h5_path,debug):

    """
    This function determines whether or not a given item exists, which could
    be one of the following
        - A folder on disk
        - An hdf5 file
        - An dataset within an hdf5 file
        - A folder within an hdf5 file

    If the object is within an hdf5 file, the type of item is determined:
        - folder within the hdf5 file
        - number
        - string
        - image
        - image series
        - line (array)
    """
    object_exists = False
    path_exists = False
    data_type = False
    shape = False
    f1 = False

    # Check if the file or folder path exists
    if file_path:
        path_exists = os.path.exists(file_path)
        if debug:
            print(f"path {file_path} exists:{path_exists}")

    if object_type == 'h5_object' and path_exists:


        # Open the file
        try:
            f1 = h5py.File(file_path, 'r')

            # See if the given h5 object exists
            object_exists = h5_path in f1
        except IOError:
            print('path is invalid')

        if object_exists:

            # If this is an HDF5 data object, check if it's a group or dataset
            # - are there other possibilities as well?
            try:
                h5_object = f1[h5_path]

                print('h5_object.name: ' + str(h5_object.name))
                data_type, shape = is_h5_group_or_dataset(h5_object)
            except KeyError:
                h5_object = False

        else:
            print('the object ' + str(h5_path) + ' does not exist')

        if f1:
            f1.close()

    else:
        object_exists = path_exists

    return object_exists, data_type, shape

def is_h5_group_or_dataset(h5_object):

    """
    If the object is within an hdf5 file, the type of item is determined:
        - folder within the hdf5 file
        - number
        - string
        - image
        - image series
        - line (array)
    """

    data_type = shape = False

    # Need to see if this is a folder (group) or data (dataset)
    # Are there other possibilities?
    try:
        h5_object_data_type = h5_object.dtype
        print('')
        print('h5_object.dtype: ' + str(h5_object_data_type))
        print('h5_object.shape: ' + str(h5_object.shape))
        print('h5_object.dims: ' + str(h5_object.dims))
        for dim in h5_object.dims:
            print('dim.label: ' + str(dim.label))
        print('h5_object.file: ' + str(h5_object.file))
        print('h5_object.parent: ' + str(h5_object.parent))
        print('h5_object.attrs: ' + str(h5_object.attrs))

        shape = h5_object.shape
        shape_length = len(shape)

        # See what the hell we've got here - this part could be done better...
        if shape_length == 0:
            if 'float' in str(h5_object.dtype) or \
                    'int' in str(h5_object.dtype):
                data_type = 'number'
            else:
                data_type = 'text'

        if shape_length == 1:
            data_type = 'line'

            # Sometimes strings are stored in an array, try to look for
            # such cases
            if shape[0] == 1:
                array = h5_object[:]
                string_value = array[0]
                is_string = isinstance(string_value, str)
                if is_string:
                    data_type = 'text-array'

        if shape_length == 2:
            data_type = 'image'
        if shape_length == 3:
            data_type = 'image-series'

    except AttributeError:
        data_type = 'h5_folder'
        shape = 0

    print('')
    print('data_type: ' + str(data_type))
    print('')
    print('*** END resources_py/handle_object.py is_h5_group_or_dataset')
    print('')

    return data_type, shape

def get_object(input_string,debug,downsample=False):

    """
    Input:
        - folder/file/object path name
        - debug (True or False)

    Output:
        - output_object
        - object_type
        - data_type
        - shape
    """
    output_object = shape = False

    # Parse input - directory? file? directory in a file? object in a file?
    object_type, file_path, h5_path, slice_par = \
        parse_object_path(input_string)
    if debug:
        print(f'object_type: {object_type}')
    object_exists, data_type, shape = \
        does_object_exist(object_type, file_path, h5_path,debug)

    if debug:
        print(f'Object exists: {object_exists}')

    # If this is a folder, get the contents
    if object_type == 'folder':

        output_object = get_folder_contents(file_path,debug)

    # If this is a file, get the contents
    if object_type == 'h5_file':

        output_object = \
            get_h5_file_folder_contents(file_path, h5_path, data_type,debug)

    # If this is an object within an hdf5 file, get it!
    if object_type == 'h5_object':

        # If this is a folder in an hdf5 file, get the contents
        if data_type == 'h5_folder':

            output_object = \
                get_h5_file_folder_contents(file_path, h5_path, data_type,debug)

        # If this is a dataset, get the values
        elif data_type == 'image' or data_type == 'image-series' \
            or data_type == 'line' or data_type == 'text' \
                or data_type == 'number' or data_type == 'text-array':

            output_object= get_dataset(file_path, h5_path, data_type,
                                             shape, slice_par,debug)

            if downsample==True:

                downsampled_image=block_reduce(output_object, block_size=downsample_block_size, func=np.mean)
                output_object=downsampled_image
                downsample=downsample_block_size[0]
            else:
                downsample=0
    # Create an output dictionary, save some information
    output_dictionary = \
        convert_data_to_dict_list(input_string, output_object, object_type,
                                  data_type, shape,downsample)

    return output_dictionary
    #return output_object

def get_dataset(file_path, h5_path, data_type, shape, slice_par,debug):
    if debug:
        print('')
        print('*** START resources_py/handle_object.py get_dataset ***')
        print('')
        print('data_type: ', data_type)
        print('')

    dataset = {}

    if data_type == 'image' or data_type == 'image-series' \
            or data_type == 'line' or data_type == 'text-array':

        # Get the image or array from the file
        image = handle_images.get_image(file_path, h5_path, data_type,
                                                 shape, slices=slice_par,debug=debug)



        dataset = image

    print('')
    print('*** END resources_py/handle_object.py get_dataset ***')
    print('')

    return dataset
def get_h5_file_folder_contents(file_path, h5_path, data_type,debug):

    """
    Check this shit out:
    http://docs.h5py.org/en/latest/high/group.html#reference
    """

    if debug:
        print('')
        print('*** START resources_py/handle_object.py '
              'get_h5_file_folder_contents ***')
        print('')

    h5_file = h5_object = False

    # Create output dictionary
    contents = {}
    contents['folder_contents'] = {}

    # Open the file
    try:
        h5_file = h5py.File(file_path, 'r')
    except IOError:
        h5_file = False
        print('not an hdf5 file? empty file?')
    except Exception:
        h5_file = False
        print('Unexpected error:')

    # Get the folder in the file if requested, otherwise just open the file
    if h5_file and h5_path:
        h5_object = h5_file[h5_path]
    else:
        h5_object = h5_file

    # Read the config file in order to make urls
    file_url = create_file_url(file_path,debug)

    # Loop over items, add to output dictionary
    i = 0
    if h5_object:
        for key in list(h5_object.values()):

            item_type, shape = is_h5_group_or_dataset(key)
            if key is None:
                print('*** BAD KEY - SKIPPING ***')

            if item_type == 'text-array':
                item_type = 'text'

            if debug:
                print('key.name:  [', key.name, ']')
                print('item_type: [', item_type, ']')

            # The full path name on the host system (key.name contains a slash
            # at the beginning)
            full_path = file_path + key.name

            # Create the url for this item
            item_url = file_url + key.name

            # Create a shortened name from the full path name
            split_string = key.name.lstrip('/ \\')
            split_string = split_string.rstrip('/ \\')
            split_string = split_string.split('/')
            short_name = split_string[-1]

            # The output dictionary which will eventually be sent as json
            contents['folder_contents'][i] = {}
            contents['folder_contents'][i]['short_name'] = short_name
            contents['folder_contents'][i]['full_name'] = full_path
            contents['folder_contents'][i]['url'] = item_url
            contents['folder_contents'][i]['item_type'] = item_type
            contents['folder_contents'][i]['shape'] = shape

            i += 1

    if h5_file:
        h5_file.close()

    return contents

def get_folder_contents(file_path,debug):

    # Create output dictionary
    contents = {}
    contents['folder_contents'] = {}

    # Get the folder contents
    item_list = []
    item_list = os.listdir(file_path)


    # Read the config file in order to make urls
    file_url = create_file_url(file_path,debug)

    # Loop over items, add to output dictionary
    i = 0
    for item in item_list:

        short_name = False
        full_path = False
        item_url = False
        item_type = False

        # Assemble the complete file path, note type of file. There should only
        # be two possibilities: folder or hdf5 file. Other file types need to
        # be ignored with ignore_file()
        full_path = file_path + '/' + item
        if os.path.isfile(full_path):
            item_type = 'h5_file'
        if os.path.isdir(full_path):
            item_type = 'folder'


        # Create the url for this item
        item_url = file_url + '/' + item

        # Create a shortened version of the name - just the file name,
        # folder, or item within an hdf5 file
        short_name = os.path.basename(item)

        contents['folder_contents'][i] = {}
        contents['folder_contents'][i]['short_name'] = short_name
        contents['folder_contents'][i]['full_name'] = full_path
        contents['folder_contents'][i]['url'] = item_url
        contents['folder_contents'][i]['item_type'] = item_type

        i += 1

    return contents
def create_file_url(file_path,debug):

    config_par = read_config_file()
    data_dir = protocol = host_name = port = False

    if 'DATA_DIR' in config_par:
        data_dir = config_par['DATA_DIR']
        if debug:
            print(f"config DATA_DIR:{data_dir}")
    if 'PROTOCOL' in config_par:
        protocol = config_par['PROTOCOL']
    if 'HOST_NAME' in config_par:
        host_name = config_par['HOST_NAME']
    if 'PORT' in config_par:
        port = config_par['PORT']

    # I'm making the urls without the data directory name, so remove it.
    # The resulting url will not be sensible if this script is run from the
    # command line and the given path does not match that in the config file
    file_path_in_data_dir = ''
    if data_dir in file_path:
        file_path_in_data_dir = file_path.split(data_dir, 1)[1]
    else:
        file_path_in_data_dir = file_path
    if debug:
        print(f'file path in data dir: {file_path_in_data_dir}')
    # Construct file url
    file_url = protocol + '://' + host_name + ':' + port + '/'+\
        file_path_in_data_dir
    if debug:
        print(f'file url: {file_url}')

    return file_url

def read_config_file():

    # Dumb way to get the config options?
    config_par = {}
    with open(CONFIG_FILE) as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            name = name.strip()
            var = var.strip()
            var = str(var.replace("'", ""))
            var = var.rstrip('/ \\')
            config_par[name] = var

    data_dir = protocol = host_name = port = False

    if 'DATA_DIR' in config_par:
        data_dir = config_par['DATA_DIR']
    if 'PROTOCOL' in config_par:
        protocol = config_par['PROTOCOL']
    if 'HOST_NAME' in config_par:
        host_name = config_par['HOST_NAME']
    if 'PORT' in config_par:
        port = config_par['PORT']

    # return data_dir, protocol, host_name, port
    return config_par

def convert_data_to_dict_list(path, dataset, object_type, data_type, shape,downsampled=0):

    dataset_dict = {}
    dataset_dict['path'] = path
    if dataset is False:
        return dataset_dict

    if object_type == 'h5_object':

        dataset_dict['object_type'] = object_type
        dataset_dict['item_type'] = data_type

        if data_type == 'image-series' or data_type == 'image' or \
                data_type == 'line':
            dataset_dict['shape'] = shape
            dataset_dict['values'] = dataset.tolist()
            dataset_dict['downsampled']=downsampled


        if data_type == 'number':
            dataset_dict['values'] = dataset.tolist()

        if data_type == 'text' or data_type == 'text-array':
            if isinstance(dataset, str):
                dataset_dict['values'] = dataset
            else:
                dataset_dict['values'] = str(dataset.decode())

            # quick fix - need to fill these in properly!
            dataset_dict['error'] = 'False'
            dataset_dict['item_type'] = 'text'
            dataset_dict['does_exist'] = 'True'
            dataset_dict['short_name'] = os.path.basename(dataset_dict['path'])

        if data_type == 'h5_folder':
            dataset_dict.update(dataset)

    if object_type == 'h5_file' or object_type == 'folder':
        dataset_dict['object_type'] = object_type
        dataset_dict.update(dataset)


    return dataset_dict
