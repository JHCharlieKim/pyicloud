import os

from pyicloud import PyiCloudService

username = os.environ.get('PYICLOUD_USERNAME')
api = PyiCloudService(username)

favorite_photo_id_map = dict()
for photo in api.photos.albums['Favorites']:
    favorite_photo_id_map[photo.id] = 1

print('You have {} favorite photos'.format(len(favorite_photo_id_map.keys())))

# TODO: mkdir download
screenshots_iterator = iter(api.photos.albums['Screenshots'])
while True:
    photo = next(screenshots_iterator, None)
    if photo is None:
        break

    if favorite_photo_id_map.get(photo.id, 0) == 1:
        print('{} is favorite photo.'.format(photo.filename))
        continue

    print('Download {}'.format(photo.filename))
    # download = photo.download(version='original')
    # TODO: Consider duplicated filename
    # TODO: Skip for x photos (Latest issue)
    # with open('download/{}'.format(photo.filename), 'wb') as opened_file:
    #     opened_file.write(download.raw.read())

    # print('Delete {}'.format(photo.filename))
    # photo.delete()
