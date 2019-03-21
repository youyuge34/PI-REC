import os
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='path to the dataset')
parser.add_argument('--train', type=int, default=28, help='number of train in a iter')
parser.add_argument('--val', type=int, default=1, help='number of val in a iter')
parser.add_argument('--test', type=int, default=1, help='number of test in a iter')
parser.add_argument('--output', type=str, help='path to the three file lists')
args = parser.parse_args()

ext = {'.jpg', '.png'}
total = args.train + args.val + args.test
images_train = []
images_val = []
images_test = []

num = 1
for root, dirs, files in os.walk(args.path):
    print('loading ' + root)
    for file in files:
        if os.path.splitext(file)[1] in ext:
            path = os.path.join(root, file)
            if num % total > (args.val + args.test) or num % total == 0:
                images_train.append(path)
            elif num % total <= args.val and num % total > 0:
                images_val.append(path)
            else:
                images_test.append(path)
            num += 1

images_train.sort()
images_val.sort()
images_test.sort()

print('train number =', len(images_train))
print('val number =', len(images_val))
print('test number =', len(images_test))

if not os.path.exists(args.output):
    os.mkdir(args.output)
np.savetxt(os.path.join(args.output, 'train.flist'), images_train, fmt='%s')
np.savetxt(os.path.join(args.output, 'val.flist'), images_val, fmt='%s')
np.savetxt(os.path.join(args.output, 'test.flist'), images_test, fmt='%s')
