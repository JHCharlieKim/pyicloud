import os
from datetime import date, timedelta
from io import BytesIO

import piexif
from PIL import Image

from pyicloud import PyiCloudService

username = os.environ.get('PYICLOUD_USERNAME')
download_path = os.environ.get('DOWNLOAD_PATH', 'downloads')
api = PyiCloudService(username)

favorite_photo_id_map = dict()
for photo in api.photos.albums['Favorites']:
    favorite_photo_id_map[photo.id] = 1

print('You have {} favorite photos'.format(len(favorite_photo_id_map.keys())))

if not os.path.exists(download_path):
    os.makedirs(download_path)

screenshots_iterator = iter(api.photos.albums['Screenshots'])
while True:
    photo = next(screenshots_iterator, None)
    if photo is None:
        break

    last_month = date.today() - timedelta(days=30)
    if photo.created.date() > last_month:
        print('This screenshot is taken recently. Skip...')
        continue

    if favorite_photo_id_map.get(photo.id, 0) == 1:
        print('{} is favorite photo.'.format(photo.filename))
        continue

    filename = photo.filename
    while os.path.exists(os.path.join(download_path, filename)):
        filename = 'NEW_{}'.format(filename)

    print('Download {}'.format(filename))
    download = photo.download(version='original')
    image = Image.open(BytesIO(download.content))
    created_datetime = photo.created.strftime('%Y:%m:%d %H:%M:%S')

    exif_dict = piexif.load(image.info['exif']) if 'exif' in image.info else {'0th': {}, 'Exif': {}, 'GPS': {},
                                                                              '1st': {}}
    exif_dict['0th'][piexif.ImageIFD.DateTime] = created_datetime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = created_datetime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = created_datetime

    image.save(os.path.join(download_path, filename), exif=piexif.dump(exif_dict))

    print('Delete {}'.format(filename))
    photo.delete()
