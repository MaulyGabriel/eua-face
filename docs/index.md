### Projeto

Reconhecimento facial: identificação do operador presente no equipamento.

Desenvolvedores: 

Gabriel Mauly | gabriel.mauly@solinftec.com.br 

Rene Gonzalez | rene.gonzalez@solinftec.com.br

### Arquitetura
    
    environment.yml  # Dependências do projeto
    mkdocs.yml       # Arquivo de configuração.
    docs/
        index.md     # Página da documentação.    
    images/          # Faces a serem treinadas e reconhecidas
    models/          # contém os modelos treinados
        codes.npy    
        imagens.npy  
        names.npy     
    Operador.py      # Algoritmo principal, realiza o reconhecimento e comunicação serial
    Treinamento.py   # Realiza o treinamento das faces

### Anaconda

Para usuários anaconda, abra o terminal na pasta do projeto e utilize o seguinte comando para instalar as dependências:

* conda env create -f environment.yml

### PIP


Para usuários pip, abra o terminal na pasta do projeto e utilize o seguinte comando para instalar as dependências:

* pip install -r rec-facial.txt



### Comandos

Para executar o treinamento de novas faces utilize:

* python Treinamento.py 

<b>obs:</b> é necessário editar o arquivo Treinamento.py, adicionando a última linha qual plataforma 
de treinamento deseja utilizar train() para treinar diretamente no raspbery  ou train_pc() para treinar
no seu pc.

Para rodar o reconhecimento facial utilize:

* python Operador.py  
    
### Codificação

Explicação das classes implementadas

#### Class Treinamento.py

Bibliotecas:
   
    import face_recognition as fr   
    import glob
    import numpy as np 
    import os
    from time import time

Funções:

<b>split_string()</b>    
       
Converte o valor de uma string em uma lista de acordo com o critério de separação passado como parâmetro.
    
    split_string(value, char)
        value: (string) valor a ser convertido em lista
        char:  (string) critério de separação
    
    Exemplo:
    
    >> data = '10.gabriel.jpg'
    
    >> value = split_string(value=data, char='.')
    
    >> print(value)
    
    >> ['10', 'gabriel', 'jpg]
        
<b>train()</b>
    
Realiza o treinamento das faces no dispositivo (atualmente raspberry Pi), não é necessário passar nenhum
parâmetro, pois o mesmo realiza a leitura das imagens e gera os modelos treinados.

<b>train_pc()</b>
    
Realiza o treinamento das faces no desktop, a diferença está na maneira que o SO local trata o sistema
de diretórios.
   
#### Class Operador.py


Bibliotecas:
   
    from __future__ import print_function
    from imutils.video import WebcamVideoStream
    from imutils.video import FPS
    import argparse
    import imutils
    import cv2
    import dlib
    import face_recognition as fr
    import multiprocessing
    import numpy as np
    import os
    import serial
    import shutil
    import _thread as tr  
    import time
    from Treinamento import split_string, train

Funções:

<b>check_sum()</b>
    
Gera o check sum da mensagem (dígito que valida a integridade da informação)
    
    check_sum(hexadecimal):
        hexadecimal: (string) mensagem (informação) que precisa do dígito validador
    
    Exemplo:
        
    >> mensagem = '$PNEUD,G,0,1,'
        
    >> mensagem = check_sum(hexadecimal=mensagem)
        
    >> print(mensagem)
        
    >> 28
        
<b>init_board()</b>
    
Responsável por iniciar a comunicação serial com o bordo, não é necessário passar nenhum parêmtro, tem como
retorno a conexão estabelecida.

<b>identifier_face()</b>
    
Responsável por identificar um rosto para o cadastro automático, retorna a face reconhecida para treinamento.
    
    identifier_face(mean, tempo, camera, fps):
        mean:   (float) Média de confiança na identificação de uma face
        tempo:  (int) Tempo máximo para realizar a identificação da face
        camera: (object) Câmera responsável por ler os frames
        fps:    (object) Atualiza o fps do frame  
        
<b>wait_ok()</b>

Responsável por aguardar a confirmação de recebimento do bordo.
    
    wait_ok(message, tempo):
        message: (string) mensagem a ser enviada para o bordo
        tempo: (int) tempo máximo de espera para receber a confirmação

<b>send_message()</b>

Responsável por enviar mensagem para o bordo pela porta serial
    
    send_message(board, message, tempo):
        
        board: (object) Objeto com a conexão serial
        message: (string) mensagem a ser enviada
        tempo: (int) caso tenha que aguardar confirmação, tempo máximo de espera


<b>load_models()</b>
    
Responsável por carregar os modelos treinados.

<b>alter_turn()</b>
    
Responsável em definir o tempo de espera para a troca de turno.
    
    alter_turn(timeout):
        timeout: (int) tempo de espera.

<b>read_serial()</b>

Responsável por realizar a leitura das informações na porta serial
    
    read_serial(board, flags, conn):
        
        board: (object) Conexão com a porta serial
        flags: (object) Variável de comunicação entre processos
        conn:  (object) Comunicação entre processos

<b>recognition()</b>

Responsável por realizar o reconhecimento facial
    
    recognition(board, flags, conn):
        
        board: (object) Conexão com a porta serial
        flags: (object) Variável de comunicação entre processos
        conn:  (object) Comunicação entre processos

