# -*- coding: utf-8 -*-
# -*- encoding: utf-8
"""
	Reconhecimento facial
		
		Este projeto tem como objetivo principal reconhecer a face do operador e estabelecer uma comunicação com o
		MAG-100, efetuando o cadastro do operador e o reconhecimento do mesmo em troca de turno, liberação do equipamento...
		
		Utiliza-se as seguintes bibliotecas (na ordem da importação):
		opencv, dlib, face_recognition, glob, multiprocessing, numpy, os, pyserial, shutil, threading, thread, time  e treinamento
"""
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import dlib
import face_recognition as fr
import glob
import multiprocessing
import numpy as np
import os
import serial
import shutil
import threading as th
import _thread as tr  # mudar para _thread
import time
from Treinamento import GeraListaDeString, Treinamento

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="ID da camera que deseja realizar o reconhecimento", default=0)
args = vars(ap.parse_args())

# configuracao dos parametors da porta serial
porta = '/dev/ttyUSB0'  # '/dev/ttyAMA0'
baudrate = 9600
timeout = 1
camera = 0


def CheckSum(hexadecimal):
    """
        Responsável pela validação do hexadecimal enviado
        na troca de informações entre o Rasp e MAG-100.

        Args:
            hexadecimal: string a ser gerado o hexadecimal
    """
    verificador = 0

    for char in str(hexadecimal):
        verificador = verificador ^ ord(char)

    var = ''

    retorno = hex(verificador)

    tamanho = len(retorno)

    if (tamanho == 3):
        var = '0' + retorno[2]
    elif (tamanho == 4):
        var = retorno[2:4]
    else:
        print("[ERRO - NAO FOI POSSIVEL GERAR O CHECKSUM]")

    return var.upper()


def Bordo():
    """
        Responsável pela comunicação da porta serial

        Return:
            retorna o objeto bordo, contém a conexao com a
            porta serial
    """
    bordo = serial.Serial(porta, baudrate=baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                          bytesize=serial.EIGHTBITS, timeout=timeout)

    return bordo


def DetectaRostoCadastro(umbral, tempo,vs,fps):
    """
        Responsável por reconhecer a face na imagem de cadastro
        de um novo operador, utiliza o classificador da blibioteca DLIB

        Args:
            umbral: int, com qual confianca desejo identificar a face
            tempo: int, tempo limite para identificar a face
        Return:
            retorna o frame capturado
    """
    frame = np.array([])

    facesDetectadas = ''

    detector = dlib.get_frontal_face_detector()

    i = 0
    while len(facesDetectadas) < 1:
        i += 1
        frame = vs.read()
        facesDetectadas, confianca, idx = detector.run(frame, 0, umbral)

        if i == tempo:
            frame = np.array([])
            break
        print("CADASTRO REALIZADO:", len(facesDetectadas))
        fps.update()
    return frame



def AguardandoOk(mensagem, tempo):
    """
        Responsável por aguardar o $POK do bordo

        Args:
            mensagem: string a ser analisada se aguarda ou não
            tempo: int , tempo limite para aguardar
    """
    flag = 0
    while tempo > 1 and flag == 0:
        if bordo.inWaiting() > 0:
            msg = bordo.readline().decode("utf-8", "replace")
            if msg[:4] == "$POK":
                flag = 1
                print('[ENCONTREI O $POK]')
                break
            else:
                bordo.write(mensagem.encode())
            tempo -= 1
        else:
            tempo -= 1
            time.sleep(0.5)


def EnviarMensagem(bordo, mensagem, tempo):
    """
        Responsável por enviar mensagens ao bordo

        Args:
            bordo: conexao com a porta serial
            mensagem: string, mensagem a ser enviada
            tempo: int, tempo limite para envio
    """
    bordo.write(mensagem.encode())
    print('[ALICE] _ ', mensagem.upper())
    if mensagem[6] == ',':
        flags[0] = 0
        time.sleep(0.5)
        AguardandoOk(mensagem, tempo)
        flags[0] = 1



