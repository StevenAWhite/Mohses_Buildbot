# -*- python -*- vi:ft=python:
# vim:set ts=2 sw=2 sts=2 et:

#Author: Steven A White
#Date:   08/04/2023

import sys
import re

import datetime
from buildbot.plugins import *

from   .factories.TrackedFactory import *
from   .factories.PeriodicFactory import *

if __name__ == "__main__":
  print( "Error: " + sys.argv[0] +" has no entry point", file=sys.stderr)
  sys.exit(1)

def isImportant(change):
  for name in change.files:
    if (name.endswith(".cpp") or name.endswith(".h")  or name.endswith(".txt") or name.endswith(".cmake") 
         or name.endswith(".xsd") or name.endswith(".qml") or name.endswith(".qrc") or name.endswith(".in")):
      return True
  return False

mohses_repo = r'https://github.com/StevenAWhite/Mohses_Refactor.git'

def repo_codebase_map():
  return {
   mohses_repo:'mohses'
  }

def pollers():
  pollers = []
  pollers.append(changes.GitPoller(
          repourl= mohses_repo
          , project = 'mohses'
          , category = 'source' 
          , branches=True 
          , pollAtLaunch=True
          , pollInterval=300))
  return pollers

def builders(workers):
  compatible_builders = {
    'all' : {}
    , 'nightly' : []
    , 'tracked' : [] 
  }
  #Search the worker dictionary for supported workers. 
  if 'linux' in workers: 
    print("Scanning for compatible linux workers")
    if 'amd64' in workers['linux']:
       print("\tmohses_core_linux_amd64 [Created!]")
       compatible_builders['tracked'].append(
         util.BuilderConfig(name="mohses_core_linux_amd64"
           ,workernames=workers['linux']['amd64']
           ,tags=["mohses","tracked","linux","gcc","amd64"]
           ,factory=tracked_factory(repo=mohses_repo, branch='trunk', runUnitTest=False)
           ,properties={'generator':'Ninja'
                        ,'cross':'false'
                        ,'os':'linux'
                        ,'arch':'amd64'
                        ,'parallel_limit' : ''
                        }
         )
       )
       print("\tnightly_mohses_core_linux_amd64 [Created!]")
       compatible_builders['nightly'].append(
         util.BuilderConfig(name="nightly_mohses_core_linux_amd64"
           ,workernames=workers['linux']['amd64']

           ,tags=["mohses","nightly","linux","gcc","amd64"]
           ,factory=periodic_factory(repo=mohses_repo, branch='trunk', runUnitTest=False, isDaily=True, isWeekly=True, isMonthly=True)
           ,properties={'generator':'Ninja'
                        ,'cross':'false'
                        ,'os':'linux'
                        ,'arch':'amd64'
                        ,'parallel_limit' : ''
                        }
         )
       )
    if 'aarch64' in workers['linux']:
       print("\tmohses_core_linux_aarch64 [Created!]")
       compatible_builders['tracked'].append(
         util.BuilderConfig(name="mohses_core_linux_aarch64"
           ,workernames=workers['linux']['aarch64']
           ,tags=["mohses","tracked","linux","gcc","aarch64"]
           ,factory=tracked_factory(repo=mohses_repo, branch='trunk', isCrossBuild=True, runUnitTest=False)
           ,properties={'generator':'Ninja'
                        ,'cross':'true'
                        ,'os':'linux'
                        ,'arch':'aarch64'
                        ,'parallel_limit' : ''
                        }
         )
       )
       print("\tnightly_mohses_core_linux_aarch64 [Created!]")
       compatible_builders['nightly'].append(
         util.BuilderConfig(name="nightly_mohses_core_linux_aarch64"
           ,workernames=workers['linux']['aarch64']
           ,tags=["mohses","nightly","linux","gcc","aarch64"]
           ,factory=periodic_factory(repo=mohses_repo, branch='trunk', isCrossBuild=True, runUnitTest=False, isDaily=True, isWeekly=True, isMonthly=True)
           ,properties={'generator':'Ninja'
                        ,'cross':'true'
                        ,'os':'linux'
                        ,'arch':'amd64'
                        ,'parallel_limit' : ''
                        }
         )
       )
  if 'windows' in workers: 
    print("Scanning for compatible windows workers")
    if 'amd64' in workers['windows']:
       print("\tmohses_windows_msvc17 [Created!]")
       compatible_builders['tracked'].append(
         util.BuilderConfig(name="mohses_windows_msvc17"
           ,workernames=workers['windows']['amd64']
           ,tags=["mohses","tracked","windows","msvc16","amd64"]
           ,factory=tracked_factory(repo=mohses_repo, branch='trunk', runUnitTest=True)
           ,properties={'generator':'Visual Studio 17 2022'
                       ,'cross':'false'
                       ,'os':'windows'
                       ,'arch':'amd64'
                       ,'parallel_limit' : '3'
                       }
         )
       )
       print("\tnightly_mohses_windows_msvc17 [Created!]")
       compatible_builders['nightly'].append(
         util.BuilderConfig(name="nightly_mohses_windows_mvc17"
           ,workernames=workers['windows']['amd64']
           ,tags=["mohses","nightly","windows","msvc17","amd64"]
           ,factory=periodic_factory(repo=mohses_repo, branch='trunk', runUnitTest=False, isDaily=True, isWeekly=True, isMonthly=True)
           ,properties={'generator':'Visual Studio 17 2022'
                        ,'cross':'false'
                        ,'howtos':'ON'
                        ,'os':'windows'
                        ,'arch':'amd64'
                        ,'parallel_limit' : ''
                        }
         )
       )
  compatible_builders['all'] = compatible_builders['tracked'] + compatible_builders['nightly']
  compatible_builders['force'] = compatible_builders['all']
  return compatible_builders

