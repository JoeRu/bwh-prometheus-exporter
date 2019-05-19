import os
if not os.path.exists('darknet'):
	os.system('git clone https://github.com/AlexeyAB/darknet.git')
	os.chdir('darknet')
	os.system("sed -i 's/LIBSO=0/LIBSO=1/g' Makefile")
	os.system('make')
	os.system('cp libdarknet.so ..')

