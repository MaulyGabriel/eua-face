# -*- coding: utf-8 -*-
# -*- encoding: utf-8

from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import imutils
import cv2
import dlib
import face_recognition as fr
import multiprocessing as mp
import numpy as np
import os
import serial
import shutil
import _thread as tr
import time
from Treinamento import split_string, train


def check_sum(hexadecimal):
    validator = 0

    for char in str(hexadecimal):
        validator = validator ^ ord(char)

    var = ''

    value = hex(validator)

    if len(value) == 3:
        var = '0' + value[2]
    elif len(value) == 4:
        var = value[2:4]
    else:
        print("error in check sum")

    return var.upper()


def init_board():
    try:

        os.system('sudo chmod -R 777 /dev/ttyUSB0')

        port = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE,
                             stopbits=serial.STOPBITS_ONE,
                             bytesize=serial.EIGHTBITS, timeout=1)

        return port

    except serial.SerialException:
        print('Verify your permission')

        return None


def identifier_face(mean, tempo, camera, fps):
    frame = np.array([])

    face_found = ''

    detector = dlib.get_frontal_face_detector()

    i = 0

    while len(face_found) < 1:
        i += 1
        frame = camera.read()
        face_found, confidence, idx = detector.run(frame, 0, mean)

        if i == tempo:
            frame = np.array([])
            break

        print("operator create with success :", len(face_found))

        fps.update()

    return frame


def wait_ok(message, tempo):
    flag = 0

    while tempo > 1 and flag == 0:

        if board.inWaiting() > 0:
            msg = board.readline().decode("utf-8", "replace")
            if msg[:4] == "$POK":
                flag = 1
                print('found ok')
                break
            else:
                board.write(message.encode())
            tempo -= 1
        else:
            tempo -= 1
            time.sleep(0.5)


def send_message(board, message, tempo):
    board.write(message.encode())

    if message[6] == ',':
        flags[0] = 0
        time.sleep(0.5)
        wait_ok(message, tempo)
        flags[0] = 1


def load_models():

    codes = np.load('/home/pi/Alice/models/codes.npy')
    names = np.load('/home/pi/Alice/models/names.npy')
    images = np.load('/home/pi/Alice/models/images.npy')

    return codes, names, images


def load_models_pc():

    codes = np.load('models/codes.npy')
    names = np.load('models/names.npy')
    images = np.load('models/images.npy')

    return codes, names, images


def alter_turn(timeout):
    time.sleep(timeout)
    flags[4] = 1
    flags[3] = 0


def read_serial(board, flags, conn):

    print('serial starting ...')

    while True:
        pass

        while flags[0]:

            if board.inWaiting() > 0:

                message = board.readline().decode("utf-8", "replace")

                if message[:8] == '$PNEUL,C':

                    send_message(board, '$PNEUDOK,46\r\n', 1)

                    idx = message.find('*')

                    if idx != -1:

                        if check_sum(message[:idx]) == message[idx + 1:idx + 3]:

                            if message[9] == '0':

                                flags[1] = 0
                                flags[2] = 1

                                conn.send(message)
                            elif message[9] == '1':

                                flags[1] = 0
                                flags[3] = 1

                            else:
                                pass


def recognition(board, flags, conn):

    print('recognition starting ....')

    old_operator = 0
    turn_operator = 0

    not_identified = 0
    not_detected = 0

    codes, names, images = load_models()

    vs = WebcamVideoStream(src=0).start()
    fps = FPS().start()

    while True:

        if flags[3] and flags[4]:
            send_message(board, '$PNEUDOK,*46', 1)
            turn_operator = old_operator
            old_operator = 0
            tr.start_new_thread(alter_turn, (180,))
            flags[4] = 0
            flags[1] = 1

        if flags[2]:

            list_data = conn.recv()

            frame = identifier_face(mean=1.5, tempo=25, camera=vs, fps=fps)

            if frame.any():

                codes = list(np.load('/home/pi/Alice/models/codigos.npy'))
                names = list(np.load('/home/pi/Alice/models/nomes.npy'))

                list_data = split_string(list_data, ',')

                code = list_data[3]

                photo = imutils.resize(frame, width=480)

                if code in codes:

                    idx = codes.index(code)
                    nome = names[idx]

                    if os.path.isfile('/home/pi/Alice/images/' + code + '.' + nome + '.jpg'):
                        shutil.move('/home/pi/Alice/images/' + code + '.' + nome + '.jpg',
                                    '/home/pi/Alice/images/olds/' + code + '.' + nome + '.' + time.strftime(
                                        "%Y%m%d%H%M") + '.jpg')

                cv2.imwrite('/home/pi/Alice/images/' + code + '.' + list_data[4] + '.jpg', photo)

                hexadecimal = '$PNEUD,C,0,' + code + ',' + list_data[4] + ',*' + check_sum(
                    '$PNEUD,C,0,' + code + ',' + list_data[4] + ',') + '\r\n'

                send_message(board, hexadecimal, 10)

                train_face = mp.Process(target=train())
                train_face.start()
                train_face.join()

                codes, names, images = load_models()

            else:
                send_message(board, '$PNEUD,C,0,-1,*01\r\n', 10)

            flags[1] = 1
            flags[2] = 0

        while flags[1]:

            codes_operators = []
            names_operators = []

            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            rgb_frame = frame[:, :, ::-1]

            face_coordinates = fr.face_locations(rgb_frame)
            face_coded = fr.face_encodings(rgb_frame, face_coordinates)

            qtd_faces = len(face_coordinates)

            if qtd_faces != 0:

                for (topo, direita, baixo, esquerda), face_coded in zip(face_coordinates, face_coded):

                    face_result = fr.compare_faces(images, face_coded, tolerance=0.6)

                    if True in face_result:
                        found_operator = face_result.index(True)

                        codes_operators.append(codes[found_operator])

                        names_operators.append(names[found_operator])

                codes_operators = list(set(codes_operators))
                names_operators = list(set(names_operators))
                unknown_faces = qtd_faces - len(codes_operators)

                if old_operator == 0 and flags[3]:

                    if turn_operator in codes_operators:
                        idx = codes_operators.index(turn_operator)
                        del codes_operators[idx]
                        del names_operators[idx]

                if old_operator in codes_operators:
                    not_identified = 0
                    not_detected = 0
                else:

                    if len(codes_operators) > 0:

                        not_identified = 0
                        not_detected = 0

                        code_authorized = codes_operators[0]
                        name_authorized = names_operators[0]

                        hexadecimal = '$PNEUD,C,1,' + str(code_authorized) + ',' + str(name_authorized) + ',*' + \
                                      check_sum('$PNEUD,C,1,' + str(code_authorized) + ',' +
                                                str(name_authorized) + ',') + '\r\n'

                        send_message(board, hexadecimal, 10)

                        old_operator = code_authorized

                        print(name_authorized, ": was recognized")

                    else:
                        not_detected = 0

                        if not_identified == 20:
                            not_identified = 0
                        else:
                            not_identified += 1

            else:
                not_identified = 0

                if not_detected == 20:
                    not_detected = 0
                else:
                    not_detected += 1
        fps.update()


if __name__ == '__main__':

    board = init_board()

    receive, send = mp.Pipe()

    flags = mp.Array('i', [1, 1, 0, 0, 1])

    serial_process = mp.Process(target=read_serial, args=(board, flags, send,))
    recognition_process = mp.Process(target=recognition, args=(board, flags, receive,))

    serial_process.start()
    recognition_process.start()

    serial_process.join()
    recognition_process.join()
