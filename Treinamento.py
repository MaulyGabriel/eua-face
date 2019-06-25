# -*- coding: utf-8 -*-

"""
	Esse codigo e responsavel por realizar o treinamento  dos modelos  com as novas fotos cadastradas
"""
import cv2
import face_recognition as fr 
import glob
import numpy as np 
import os
import time


def GeraListaDeString(string, caractere):
	"""
		Responsavel por quebrar uma string em lista a partir de um caractere

		Args:
			string: texto a ser quebrado
			caractere: simbolo a ser usado como parametro de separacao do char
		Return:
			Lista da string
	"""
	lista = list(string.split(caractere))

	return lista

def Treinamento():
	"""
		Responsavel por ler as imagens do diretorio e atualizar os modelos para 
		o reconhecimento do operador
	"""
	encodings = []
	codigos   = []
	nomes     = []

	for imagem in glob.glob(os.path.join("/home/pi/Alice/imagens","*.jpg")):

		image = fr.load_image_file(imagem)
		unknown_face = fr.face_encodings(image)

		if(len(unknown_face)>0):

			encodings.append(fr.face_encodings(image)[0])
			lista = GeraListaDeString(str(imagem), '/')
			print(lista)
			lista = GeraListaDeString(str(lista[5]), '.')
			print(lista)
			codigos.append(lista[0])
			nomes.append(lista[1])
		else:
			print('Face nao encontrada', image)



	np.save('/home/pi/Alice/modelo/imagens.npy',encodings)
	np.save('/home/pi/Alice/modelo/codigos.npy',codigos)
	np.save('/home/pi/Alice/modelo/nomes.npy',nomes)
	print('Treinamento finalizadao')


Treinamento()
