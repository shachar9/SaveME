import math
import pickle
import numpy as np
import cv2
import os.path as path
import scipy.spatial.distance as distance

crop = lambda img,x,y,w,h: np.array([p[x:x+h] for p in img[y:y+w]])

doCoordsFilePath = lambda p: path.join(path.dirname(p), path.basename(path.splitext(p)[0]), path.basename(path.splitext(p)[0]) + '.faces.coords')

doImageFilePath = lambda p, ext: path.join(path.dirname(p), path.basename(path.splitext(p)[0]), path.basename(path.splitext(p)[0]) + '.' + ext +'.jpg')

def show(img):
	cv2.imshow('Image', img)
	cv2.waitKey(5000)

def recognizeFaces(image):
	faceCascade = cv2.CascadeClassifier(cascPath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
	return faces

def saveImage(imagePath, image):
	return cv2.imwrite(imagePath, image)

def saveFace(imagePath, face):
	with open(doCoordsFilePath(imagePath),'w') as f:
	    pickle.dump(face, f)

def saveSubImage(imagePath, image, ext='face'):
	cv2.imwrite(doImageFilePath(imagePath, ext), image)

def loadFace(imagePath):
	with open(doCoordsFilePath(imagePath),'r') as f:
	    face = pickle.load(f)
	return face;

def loadSubImage(imagePath, ext='face'):
	return cv2.imread(doImageFilePath(imagePath, ext))

def loadFaceFromImage(imagePath):
	face = loadFace(imagePath)
	image = cv2.imread(imagePath)
	return crop(image, *face)

basePath = path.dirname(path.abspath(__file__))
cascPath = path.join(basePath, 'resources/haarcascade_frontalface_default.xml')

def drawRectangles(image, faces):
	copy = image.copy()
	for (x, y, w, h) in faces:
    		cv2.rectangle(copy, (x,y), (x+w, y+h), (0, 255, 0), 2)
	return copy

def scaleGauss(Mg):
	gmin = min(Mg.min(0))
	gmax = max(Mg.max(0))
	lin_scale = np.vectorize(lambda x: 1.0*((x-gmin)/(gmax-gmin)))
	return lin_scale(Mg)

def getGaussGenerator(sigma=100):
	return lambda w,h: cv2.getGaussianKernel(w,sigma) * cv2.getGaussianKernel(h,sigma).transpose()

def getGaussMaskGenerator(gaussGenerator):
	return lambda w,h: scaleGauss(gaussGenerator(w,h))

doRgb = lambda mat: np.array([[[x,x,x] for x in row] for row in mat])

interp = lambda x,y,a: a*x + (1.0-a)*y

def mergeByAdditiveMask(src, dst, maskGenerator):
	(h, w) = dst.shape[:2]
	src = cv2.resize(src.copy(), (w,h))
	M = maskGenerator(w, h)
	return interp(src, dst, doRgb(M)).astype('uint8')
	
def pasteIn(src,dst,x,y,w,h):
	dst = dst.copy()
	for i in range(0,w):
		for j in range(0,h):
			dst[j+y][i+x] = src[j][i]
	return dst

pointInBox = lambda px,py,x,y,w,h: (px >= x) and (py >= y) and (px <= x + w) and (py <= y + h)

getCenter = lambda x, y, w, h: ((float(w) / 2.0) + x, (float(h) / 2.0) + y)

def findRightFace(faces, h, w, relx, rely):
	pos = (float(w) * (relx / 100.0), float(h) * (rely / 100.0))
	sfaces = [f for f in faces if pointInBox(pos[0], pos[1], *f)]
	sfaces.sort(key=lambda f: distance.euclidean(pos, getCenter(*f)))
	return sfaces[0] if len(sfaces) > 0 else None

def cropFaceFromImageDetails(photo_det, imageFile):
	try:
		if imageFile == None: return None
		image = cv2.imread(imageFile)
		if image == None: return None
		faces = recognizeFaces(image)
		face = findRightFace(faces, h=photo_det['height'], w=photo_det['width'], relx=photo_det['x'], rely=photo_det['y'])
		return crop(image, *face) if face != None else None
	except:
		return None

###
#scene = cv2.imread(scenePath)
#faces = recognizeFaces(scene)
#show(drawRectangles(scene, faces))
#saveFace(scenePath, face)
#faceImg = loadFaceFromImage(scenePath)
#saveSubImage(scenePath, faceImg)

#import saveme
#sp = saveme.loadSP('/home/shachar/git/SaveME/cache/?')
#user_faces_map = { i : img for i, img in enumerate(self.user_faces_images) }
#image_helper.sortByHistogram(faceImg, user_faces_map)[:3]
#v = placeFaceInScene(scenePath, self.user_faces_images[?])
###

#image = cv2.imread(imagePath)
#(h, w) = image.shape[:2]
#faces = recognizeFaces(image)
#face = findRightFace(faces, h, w, x?, y?)
#userFaceImg = loadFacesImages(imagePath)[?]
#sceneFace = loadFaces(scenePath)[?]
#merged = mergeByAdditiveMask(userFaceImg, sceneFaceImg, getGaussMaskGenerator(getGaussGenerator()))
#nscene = pasteIn(merged, scene, *sceneFace)

#user_images = [retrieveImage(p) for p in photos_sources]
#user_images = [im for im in user_images if im != None]

#http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_pyramids/py_pyramids.html#additional-resources
def getGaussianPyramid(img, lvls):
	G = img.copy()
	gpyramid = [G]
	for i in xrange(lvls):
		G = cv2.pyrDown(G)
		gpyramid.append(G)
	return gpyramid

def getLaplacianPyramid(gpyramid, lvl):
	lpyramid = [gpyramid[lvl]]
	for i in xrange(lvl,0,-1):
		GE = cv2.pyrUp(gpyramid[i])
		L = cv2.subtract(gpyramid[i-1],GE)
		lpyramid.append(L)
	return lpyramid

thresMask = lambda M: doRgb(np.round(cv2.split(M)[0] / 255.0) * 255.0)
masksize = lambda M, i: (lambda ns: thresMask(cv2.resize(M.copy(), (ns, ns))))(int(2 ** (math.log(M.shape[1], 2) - i)))

def laplacianPyramidBlending(A, B, mask, lvl, mergeFunc):
	# generate Gaussian pyramid for A
	gpA = getGaussianPyramid(A, lvl + 1)

	# generate Gaussian pyramid for B
	gpB = getGaussianPyramid(B, lvl + 1)

	# generate Laplacian Pyramid for A
	lpA = getLaplacianPyramid(gpA, lvl)

	# generate Laplacian Pyramid for B
	lpB = getLaplacianPyramid(gpB, lvl)

	# generate Gaussian pyramid for mask
	gpM = [masksize(mask, i) for i in range(lvl, -1, -1)]
	
	# Now add left and right halves of images in each level
	LS = [mergeFunc(la, lb, lm) for la,lb,lm in zip(lpA,lpB,gpM)]

	# now reconstruct
	ls_ = LS[0]
	for i in xrange(1,lvl + 1):
		ls_ = cv2.pyrUp(ls_)
		ls_ = cv2.add(ls_, LS[i])
	return ls_

bgrHistogram = lambda img: cv2.calcHist([img], [0, 1, 2], None, [32, 32, 32], [0, 256, 0, 256, 0, 256])

toReverse = lambda method: True if method in (cv2.cv.CV_COMP_CORREL, cv2.cv.CV_COMP_INTERSECT) else False

def sortByHistogram(sceneFaceImg, user_images_dict, method=cv2.cv.CV_COMP_CORREL):
	scene_hist = cv2.normalize(bgrHistogram(sceneFaceImg)).flatten()
	user_hists = { name : cv2.normalize(bgrHistogram(user_img)).flatten() for name, user_img in user_images_dict.items() }
	user_hists_comp = { name : cv2.compareHist(scene_hist, user_hist, method) for name, user_hist in user_hists.items() }
	return sorted(user_hists_comp.items(), key=lambda (k,v): v, reverse=toReverse(method))

def pyrMerge(scene, userFaceImg, sceneFace, maskFaceImg, sceneFaceImg=None, psize=512, lvl=3):
	sceneFaceImg = crop(scene, *sceneFace) if sceneFaceImg == None else sceneFaceImg
    	A = cv2.resize(userFaceImg.copy(), (psize,psize))
    	B = cv2.resize(sceneFaceImg.copy(), (psize, psize))
    	M = thresMask(cv2.resize(maskFaceImg.copy(), (psize, psize)))
    	l = laplacianPyramidBlending(A, B, M, lvl, lambda la,lb,lm: interp(la, lb, lm / 255.0).astype('uint8'))
    	merged = cv2.resize(l, tuple(sceneFaceImg.shape[:2]))
    	return pasteIn(merged, scene, *sceneFace)

def placeFaceInScene(scenePath, userFaceImg, sceneFaceImg=None, psize=512, lvl=3):
	scene = cv2.imread(scenePath)
	sceneFace = loadFace(scenePath)
	maskImg = loadSubImage(scenePath, 'mask')
	maskFaceImg = crop(maskImg, *sceneFace)
	return pyrMerge(scene, userFaceImg, sceneFace, maskFaceImg, sceneFaceImg, psize, lvl)



