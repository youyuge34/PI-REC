import shutil
import os
flist = 'datasets/getchu/train.flist'
with open(flist) as f:
	files = f.readlines()
	total = len(files)
	for i,file in enumerate(files):
		if i % 500 ==0:
			print('now {:.2f}%'.format(i/total*100.))
		# print(file)
		file = file.strip()
		shutil.copyfile(file, os.path.join('datasets/getchu/split_train/',file.split('\\')[-1]))
