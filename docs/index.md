### Projeto

Reconhecimento facial: identificação do operador presente no equipamento.

Desenvolvedor: Gabriel Mauly | gabriel.mauly@solinftec.com.br | (18) 98167-8570

### Comandos
* python Treinamento.py - Executa o treinamento do modelo.
* python Operador.py    - Inicia o reconhecimento e comunicação serial.


### Arquitetura
    
    environment.yml  # Dependências do projeto
    mkdocs.yml       # Arquivo de configuração.
    docs/
        index.md     # Página da documentação.    
    imagens/         # Faces a serem treinadas e reconhecidas
    modelo/          # contém os modelos treinados
        codes.npy    
        imagens.npy  
        names.npy     
    Operador.py      # Algoritmo principal, realiza o reconhecimento e comunicação serial
    Treinamento.py   # Realiza o treinamento das faces
    
### Codificação

Descrição dos algoritmos desenvolvidos


Class Treinamento.py
    
    
    split_string(value, char)
        value: string a ser separada em lista
        char: string, critério de separação
    
    train()
    
    train_pc()





