#!/usr/bin/python

'''
Get images and arrays.
A routine for decimating images is included and used by default.
'''

#####################
# IMPORT LIBRARIES ##
#####################

# HDF5
import hdf5plugin
import h5py

# Image reduction
from skimage.measure import block_reduce
import copy


# General systems
import argparse
import sys
import numpy
import os.path

# Profiling
import cProfile

assert hdf5plugin  # silence pyflakes

downsample_block_size=(3,3)

###########
# HELPERS #
###########

def get_image(fileName, dataset_name, data_type, shape, slices,debug):
    '''
    Get an image, image from a series of images, or an array
    Slicing is allowed, and encouraged!
    '''

    if debug:
        print('')
        print('*** START resources/handle_images.py get_image ***')
        print('')
        print('fileName:    ', fileName)
        print('dataset_name:', dataset_name)
        print('data_type:   ', data_type)
        print('shape:       ', shape)
        print('slices:      ', slices)

    good_slice_def = True
    # limits = []
    #
    # # Set the absolute limits for image section selection (slicing)
    # for idx, dim in enumerate(shape):
    #     limits.append([0, dim])
    #     limits.append([0, dim])
    #
    # if debug:
    #     print('limits:      ', limits)
    #     print('')

    # Check for bad slice definitions
    # if (slices):

        #good_slice_def = True

        # The shape and number of slice parameters should be compatible
        # if len(slices) != len(limits):
        #     good_slice_def = False
        #
        # # There should be a certain number of slice parameters for certain data
        # # types
        # if (data_type == 'line' or data_type == 'text-array') \
        #         and len(slices) != 2:
        #     good_slice_def = False
        # if data_type == 'image' and len(slices) != 4:
        #     good_slice_def = False
        # if data_type == 'image-series' and len(slices) != 6:
        #     good_slice_def = False
        #
        # if good_slice_def:

        # Look at each slice parameter
        #for idx, slice_value in enumerate(slices):

            # If the given slice parameters are out of range, place them at
            # the limits
            # if slice_value < limits[idx][0]:
            #     print('Too small slice parameter: slices[', idx, ']:',
            #               slices[idx])
            #     slices[idx] = limits[idx][0]
            #
            # if slice_value > limits[idx][1]:
            #     print('Too big slice parameter: slices[', idx, ']:',
            #               slices[idx])
            #     slices[idx] = limits[idx][1]
            #
            # # If the second element of a pair of slice parameters is less
            # # than or equal to the first element, just give up and stop
            # # using the slice parameters.
            # if idx % 2 != 0 and slices[idx] <= slices[idx - 1]:
            #
            #     print('Oops!', slices[idx], 'is <=',
            #               slices[idx - 1])
            #     good_slice_def = False

        # For image series, make sure only one image is being returned,
        # otherwise there could be trouble for huge stacks of huge images...
        # if good_slice_def and data_type == 'image-series':
        #     if slices[1] - slices[0] > 1:
        #         slices[1] = slices[0] + 1

    # Open the file
    f1 = h5py.File(fileName, 'r')

    # If slices are properly defined, use them
    if good_slice_def and slices:

        if debug:
            print('slices just before using them:', slices)

        if data_type == 'line' or data_type == 'text-array':
            image = f1[dataset_name][slices[0]:slices[1]]

        if data_type == 'image':
            image = f1[dataset_name][slices[0]:slices[1], slices[2]:slices[3]]
            # Hopefully this will give the correct section of the image that is
            # being returned, even if the original slice definitions were out
            # of the actual image range


        if data_type == 'image-series':
            image = f1[dataset_name][slices[0],:,:]
            # For an image series, return the first image
            #image = image[0]


    else:

        # If no slices are defined, return the entire array or image
        if data_type == 'line' or data_type == 'text-array':
            image = f1[dataset_name][:]
        if data_type == 'image':
            image = f1[dataset_name][:, :]
            # The image section
        # For an image series, return the entire first image
        if data_type == 'image-series':
            image = f1[dataset_name][0, :, :]
            #image = image[0]

    # Close the file
    f1.close()
    if debug:
        print('')
        print('image size: ', image.shape)
        print('')
        print('image:')
        print(image)
        print('')
        print('*** END resources/handle_images.py get_image ***')
        print('')
    return image


