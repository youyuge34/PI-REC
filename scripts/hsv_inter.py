import cv2 as cv 

start = '138/138_AB_blur.png'
img_start = cv.imread(start)
img_start = cv.cvtColor(img_start, cv.COLOR_BGR2HSV)
h, s, v = cv.split(img_start)
ran = 60
for x in range(ran):
	new_h = h + 255 // ran * x
	img_end = cv.merge([new_h, s, v])
	img_end = cv.cvtColor(img_end, cv.COLOR_HSV2BGR)
	path = '{}/img_{}_h_{}_inter.png'.format(start.split('/')[0],start.split('/')[-1].split('.')[0],x)
	cv.imwrite(path, img_end)
	print('img_inter is saved to', path)
	

