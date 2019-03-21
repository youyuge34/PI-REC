import cv2 as cv 
import numpy as np 

start = '7/blue.png'
end = '7/red.png'
img_start = cv.imread(start)
img_end = cv.imread(end)
ran = 10

for x in range(1,ran):
	scale = x / float(ran)
	cha = (img_end.astype(np.int)-img_start.astype(np.int))
	img_inter = img_start + cha * scale

	path = '{}/img_{}_{}_inter_{}.png'.format(start.split('/')[0],start.split('/')[-1].split('.')[0],end.split('/')[-1].split('.')[0],scale)
	cv.imwrite(path, img_inter)
	print('img_inter is saved to', path)

