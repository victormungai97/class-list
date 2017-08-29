# pictures.py

import os

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
