#!/bin/env python

import sys

from buildbot.plugins import *
from . import workflows
#from . import slack_reporter as reporter


def configuration(workers):
  
  cb_dict = { **workflows.repo_codebase_map(),  }
  cb_func = lambda change : (_codebases)[change['repository']] 
  
  return {
     'pollers':workflows.pollers()
     ,'workflows':workflows.builders() 
     ,'schedules':workflows.schedules() 
     ,'codebases':cb_func
  }
  

if __name__ == "__main__":
  print( "Valid Configuration " + sys.argv[0])
  sys.exit(0)
