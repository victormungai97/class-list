# pictures.py

import os

from app import registration_folder, upload_folder
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}


def allowed_file(filename):
    """
    Function hecks whether file is allowed based on filename extension
    :param filename: File to be checked
    :return: Status of checking, either True(allowed) or False(disallowed)
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def compress_image(filename):
    """
    Function to resize(compress) image to a given size
    :param filename: Image to resize
    :return: None
    """
    from PIL import Image  # library for compressing images
    # open file to be compressed
    img = Image.open(filename)
    # compress the image accordingly
    foo = img.resize((200, 200), Image.ANTIALIAS)
    # save the downsized image
    foo.save(filename, optimize=True, quality=100)


def register_get_url(filename="", path="", counter=0, regno="", list_of_images=None):
    """
    Function to retrieve the URL of image to be saved
    :param list_of_images: List of images uploaded by student
    :param filename: Name of image
    :param path: Path to the folder to contain image
    :param counter: No of image in array
    :param regno: Registration number of student
    :return: URL of image
    """
    if list_of_images is None:
        list_of_images = []
    # get extension of file
    extension = str(filename.split(".")[len(filename.split(".")) - 1])
    # get path to source of uploaded file
    source = path + filename
    # get path of file
    file_ = path + regno + "_" + str(counter) + "." + extension
    # call learning code
    if counter == len(list_of_images):
        ################################################
        """Face learning to go here"""
        pass
        #################################################
    # delete existing file
    if os.path.isfile(file_):
        os.remove(file_)
    # rename file
    os.rename(source, file_)
    # get url to save to db
    return file_.replace("app/static/", "")


def class_get_url(filename="", path="", regno=""):
    """
    Function to retrieve the URL of image to be saved during class attendance
    :param filename: Name of image
    :param path: Path to the folder to contain image
    :param regno: Registration number of student
    :return: URL of image and verification status of image
    """
    # get extension of file
    extension = str(filename.split(".")[len(filename.split(".")) - 1])
    # get path to source of uploaded file
    source = path + filename
    # get path of file
    file_ = path + regno + "." + extension
    # status for verification, to be modified as per findings of image recognition
    verified = 1

    # call image recognition code
    ##############################
    pass
    ##############################

    # delete existing file
    if os.path.isfile(file_):
        os.remove(file_)
    # rename file
    os.rename(source, file_)
    # get url to save to db
    return file_.replace("app/static/", ""), verified


def determine_picture(reg_num, image, list_of_images=None, counter=0):
    """
    Function that processes images before their URLs are retrieved
    :param reg_num: Registration number of student
    :param image: Specific image being processed
    :param list_of_images: List of images uploaded by student
    :param counter: No. of image in list
    :return: URL of image and verification code if any
    """
    # split reg_num to retrieve year, course and specific number of student
    if list_of_images is None:
        list_of_images = []
    details = reg_num.split("/")
    # create new path to folder for student's image(s)
    path = '/'.join([upload_folder, details[0], details[2], '/'])
    # create the new folder
    if not os.path.isdir(path):
        os.makedirs(path)
    # get name of the source file + Make the filename safe, remove unsupported chars
    filename = str(secure_filename(image.filename))
    # save image
    image.save(os.path.join(path, filename))
    # compress image
    compress_image(os.path.join(path, filename))
    if list_of_images and counter != 0:
        return register_get_url(filename, path, counter, regno=details[1], list_of_images=list_of_images)
    return class_get_url(filename, path, regno=details[1])
