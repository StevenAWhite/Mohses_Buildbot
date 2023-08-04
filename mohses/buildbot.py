#!/bin/env python

import sys

from buildbot.plugins import *
from . import workflows
#from . import slack_reporter as reporter

def configuration(workers):
  return workflows.configuration(workers)

if __name__ == "__main__":
  print( "Valid Configuration " + sys.argv[0])
  sys.exit(0)
