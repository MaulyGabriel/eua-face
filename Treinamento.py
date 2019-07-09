# -*- coding: utf-8 -*-
import face_recognition as fr 
import glob
import numpy as np 
import os


def split_string(string, char):

	data = list(string.split(char))

	return data


def train():

	encodings = []
	codes = []
	names = []

	for imagem in glob.glob(os.path.join("/home/pi/Alice/imagens", "*.jpg")):

		image = fr.load_image_file(imagem)
		unknown_face = fr.face_encodings(image)

		if len(unknown_face) > 0:

			encodings.append(fr.face_encodings(image)[0])
			print(split_string(str(imagem), '/'))
			lista = split_string(str(imagem), '/')
			print(lista)
			lista = split_string(str(lista[5]), '.')
			print(lista)
			codes.append(lista[0])
			names.append(lista[1])

		else:
			print('Face nao encontrada', image)

	np.save('/home/pi/Alice/modelo/imagens.npy',encodings)
	np.save('/home/pi/Alice/modelo/codes.npy',codes)
	np.save('/home/pi/Alice/modelo/names.npy',names)
	print('Treinamento finalizadao')

	print('Treinamento finalizadao')


train()