def CarregaNovoModelo():
    """
        Responsável por carregar os novos modelos treinados

        Return:
            retorna os modelos atualizados
    """
    codigos = np.load('/home/pi/Alice/modelo/codigos.npy')
    nomes = np.load('/home/pi/Alice/modelo/nomes.npy')
    imagens = np.load('/home/pi/Alice/modelo/imagens.npy')

    return codigos, nomes, imagens


def Timer(trName, timeout):
    """
        Responsável por aguardar a troca de turno dos
        operadores

        Args:
            trName: string, nome do procesos
            tempo: int, tempo para a troca de turno
    """
    time.sleep(timeout)
    flags[4] = 1
    flags[3] = 0


def PortaSerial(trName, bordo, flags, conn):
    """
        Responsável pelo atendimento das solicitaçes do
        bordo

        Args:
            trName: string, nome do serviço
            bordo: obj, conexao com a porta serial
            flags: array de flags controladoras de ações
            conn: obj, contem as informações de um novo do operador a ser cadastrado
    """
    print(trName)

    while True:
        pass

        while flags[0]:

            if (bordo.inWaiting() > 0):

                mensagem = bordo.readline().decode("utf-8", "replace")

                if mensagem[:8] == '$PNEUL,C':

                    EnviarMensagem(bordo, '$PNEUDOK,46\r\n', 1)
                    
                    idx = mensagem.find('*')
                    if idx != -1:

                        if CheckSum(mensagem[:idx]) == mensagem[idx + 1:idx + 3]:

                            if (mensagem[9] == '0'):
                                """
                                    Caiu no cadastro do operador
                                """
                                count = 0;

                                flags[1] = 0
                                flags[2] = 1

                                
                                conn.send(mensagem)
                                print("[BORDO]", mensagem)

                                
                            
                            elif (mensagem[9] == '1'):
                                """

                                    Caiu na troca de turno
                                """
                                flags[1] = 0
                                flags[3] = 1

                            else:
                                pass


