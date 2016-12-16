# Usando Hadoop com Docker

Este tutorial não abrange a instalação do Docker. Portanto, será assumido que o Docker já estaja instalado. 

### Imagem Docker

O primeiro vamos instalar a imagem com o hadoop configurado na máquina
```shell 
docker pull sequenceiq/hadoop-docker:2.7.1
```
Uma vez instalada, o seguinte comando deve ser executado 

```shell 
docker run --privileged=true -v /home/allyson/DockerTemp:/k -p 50070:50070 -p 8088:8088 -p 19888:19888 -p 9000:9000 -it sequenceiq/hadoop-docker:2.7.1 /etc/bootstrap.sh -bash

```
Quebrando o comando acima em partes: ```--privileged=true``` dá acesso extendido aos recursos da máquina anfitriã. 

```-v /home/allyson/DockerTemp:/k``` onde ```-v``` é a versão resumida do comando ```-volume``` que informa ao docker que haverá um compartilhamento da pasta ```/home/allyson/DockerTemp```, na máquina anfitriã com a ```/k``` da máquina hospedeira. 

Obs: não é necessário criar manualmente a parta ```/k``` na raíz da máquina hospedeira. Esse processo é feito automaticamente pelo docker. 

O próximo seguimento de comandos são os compartilhadores de portas. O comando ```-p porta_máquina_anfritriã:porta_máquina_hospedeira``` registra os serviços da máquina hospedeira na máquina anfritriã. Desse modo os recursos do Hadoop podem ser usados em ```localhost``` na máquina anfritriã, por exemplo. 

Para fim de testes, só algumas portas foram compartilhadas. Segue a lista de portas que o Hadoop utiliza: 
[Hadoop Portas](https://wikitech.wikimedia.org/wiki/Analytics/Cluster/Ports)

O próximo comando ```-it sequenceiq/hadoop-docker:2.7.1``` informa ao docker que a imagem ```sequenceiq/hadoop-docker:2.7.1``` será executada e modo ```interective terminal```, ou seja, você terá acesso ao terminal da mesma como se estivesse fazendo um acesso via SSH. 

O último comando ```/etc/bootstrap.sh -bash``` inicia os serviços necessários no container para que tudo funcione bem. Esse arquivo já faz parte da imagem. 

[carrgar uma imagem aqui de tudo funcionando]

#### Hadoop
O hadoop está organizado dentro da parta ```/usr/local/hadoop/```, o container registra esse caminho em uma variável de ambiente ```HADOOP_PREFIX```. Abra a pasta com o comando ```cd /usr/local/hadoop/bin``` e na pasta ```./hadoop```. Bem-vindo ao Hadoop ;p

#### Criando um Mapper e um Reducer com Python
Nesse exemplo será usado as entradas e saídas padrões de dados (stdin e stdout), Portanto, trataremos todas as entradas da aplicação Python com a classe ``sys```

##### Mapper.py
```python 
import sys 

def main(): 
	for line in sys.stdin: 
		if "CAFÉ" in line: 
			print line

if __name__ == '__main__':
	main()

```
Esse mapeador irá receber o fluxo de dados e verificar se há alguma sequência de caracteres que se relaciona com "CAFÉ". Caso verdade, a linha é 'printada' no console. 

##### Reducer.py
```python 
import sys

def main(): 
	for line in sys.stdin:
		print line[10:30]

if __name__ == '__main__':
	main()
```
O redutor respeita as mesmas regras de entrada e saída do mapeador. O escopo de um reducer é estruturar dos dados que foram previamente mapeados. Nesse exemplo todas as linhas que tem "CAFÉ" serão reduzidas em uma substring do caracter 10 ao 30. 

Para testar o mapeador e o redutor em um fluxo de dados basta usar o comando: 
```shell
cat /home/allyson/log_servidor_padaria.TXT | python /home/allyson/mapper.py | python /home/allyson/reducer.py

```

#### E no Hadoop?
As rotinas no Hadoop são mais complexas. Por esse motivo não entarei a fundo sobre a funcionalidade de cada comando a seguir, apenas em como fazer um streaming com uma lib especifica do Hadoop. 

Dentro da pasta compartilhada "DockerTemp", crie a seguinte estrutura de pastas: 
* data: para armazenar os dados brutos do servidor; 
* scripts: para armazenar nossos scripts Python. 

As modificações serão refletidas imadiatamente na pasta ```\k\``` na máquina hospedeira. Na pasta scripts crie o arquivos mapper.py e reducer.py com os códigos acima e um arquivo process.py com o código abaixo: 

```python 
import os, sys, subprocess as bash

#configuracoes de path dentro da maquina docker: 
HADOOP_PATH = os.environ['HADOOP_PREFIX'] + '/bin/'
HADOOP_LIB  = os.environ['HADOOP_PREFIX'] + '/share/hadoop/tools/lib/'

#path para o arquivo: 
file_path   = '/k/data/vivo.TXT'
file_name   = 'vivo.TXT'

b = bash.Popen(['%(HADOOP_PATH)shadoop' % locals(),
				'fs',
			    '-put',
			    file_path,
			    '/'])
b.communicate()

sys.stdout.flush()

print "Importando arquivos para o sistema de arquivos do Hadoop"


b = bash.Popen(['%(HADOOP_PATH)shadoop' % locals(),
				'jar',
				'%(HADOOP_LIB)s/hadoop-streaming-2.7.1.jar' % locals(), 
				'-files', 
				'/k/scripts/mapper.py,/k/scripts/reducer.py', 
				'-mapper', 
				'python mapper.py', 
				'-reducer', 
				'python reducer.py', 
				'-input', 
				'/'+file_name, 
				'-output', 
				'/output'
			   ])

b.communicate()
sys.stdout.flush()

print "Executando Mappers e Reducers"

b = bash.Popen(['python', 
				'/k/scripts/count.py', 
				'/output/part-00000'
			   ])

b.communicate()
sys.stdout.flush()

b = bash.Popen(['%(HADOOP_PATH)shadoop' % locals(), 'fs', '-rm', '-R', '/output'])
b.comunicate()
print "Deletando arquivos temporarios"
```

Também adicionaremos uma rotina para consumir o produto do reducer.py, no arquivo count.py, na pasta scripts: 

```python 

import sys
import os
import subprocess

HADOOP_PATH = os.environ['HADOOP_PREFIX'] + '/bin/'

filepath = sys.argv[1]

print(filepath)
cat = subprocess.Popen(["%(HADOOP_PATH)shadoop" % locals(), "fs", "-cat", filepath], stdout = subprocess.PIPE)

for line in cat.stdout: 
	print(line.upper())
```
Algo bem simples, apenas pega a saída de dados e executa um comando upper(). 