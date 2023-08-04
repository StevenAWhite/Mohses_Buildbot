import mohses as mohses

from buildbot.plugins import worker

linux_amd64   = worker.LocalWorker('linuux_amd64')
linux_aarch64 = worker.LocalWorker('linux_aarch64')

mohses = mohses.configuration(
            {
              'linux':{
                 'amd64': linux_amd64,
                 'aarch64':linux_aarch64
                 } 
              ,'macosx' : {}
              ,'windows' : {}
            }
         )
print (f"The Value of mohses_configuration is:\n{mohses}")