def codebases():
  return {
              'mohses' : {'repository' : 'https://github.com/StevenAWhite/Mohses_Refactor.git', 'branch' : 'trunk','revision' : None }
         }

def schedules(builders):
  schedules = []
  print(builders)
  mohses_codebases= { **codebases() }
 
  mohses_force_codebases = [] #A list of strings, where each string is a key from the dictionary

  for key in mohses_codebases.keys():
     mohses_force_codebases .append(
      util.CodebaseParameter( #parameter group to specify sourcestamp for given codebase
          key #'codebase=key'
          ,label=key
          ,branch=util.StringParameter(name="branch", default=mohses_codebases[key]['branch'])
          ,revision=util.FixedParameter(name="revision", default="")
          ,repository=util.FixedParameter(name="repository", default=mohses_codebases[key]['repository'])
          ,project=util.FixedParameter(name="project", default="")
      )
    )
   
  schedules.append(schedulers.ForceScheduler(
                  name="mohses-manual"
                  ,label="Manually Build"
                  ,builderNames=builders['force']
                  ,properties=[util.FixedParameter(name="name",default="force")]
                  ,buttonName="Build Now"
                  ,codebases=mohses_force_codebases #a list of the names of the codebases
                  ,reason=util.StringParameter(name="reason", label="reason:", required=False, size=80)
                  ,username=util.UserNameParameter(label="email:", default="buildbot@crest.washington.edu", size=80)
               ))
  schedules.append(schedulers.Nightly(
                     name='mohses-nightly'
                     ,builderNames=builders['nightly']
                     ,properties={'name':'nightly', 'isNightly':True, 'isWeekly':True, 'isMonthly':True}
                     ,dayOfWeek=[0,1,2,3,4]
                     ,hour=19,minute=30
                     ,createAbsoluteSourceStamps=True
                     ,codebases = mohses_codebases
                     #,onlyIfChanged=True
                 ))

  schedules.append(schedulers.AnyBranchScheduler(
                    name='mohses-tracked'
                    ,builderNames=builders['tracked']
                    ,fileIsImportant=isImportant
                    ,properties={'name':'tracked'}
                    ,codebases = mohses_codebases
                    ,treeStableTimer = 300
                 ))
  return schedules