def Reconhecimento(trName, bordo, flags, conn):
    """
        Responsável pelo reconhecimento dos operadores e
        cadastrado

        Args:
            trName: string, nome do serviço
            bordo: obj, conexao com a porta serial
            flags: array de flags controladoras de ações
            conn: obj, contem as informações de um novo do operador a ser cadastrado
    """
    print(trName)

    # controla ultimo operador
    oldOperador = 0
    trocaOperador = 0

    x = 0
    n = 0

    codigos, nomes, imagens = CarregaNovoModelo()

    # inicializando a camera
    vs = WebcamVideoStream(src=camera).start()
    fps = FPS().start()

    while True:

        if flags[3] and flags[4]:
            """
                Troca de Turno
            """
            EnviarMensagem(bordo, '$PNEUDOK,*46', 1)
            trocaOperador = oldOperador
            oldOperador = 0
            tr.start_new_thread(Timer, ('Timer', 180,))
            flags[4] = 0
            flags[1] = 1

        if flags[2]:
            """
                Cadastro de um novo operador
            """
                     
            listaDados = conn.recv()            

            frame = DetectaRostoCadastro(umbral=1.5, tempo=25, vs=vs,fps=fps)

            if frame.any():

                codigos = list(np.load('/home/pi/Alice/modelo/codigos.npy'))
                nomes = list(np.load('/home/pi/Alice/modelo/nomes.npy'))
                imagens = list(np.load('/home/pi/Alice/modelo/imagens.npy'))
                
                listaDados = GeraListaDeString(listaDados, ',')

                codigo = listaDados[3]

                foto = imutils.resize(frame,width=480)

                if codigo in codigos:
                    """
                        Se já existe o operador cadastrado verifica se há imagem cadastrada
                        move para o diretorio "olds" e atualiza a foto do operador, senão
                        efetua o cadastro de um novo operador normalmente
                    """
                    idx = codigos.index(codigo)
                    nome = nomes[idx]
                    if os.path.isfile('/home/pi/Alice/imagens/' + codigo + '.' + nome + '.jpg'):
                        shutil.move('/home/pi/Alice/imagens/' + codigo + '.' + nome + '.jpg',
                                    '/home/pi/Alice/imagens/olds/' + codigo + '.' + nome + '.' + time.strftime(
                                        "%Y%m%d%H%M") + '.jpg')

                cv2.imwrite('/home/pi/Alice/imagens/' + codigo + '.' + listaDados[4] + '.jpg', foto)
                hexadecimal = '$PNEUD,C,0,' + codigo + ',' + listaDados[4] + ',*' + CheckSum(
                    '$PNEUD,C,0,' + codigo + ',' + listaDados[4] + ',') + '\r\n'


                EnviarMensagem(bordo, hexadecimal, 10)

                train = multiprocessing.Process(target=Treinamento())
                train.start()
                train.join()

                print('[TREINAMENTO REALIZADO]')

                codigos, nomes, imagens = CarregaNovoModelo()

            
            else:
                EnviarMensagem(bordo, '$PNEUD,C,0,-1,*01\r\n', 10)

            
            flags[1] = 1
            flags[2] = 0


        while flags[1]:
            """
                Reconhecimento Facial
            """
            cods_operadores  = []
            names_operadores = []


            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            rgb_frame = frame[:, :, ::-1]

            face_cordenadas = fr.face_locations(rgb_frame)
            face_codificacoes = fr.face_encodings(rgb_frame, face_cordenadas)

            qtd_faces = len(face_cordenadas)

            if qtd_faces != 0:

                for (topo, direita, baixo, esquerda), face_codificacoes in zip(face_cordenadas, face_codificacoes):

                    comparacao = fr.compare_faces(imagens, face_codificacoes, tolerance=0.6)

                    if True in comparacao:
                        operador_encontrado = comparacao.index(True)

                        cods_operadores.append(codigos[operador_encontrado])

                        names_operadores.append(nomes[operador_encontrado])

                cods_operadores = list(set(cods_operadores))
                names_operadores = list(set(names_operadores))
                faces_desconhecidas = qtd_faces - len(cods_operadores)

                if oldOperador == 0 and flags[3]:

                    if trocaOperador in cods_operadores:
                        idx = cods_operadores.index(trocaOperador)
                        del cods_operadores[idx]
                        del names_operadores[idx]

                if oldOperador in cods_operadores:
                    x = 0  # nao conhece a pessoa
                    n = 0  # nao detecta a pessoa
                    #print('[R. MESMO OPERADOR]')
                else:

                    if len(cods_operadores) > 0:
                        x = 0
                        n = 0
                        cod_autorizado = cods_operadores[0]
                        nome_autorizdo = names_operadores[0]
                        hexadecimal = '$PNEUD,C,1,' + str(cod_autorizado) + ',' + str(nome_autorizdo) + ',*' + CheckSum(
                            '$PNEUD,C,1,' + str(cod_autorizado) + ',' + str(nome_autorizdo) + ',') + '\r\n'
                        EnviarMensagem(bordo, hexadecimal, 10)
                        oldOperador = cod_autorizado

                    else:
                        n = 0
                        if x == 20:
                            x = 0
                        else:
                            x += 1

            else:
                x = 0
                if n == 20:
                    n = 0
                else:
                    n += 1
        fps.update()

if __name__ == '__main__':
    """
        Iniciando a aplicação
            bordo: obj, contém a conexão com a porta serial
            flags: Bandeiras que sinalizam as ações a serem executadas [Ouvinte,Reconhecimento,Cadastro,TrocaDeTurno,AguardaTrocaDeTurno]
            recebe,envia: agrs a serem compartilhados entre os processos de reconhecimento  e recebimento de msg
    """
    bordo = Bordo()
    recebe, envia = multiprocessing.Pipe()
    flags = multiprocessing.Array('i', [1, 1, 0, 0, 1])

    PortaSerial = multiprocessing.Process(target=PortaSerial, args=('Bordo', bordo, flags, envia,))
    Reconhecimento = multiprocessing.Process(target=Reconhecimento, args=('Reconhecimento', bordo, flags, recebe,))

    PortaSerial.start()
    Reconhecimento.start()

    PortaSerial.join()
    Reconhecimento.join()
