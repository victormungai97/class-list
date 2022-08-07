# pictures.py

import os
from shutil import move
from werkzeug.utils import secure_filename

from app.extras import unique_files, create_path

# from classifier import infer

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}


def allowed_file(filename):
    """
    Function checks whether file is allowed based on filename extension
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
    import piexif  # library for holding on to exif data eg orientation
    # open file to be compressed
    img = Image.open(filename)
    # load exif data
    try:
        exif_dict = piexif.load(img.info["exif"])
        exif_bytes = piexif.dump(exif_dict)
    except BaseException as err:
        print('Exif error: {}'.format(err))
        exif_bytes = None
    # compress the image accordingly
    foo = img.resize((200, 200), Image.ANTIALIAS)
    # save the downsized image
    if exif_bytes:
        foo.save(filename, optimize=True, quality=100, exif=exif_bytes)
    else:
        foo.save(filename, optimize=True, quality=100)


def determine_picture(reg_num, name, image, filename, attendance=False, phone=False, path=""):
    """
    Function that processes images and
    returns their URLs and the verification status of the images, if any
    :param name: Name of the student
    :param phone: Checks if image is from phone
    :param attendance: Checks whether student is registering or attending class
    :param filename: Name of the specific image file
    :param reg_num: Registration number of student
    :param image: Specific image being processed
    :param path: Location where images is saved
    :return: URL of image and verification code if any
    """
    if not path:
        path = create_path(reg_num)
    file_ = os.path.join(path, filename)
    # split filename into basename and components
    basename, extension = filename.rsplit('.', 1)[0], filename.rsplit('.', 1)[-1]
    # change base name to name of student
    basename = name
    # get path of file
    filename = os.path.join(path, "".join([basename, "_", str(0), ".", extension]))
    if phone:
        move(file_, filename)
        file_ = filename

    filename = unique_files(path, filename, basename, extension)

    # save image
    if not phone:
        image.save(filename)
    else:
        move(file_, filename)

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


def decode_image(data, name, reg_num, ext=".jpg"):
    """
    Function to decode byte string to image
    Base64 module function b64decode will decode the byte string into bytes
    and these bytes will then be written into a file whose name is the student's name
    :param ext: The file's extension
    :param reg_num: Registration number of the student
    :param data: Byte string of the image
    :param name: Name of student to be used as file name
    :return: Image file name of the student
    """
    # get encoded version of the byte string
    img_data = data.encode('UTF-8', 'strict')
    path = create_path(reg_num)
    import base64
    # create file name
    pic_name = path + '/' + secure_filename(name) + ext
    # decode image string and write into file
    with open(pic_name, 'wb') as fh:
        fh.write(base64.b64decode(img_data))
    # return file name without directory path
    return pic_name.rsplit('/', 1)[-1]
