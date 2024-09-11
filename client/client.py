import os
from datetime import date, timedelta
from io import BytesIO
from multiprocessing.pool import ThreadPool

import piexif
from PIL import Image

from pyicloud import PyiCloudService
from pyicloud.services.photos import PhotoAsset


def download_and_delete_photo(asset: PhotoAsset):
    last_month = date.today() - timedelta(days=30)
    if asset.created.date() > last_month:
        print('This screenshot is taken recently. Skip...')
        return

    if favorite_photo_id_map.get(asset.id, 0) == 1:
        print('{} is favorite photo.'.format(asset.filename))
        return

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

favorite_photo_id_map = dict()
for photo in api.photos.albums['Favorites']:
    favorite_photo_id_map[photo.id] = 1

print('You have {} favorite photos'.format(len(favorite_photo_id_map.keys())))

if not os.path.exists(download_path):
    os.makedirs(download_path)

pool = ThreadPool(processes=number_of_thread_pool)
pool.map(download_and_delete_photo, iter(api.photos.albums['Screenshots']))
pool.close()
