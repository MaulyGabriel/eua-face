# -*- coding: utf-8 -*-
import face_recognition as fr 
import glob
import numpy as np 
import os

from time import time


def split_string(string, char):

	data = list(string.split(char))

	return data


def train():

	print('Train init ...')

	init = time()

	faces = []
	codes = []
	names = []

	for file in glob.glob(os.path.join("/home/pi/Alice/imagens", "*.jpg")):

		image = fr.load_image_file(file)
		unknown_face = fr.face_encodings(image)

		if len(unknown_face) > 0:

			faces.append(fr.face_encodings(image)[0])
			data = split_string(str(file), '/')
			data = split_string(str(data[5]), '.')
			codes.append(data[0])
			names.append(data[1])

			print(data[1], 'success')

		else:
			print(file, ' error')

	np.save('/home/pi/Alice/modelo/imagens.npy',faces)
	np.save('/home/pi/Alice/modelo/codes.npy',codes)
	np.save('/home/pi/Alice/modelo/names.npy',names)

	print('train end', time() - init)


def train_pc():

	print('Train init ...')

	faces = []
	codes = []
	names = []

	init = time()

	for file in glob.glob(os.path.join("imagens", "*jpg")):

		image = fr.load_image_file(file)
		not_face = fr.face_encodings(image)

		if len(not_face) > 0:

			faces.append(fr.face_encodings(image)[0])
			data = split_string(str(file), '/')
			data = split_string(data[1], '.')

			codes.append(data[0])
			names.append(data[1])

			print(data[1], ": success")

		else:
			print(file, ': error')

	np.save('modelo/imagens.npy', faces)
	np.save('modelo/codes.npy', codes)
	np.save('modelo/names.npy', names)

	print('Train end: ', time() - init)


train_pc()


