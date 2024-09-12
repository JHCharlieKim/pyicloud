import os
from datetime import date, timedelta
from io import BytesIO
from multiprocessing.pool import ThreadPool

import piexif
from PIL import Image

from pyicloud import PyiCloudService
from pyicloud.services.photos import PhotoAsset


def download_and_delete_photo(asset: PhotoAsset):
    created_date_for_filename = asset.created.strftime("%Y%m%d_%H%M%S")
    name, extension = asset.filename.split(".")
    filename = '{}_{}.{}'.format(name, created_date_for_filename, extension)

    print('Download {}'.format(filename))
    download = asset.download(version='original')
    image = Image.open(BytesIO(download.content))
    created_datetime = asset.created.strftime('%Y:%m:%d %H:%M:%S')

    exif_dict = piexif.load(image.info['exif']) if 'exif' in image.info else {'0th': {}, 'Exif': {}, 'GPS': {},
                                                                              '1st': {}}
    exif_dict['0th'][piexif.ImageIFD.DateTime] = created_datetime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = created_datetime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = created_datetime

    image.save(os.path.join(download_path, filename), exif=piexif.dump(exif_dict))

    print('Delete {}'.format(filename))
    asset.delete()


username = os.environ.get('PYICLOUD_USERNAME')
download_path = os.environ.get('DOWNLOAD_PATH', 'downloads')
number_of_thread_pool = os.environ.get('NUMBER_OF_THREADS_POOL', 4)
api = PyiCloudService(username)

if not os.path.exists(download_path):
    os.makedirs(download_path)

candidates = []
last_month = date.today() - timedelta(days=30)
screenshots_iterator = iter(api.photos.albums['Screenshots'])
while True:
    photo = next(screenshots_iterator, None)
    if photo is None:
        break

    if photo.created.date() > last_month:
       break

    if photo.is_favorite:
        continue

    candidates.append(photo)

pool = ThreadPool(processes=number_of_thread_pool)
pool.map(download_and_delete_photo, candidates)
pool.close()
