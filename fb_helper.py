import urllib
import json

baseUrl = 'https://graph.facebook.com'
graphApiVersion = 'v2.2'

def graphApiRequest(token, graphApiXpath, fields=[]):
	params = {'access_token' : token};
	if fields != []:
		params['fields'] = reduce(lambda x,y: x+ ',' + y, fields)
	url = '%s/%s/%s?%s' % (baseUrl, graphApiVersion, graphApiXpath, urllib.urlencode(params))
	res = urllib.urlopen(url)
	if res.code != 200:
		raise Exception('GraphAPIException', res.read())
	return json.loads(res.read())


def collectPhotosAndTags(token, user_id=None):
	if user_id == None:
		user_id = graphApiRequest(token, 'me', ['id'])['id']
	photos = graphApiRequest(token, '%s/photos'%user_id, ['images','tags'])
	if len(photos['data']) == 0:
		raise Exception("No photos, probably not enough priviliges")
	results = getPhotosDetails(photos, user_id)
	paging = photos['paging']
	while('next' in paging.keys()):
		res = urllib.urlopen(paging['next'])
		photos = json.loads(res.read()) if res.code == 200 else None
		paging = photos['paging']				
		results += getPhotosDetails(photos, user_id)
	return results

def getPhotosDetails(jphotos, user_id):
	lst = [getPhotoData(p, user_id) for p in jphotos['data']]
	return [p for p in lst if p is not None]

def getPhotoData(jphoto, user_id):
	if len(jphoto['images']) == 0:
		return None
	photo_details = jphoto['images'][0]
	user_tags = [{'x': tag['x'], 'y': tag['y']} for tag in jphoto['tags']['data'] if 'id' in tag.keys() and tag['id'] == user_id]
	if len(user_tags) == 0:
		return None
	photo_details['x'] = user_tags[0]['x']
	photo_details['y'] = user_tags[0]['y']
	return photo_details

def retrieveImage(photo_det):
	try:
		(tmp_file, http_msg) = urllib.urlretrieve(photo_det['source'])
	except:
		return None
	return tmp_file
