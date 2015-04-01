import pickle
import os.path as path
import os
import glob
import threading
import fb_helper
import image_helper
import sys
from retrying import retry
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

(NEW, INITIATED, IMAGES_SOURCES_READY, FACES_DATA_READY, SCENES_CHOSEN, SCENES_GENERATED) = range(6)

LAST_STATE = SCENES_GENERATED

scenesBasePath = '/home/shachar/Images/scenes'

basePath = '/home/shachar/projects/SaveME'
cacheBasePath = path.join(basePath, 'cache')
storyBasePath = path.join(basePath, 'view/story')

stepPerState = {
	INITIATED : lambda sp, token: sp.retrievePhotosLinks(token),
	IMAGES_SOURCES_READY : lambda sp, token: sp.retrievePhotosData(),
	FACES_DATA_READY : lambda sp, token: sp.chooseScenesParams(),
	SCENES_CHOSEN : lambda sp, token: sp.generateScenes(),
	SCENES_GENERATED : lambda sp, token: True
}


class StorylineProcessor():
	
	def __init__(self):
		self.__setState(NEW)
		self.running = False; # BUG -> It is persisted also. Need to unpersist it.
		#self.lock = threading.Lock()
		self.basic_details = {'id' : None}

	def __setState(self, state):
		self.state = state

	def getId(self):
		return self.basic_details['id']

	@retry(stop_max_attempt_number=3)
	def start(self, fb_access_token):
		self.basic_details = fb_helper.graphApiRequest(fb_access_token, 'me', ['id', 'name', 'first_name', 'last_name', 'gender'])
		self.__setState(INITIATED)

	@retry(stop_max_attempt_number=3)
	def retrievePhotosLinks(self, fb_access_token):
		self.photos_sources = fb_helper.collectPhotosAndTags(fb_access_token, self.basic_details['id'])
		self.__setState(IMAGES_SOURCES_READY)

	@retry(stop_max_attempt_number=5)
	def retrievePhotosData(self):
		user_files_details = [(p, fb_helper.retrieveImage(p)) for p in self.photos_sources[:75]]
		user_faces_images = [image_helper.cropFaceFromImageDetails(*im) for im in user_files_details]
		self.user_faces_images = [im for im in user_faces_images if im != None]
		self.__setState(FACES_DATA_READY)

	def chooseScenesParams(self):
		user_faces_map = { i : img for i, img in enumerate(self.user_faces_images) }
		self.scenes = ['wedding-photobomb1.jpg', 'wedding-photobomb3.jpg']
		scenes_faces = { s : image_helper.loadSubImage(path.join(scenesBasePath, s)) for s in self.scenes }
		sorted_by_hist = { s : image_helper.sortByHistogram(scenes_faces[s], user_faces_map) for s in self.scenes }
		self.scenes_params = [(s, sorted_by_hist[s][0][0]) for s in self.scenes]
		self.__setState(SCENES_CHOSEN)

	def __getOutputDir(self):
		user_dir = path.join(storyBasePath, self.basic_details['id'])
		if not path.exists(user_dir):
			os.mkdir(user_dir)
		# Delete exisitng files
		for f in os.listdir(user_dir):
			os.remove(path.join(user_dir, f))
		return user_dir;

	def generateScenes(self):
		self.generated_scenes = [(s, image_helper.placeFaceInScene(path.join(scenesBasePath, s), self.user_faces_images[u])) for s, u in self.scenes_params]
		odir = self.__getOutputDir()
		self.generated_images_paths = {}
		for name, img in self.generated_scenes:
			impath = path.join(odir, name)
			image_helper.saveImage(impath, img)
			self.generated_images_paths[name] = path.relpath(impath, basePath)
		self.__setState(SCENES_GENERATED)

	def __repr__(self):
		return "StorylineProcessor[%s]: State = %d | Running = %d" % (self.basic_details['id'], self.state, self.running)


#storyProcessorsCache = {}
cache_opts = {'cache.type': 'memory'}
cache_manager = CacheManager(**parse_cache_config_options(cache_opts))

def go(fb_access_token):
	sp = StorylineProcessor()
	try:
		sp.start(fb_access_token)
	except Exception as e: 
		print "Error ", e, sp
		return { 'status': -1 }
	pId = sp.getId()
	#latestSP = loadLatestSP(pId)
	latestSP = getFromCache(pId)
	if latestSP != None:
		sp = latestSP
	else:
		saveToCache(pId, sp)
	res = { 'status': sp.state }
	if sp.state == LAST_STATE:
		print "Everythings baked for id %s" % pId
		res['images'] = sp.generated_images_paths
	elif not sp.running:
		print "Start new thread for id %s" % pId
		threading.Thread(target=runSP, args=[sp, fb_access_token]).start()
	return res

def saveToCache(pId, sp):
	sp_cache = cache_manager.get_cache('stories')
	sp_cache.put(pId, sp)

def getFromCache(pId):
	sp_cache = cache_manager.get_cache('stories')
	return sp_cache.get(pId) if sp_cache.has_key(pId) else None

def runSP(sp, fb_access_token):
	sp.running = True
	print "Running for step %d." % sp.state
	try:
		result = stepPerState[sp.state](sp, fb_access_token)
	except Exception as e:
		print "Error ", e, sp
		sp.running = False
		return
	print "Done %d." % sp.state
	if sp.state in (IMAGES_SOURCES_READY, FACES_DATA_READY, LAST_STATE):
		persist(sp)
	if sp.state < LAST_STATE:
		runSP(sp, fb_access_token)
	else:
		print "Finito running"
		sp.running = False

def loadLatestSP(user_id):
	#if user_id in storyProcessorsCache:
	#	return storyProcessorsCache[user_id
	user_dir = path.join(cacheBasePath, user_id)
	if(not path.exists(user_dir)):
		return None
	cache_files = glob.glob(path.join(user_dir, '[0-%d].dat' % LAST_STATE))
	cache_files.sort(key=lambda p: int(path.splitext(path.basename(p))[0]), reverse=True)
	if len(cache_files) == 0:
		return None
	sp = loadSP(cache_files[0])
	sp.running = False
	print "Loaded SP from cache %s" % user_id
	#storyProcessorsCache[user_id] = sp
	return sp

def persist(sp):
	try:
		if sp.state < INITIATED:
			return 'ERROR'
		user_dir = path.join(cacheBasePath, sp.basic_details['id'])
		if(not path.exists(user_dir)):
			os.mkdir(user_dir)
		ncacheFilePath = path.join(user_dir, str(sp.state) + '.dat')
		with open(ncacheFilePath, 'w') as f:
			 pickle.dump(sp, f)
	except Exception as e:
		print "Error persisting SP.", e, sp

def loadSP(datFile):
	print 'loading ' + datFile
	with open(datFile,'r') as f:
		sp = pickle.load(f)
	return sp

def warmCache():
	for pId in os.listdir(cacheBasePath):
		saveToCache(pId, loadLatestSP(pId))

warmCache()
	

