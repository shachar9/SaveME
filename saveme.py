import pickle
import os.path as path
import os
import glob
import threading
import fb_helper
import image_helper
import sys
import logging
import ConfigParser
import random
from retrying import retry
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

(NEW, INITIATED, IMAGES_SOURCES_READY, FACES_DATA_READY, SCENES_CHOSEN, SCENES_GENERATED) = range(6)

LAST_STATE = SCENES_GENERATED

basePath = path.dirname(path.abspath(__file__))
scenesBasePath = path.join(basePath, 'resources/scenes')
cacheBasePath = path.join(basePath, 'cache')
viewBasePath = path.join(basePath, 'view')
storyBasePath = path.join(viewBasePath, 'story')

stepPerState = {
	INITIATED : lambda sp, token: sp.retrievePhotosLinks(token),
	IMAGES_SOURCES_READY : lambda sp, token: sp.retrievePhotosData(),
	FACES_DATA_READY : lambda sp, token: sp.chooseScenesParams(),
	SCENES_CHOSEN : lambda sp, token: sp.generateScenes(),
	SCENES_GENERATED : lambda sp, token: True
}

# Errors:
NO_IMAGES = "No photos, might be privilige problems."
NO_FACES = "Didn't find any good photos of you."

cfg = ConfigParser.ConfigParser()
cfg.read(path.join(basePath, 'config.ini'))

def getListConfig(section, option, typeFunc=lambda o: o):
	lst = cfg.get(section, option).strip().split(',')
	if len(lst) == 1 and lst[0] == '':
		return []
	else:
		return [typeFunc(o.strip()) for o in lst]

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
		user_files_details = [(p, fb_helper.retrieveImage(p)) for p in self.photos_sources[:50]]
		user_faces_images = [image_helper.cropFaceFromImageDetails(*im) for im in user_files_details]
		self.user_faces_images = [im for im in user_faces_images if im != None]
		if len(self.user_faces_images) == 0:
			raise Exception(NO_FACES)
		self.__setState(FACES_DATA_READY)

	def chooseScenesParams(self):
		user_faces_map = { i : img for i, img in enumerate(self.user_faces_images) }
		scenes_by_order = [cfg.get('Scenes',s) for s in cfg.options('Scenes')]
		self.scenes = { sname : self.__chooseImage(sname) for sname in scenes_by_order }
		scenes_faces = { s : image_helper.loadSubImage(path.join(scenesBasePath, self.scenes[s])) for s in scenes_by_order }
		sorted_by_hist = { s : image_helper.sortByHistogram(scenes_faces[s], user_faces_map) for s in self.scenes }
		self.scenes_params = [(s, sorted_by_hist[s][0][0]) for s in scenes_by_order]
		self.__setState(SCENES_CHOSEN)

	def __getOutputDir(self):
		user_dir = path.join(storyBasePath, self.basic_details['id'])
		if not path.exists(user_dir):
			os.mkdir(user_dir)
		# Delete exisitng files
		for f in os.listdir(user_dir):
			os.remove(path.join(user_dir, f))
		return user_dir;

	def __chooseImage(self, sname):
		 return random.sample(getListConfig('ScenesConfig',sname), 1)[0]

	def generateScenes(self):
		self.generated_scenes = [(s, image_helper.placeFaceInScene(path.join(scenesBasePath, self.scenes[s]), self.user_faces_images[u])) for s, u in self.scenes_params]
		odir = self.__getOutputDir()
		self.generated_images_paths = []
		for name, img in self.generated_scenes:
			impath = path.join(odir, name + '.jpg')
			image_helper.saveImage(impath, img)
			self.generated_images_paths.append({'id' :name, 'src': path.relpath(impath, viewBasePath)})
		if not cfg.getboolean('Performance', 'KeepIntermediateData'):
			self.__clearIntermediateData()
		self.__setState(SCENES_GENERATED)

	def __clearIntermediateData(self):
		self.user_faces_images = []
		self.scenes_params = []
		self.generated_scenes = []
	

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
		logging.error("Story start error: %s. %s", e, sp)
		return { 'status': getErrStatus(1) }
	pId = sp.getId()
	#latestSP = loadLatestSP(pId)
	latestSP = getFromCache(pId)
	if latestSP != None:
		sp = latestSP
	else:
		saveToCache(pId, sp)
	res = { 'status': sp.state }
	if sp.state == LAST_STATE:
		logging.info("Everythings baked for id %s", pId)
		res['images'] = sp.generated_images_paths
	elif not sp.running:
		logging.info("Start new thread for id %s", pId)
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
	logging.info("Running for step %d.", sp.state)
	try:
		sp.state = int(str(abs(sp.state))[0])
		result = stepPerState[sp.state](sp, fb_access_token)
	except Exception as e:
		sp.running = False
		sp.state = getErrStatus(e, sp.state)
		logging.error("Story phase error: %s. %s", e, sp)		
		return
	logging.info("Done %d. %s.", sp.state, sp)
	if sp.state in getListConfig('Performance','PersistInCache',lambda x: int(x)):
		persist(sp)
	if sp.state < LAST_STATE:
		runSP(sp, fb_access_token)
	else:
		logging.info("Finito running %s.", sp)
		sp.running = False

def getErrStatus(e, state):
	if e.message == NO_IMAGES:
		return -11
	elif e.message == NO_FACES:
		return -21
	return -1 * abs(state)

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
	logging.info("Loaded SP from cache %s.", user_id)
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
		logging.error("Error persisting SP. %s. %s", e, sp)

def loadSP(datFile):
	logging.info("Loading %s.", datFile)
	with open(datFile,'r') as f:
		sp = pickle.load(f)
	return sp

def warmCache():
	for pId in os.listdir(cacheBasePath):
		saveToCache(pId, loadLatestSP(pId))

if cfg.getboolean('Performance', 'WarmupCache'):
	warmCache()
	

