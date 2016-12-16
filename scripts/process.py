import os, sys, subprocess as bash

#configuracoes de path dentro da maquina docker: 
HADOOP_PATH = os.environ['HADOOP_PREFIX'] + '/bin/'
HADOOP_LIB  = os.environ['HADOOP_PREFIX'] + '/share/hadoop/tools/lib/'

#path para o arquivo: 
file_path   = '/k/data/Semple.TXT'
file_name   = 'Semple.TXT'

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
b.communicate()

print "Deletando arquivos temporarios"
