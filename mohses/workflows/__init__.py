#!/bin/python

from . import mohses_core


#We need to consolidate all of the various workflow properties
#Each workflow produces the following
#
# repository codebases : repo_codebase_map()
#   Python Dictionary of the format { repo_url : name }
#
# repository poller    : pollers()
#   Source tracking for each repository to generate changesets
#
# Build Receipies      : builders()
#   Returns a dict of all,force,nightly,tracked builders. needs to be flattented
#     to buble up
#
# Build Schedules      : schedules()
#  Buildbot scheduler combiantions preffered for each builder. You can reuse 
#  builders to make your own schedules. Defaults to Tracked, Timmed and Manual 
#  for each builder

def  configuration(workers):
  cb_dict = consolidated_repo_codebase_map()
  cb_func = lambda change : (_codebases)[change['repository']]

  known_builders = builder_dictionary(workers)
  print (known_builders)
  consolidated_builders = flatten_builders(known_builders) 
  return  {
        'pollers':consolidated_pollers()
       ,'builders': consolidated_builders
       ,'schedules':consolidated_schedules(known_builders)
       ,'codebases':cb_func
    }

def consolidated_repo_codebase_map():
  return { **mohses_core.repo_codebase_map() }

def consolidated_pollers():
  return mohses_core.pollers()

# @param: recursive dictionary of workers 
# 'os': 'platform' : [ buildbot.worker ]
#  Supported OSs windows,linux,macos
#  Supported platforms amd64, aarch64, armv7
#  Individual workflows will only setup what they support
def builder_dictionary(workers):
  return { 'mohses' : mohses_core.builders(workers) }

#Append Schedulers from imported workflows
def consolidated_schedules(builders):
  schedules = [] 
  if 'mohses' in builders:
      mohses_names = {}
      if 'all' in builders['mohses']:
        mohses_names['all']=getBuilderNames(builders['mohses']['all'])
      if 'force' in builders['mohses']:
        mohses_names['force']=getBuilderNames(builders['mohses']['force'])
      if 'nightly' in builders['mohses']:
        mohses_names['nightly']=getBuilderNames(builders['mohses']['nightly'])
      if 'tracked' in builders['mohses']:
        mohses_names['tracked']=getBuilderNames(builders['mohses']['tracked'])
      schedules = schedules + mohses_core.schedules(mohses_names)
  return schedules

#Assumes each workflow has an all category inside its returned dictionary
#Additional categories force,tracked,nightly are used to setup schedulers
def flatten_builders(builders):
  builder_list = []
  print(f"workflow_builders:{builders}")
  for workflow in builders:
    builder_list = builder_list + builders[workflow]['all']
  return builder_list

def getBuilderNames(builders):
 names = []
 for builder in builders:
   names.append(builder.name)
 print (names)
 return names


def getBuilderNames(builders):
 names = []
 for builder in builders:
   names.append(builder.name)
 print (names)
 return names