def decimate_image(image_org, image_size_limit,debug):

    '''
    This function expects images.
    For image series, send just one image from the series, like:
        image[0]

    Not sure how best to do the downsampling - max? min? sum? average?
    Some useful things here perhaps:
        http://scikit-image.org/docs/dev/api/skimage.measure.html
            #skimage.measure.block_reduce
    '''

    if debug:

        print('')
        print('*** START resources/handle_images.py decimate_image ***')
        print('')

    # In addition to outputing a downsampled image (if necessary) the range of
    image_ds = False            # image downsampled
    image_bpr = False           # image bad pixels removed
    image_bpr_ds = False        # image bad pixels removed, downsampled

    perform_downsample = False

    # Find the maximum value of the image
    max_image = image_org.max()
    min_image = image_org.min()


    if debug:
        print('max_image:', max_image)
        print('min_image:', min_image)

    # The image_size_limit is assumed to be for a roughly square image
    if image_org.shape[0] * image_org.shape[1] > image_size_limit:
        perform_downsample = True

    if debug:
        print('image before downsampling')
        print('image size:            ', image_org.shape)
        print(image_org)
        print('')
        print('image_size_limit:      ', image_size_limit)
        print('image_org.shape[0]:        ', image_org.shape[0])
        print('image_org.shape[1]:        ', image_org.shape[1])
        print('perform_downsample:    ', perform_downsample)
        print('')

    if not(perform_downsample):
        image_ds = image_org
        is_downsampled = False

    else:

        # Calculate amount of downsampling
        # downsampleX = image_org.shape[0]
        # downsampleX = int(numpy.ceil(downsampleX/numpy.sqrt(image_size_limit)))
        # downsampleY = downsampleX




        try:

            image_ds = \
                block_reduce(image_org, block_size=downsample_block_size, func=numpy.mean)
            is_downsampled = True

        except ValueError as e:
            # Don't return the original image if there was a problem with
            # the downsampling process, might be too ginormous!
            image_ds = False
            is_downsampled = False
            print('*** image decimation problem ***')
            print(e)
            print('')

        if debug:
            print('')
            print('*** END resources/handle_images.py decimate_image ***')
            print('')


    return image_ds


def check_if_mx_file(file_path, debug):

    if debug:
        print('check_if_mx_file.file_path:' + file_path)

    is_mx_file = False
    master_file_path = False

    if '_data_' in file_path:
        file_pieces = file_path.split('/')
        data_file_name = file_pieces[-1]

        if debug:
            print('data_file_name: ' + data_file_name)

        is_mx_file = True

        # The master file name should follow a certain pattern
        file_extension = data_file_name.split('.')[-1]
        master_file_name = data_file_name.split('_data_')[0] + \
            '_master.' + file_extension
        master_file_path = ''
        for piece in file_pieces[:-1]:
            master_file_path += piece + '/'
        master_file_path += master_file_name
        does_master_file_exist = os.path.isfile(master_file_path)

        if debug:
            print('master_file_name: ' + master_file_name)
            print('master_file_path: ' + master_file_path)
            print('does_master_file_exist: ' + str(does_master_file_exist))

    return is_mx_file, master_file_path


def get_image_mask(master_file_path, debug):

    if debug:
        print('get_image_mask.master_file_path:' + master_file_path)

    mask_image = 'entry/instrument/detector/detectorSpecific/pixel_mask'

    image_mask = get_image(master_file_path, mask_image, debug=debug)

    return image_mask


def apply_image_mask(image, data_type, image_mask, mask_value, new_value,
                     debug):

    # Apply the mask using the given mask value (probably 1 or greater?) then
    # replace masked pixels with the new_value (0 seems to be a good choice)
    indicies = (image_mask >= mask_value)
    image_new = numpy.copy(image)

    if data_type == 2:
        image_new[indicies] = new_value
    if data_type == 3:
        image_new[:, indicies] = new_value

    return image_new


########
# MAIN #
########

def main(argv):
    '''
    The main function - usage and help, argument parsing
    '''

    # Setup options
    parser = argparse.ArgumentParser(
        description='Reduce (downsample) an image contained in an hdf5 file')
    parser.add_argument("input_file", nargs=1,
                        help='The input hdf5 file name')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Debug output')
    parser.add_argument("-i", '--image_index', required=False, default=0,
                        help='series index for the desired image')
    parser.add_argument("-m", '--mask_file', required=False,
                        default='tau1-tau_2_master.h5',
                        help='the hdf5 file containing the mask')
    parser.add_argument('-g', '--graphical_display', action='store_true',
                        help='Debug output')

    # Print a little extra in addition to the standard help message
    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        try:
            args = parser.parse_args(['-h'])
        except SystemExit:
            print('')
            print('Examples of usage:')
            print('')
            print('  python largeImages.py tau1-tau_2_data_000001.h5')
            sys.exit()
    else:
        args = parser.parse_args(argv)

    if args.debug:
        print(args)


#######################
# RUN THE APPLICATION #
#######################

if __name__ == '__main__':
    main(sys.argv[1:])
