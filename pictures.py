# pictures.py

import os

from app import upload_folder
# from classifier import infer

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
    source = os.path.join(path, filename)
    # get path of file
    file_ = os.path.join(path, "".join([str(regno), "_", str(0), ".", extension]))
    # status for verification, to be modified as per findings of image recognition
    verified = 1

    # check if file is in current directory. If so, rename it
    for root, dirs, files in os.walk(path):
        for i in range(len(files)):
            files[i] = os.path.join(root, files[i])
        common_files = []
        if file_ in files:
            for file in files:
                if os.path.basename(file).startswith(str(regno)):
                    common_files.append(file)
            file_ = common_files[-1]
            start, end = tuple(file_.split('_'))
            file_ = "_".join([start, ".".join([str(int(end[0]) + 1), extension])])

    # rename file
    os.rename(source, file_)
    # get url to save to db
    return file_.replace("app/static/", ""), verified


def determine_picture(reg_num, image, filename, attendance=False):
    """
    Function that processes images and
    returns their URLs and the verification status of the images, if any
    :param attendance: Checks whether student is registering or attending class
    :param filename: Name of the specific image file
    :param reg_num: Registration number of student
    :param image: Specific image being processed
    :return: URL of image and verification code if any
    """
    # split reg_num to retrieve year, course and specific number of student
    details = reg_num.split("/")
    # create new path to folder for student's image(s)
    path = '/'.join([upload_folder, details[0], details[2], details[1], '/'])
    # create the new folder
    if not os.path.isdir(path):
        os.makedirs(path)
    # split filename into basename and components
    basename, extension = filename.rsplit('.', 1)[0], filename.rsplit('.', 1)[-1]
    # get path of file
    filename = os.path.join(path, "".join([basename, "_", str(0), ".", extension]))

    # check if file is in current directory. If so, rename it
    for root, dirs, files in os.walk(path):
        for i in range(len(files)):
            files[i] = os.path.join(root, files[i])
        common_files = []
        if filename in files:
            for file in files:
                if os.path.basename(file).startswith(basename):
                    common_files.append(file)
            if common_files:
                filename = common_files[-1]
                start, end = tuple(filename.split('_'))
                filename = "_".join([start, ".".join([str(int(end[0]) + 1), extension])])

    # save image
    image.save(filename)
    # compress image
    compress_image(filename)

    # status for verification, to be modified as per findings of image recognition
    verified = 1

    # call image recognition code
    ##############################
    if attendance:
        print("Calling image recognition")
        '''
        rs = infer(path)
        if rs >= 0.7:
          verified = 1
        elif rs < 0.7:
          verified = 4
        '''
    ##############################

    return filename.replace("app/static/", ""), verified
