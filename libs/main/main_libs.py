import glob
import PIL.Image as Image
import uuid
import os


def get_all_images(path):
    os.chdir('static')  # 改变工作目录到 static
    fs = glob.glob(path + '/*.jpg')  # uploads/*.jpg
    os.chdir('..')  # 改变工作目录回到todo
    return fs


def save_files_lib(abs_img_path, img):
    ''' 存图片 '''
    try:
        with open(abs_img_path, 'wb') as f:
            f.write(img)
    except:
        return False
    return True


def change_to_thumbnail(img_save_path, abs_thumbnail_father_path):
    ''' 存缩略图 '''
    img = Image.open(img_save_path)
    size = (100, 100)
    img_name = os.path.basename(img_save_path)
    img_name_point_left, img_right = os.path.splitext(img_name)
    thumbnail_save_path = abs_thumbnail_father_path + img_name_point_left + '{}x{}'.format(size[0], size[1]) + img_right
    img.thumbnail(size)
    img.save(thumbnail_save_path, 'JPEG')
    return True
