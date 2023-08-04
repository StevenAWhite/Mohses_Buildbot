# -*- python -*- vi:ft=python:
# vim:set ts=2 sw=2 sts=2 et:

#Author: Steven A White
#Date:   05-15-2018
#
# Maintainer Lucas Marin

import sys
import re

import datetime
from buildbot.plugins import *

from   .factories.TrackedFactory import *
from   .factories.NightlyFactory import *

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

def builders():
  builders = []

  #Tracked Builders  
  builders.append(
    util.BuilderConfig(name="mohses_core_linux_amd64"
      ,workernames=["local_amd64"]
      ,tags=["mohses","tracked","linux","gcc","x64"]
      ,factory=tracked_factory( branch='trunk', runUnitTest=False)
      ,properties={'generator':'Ninja'
                   ,'cross':'false'
                   ,'os':'linux'
                   ,'arch':'amd64'
                   ,'parallel_limit' : ''
                   }
    )
  )
  
  builders.append(
    util.BuilderConfig(name="mohses_core_linux_aarch64"
      ,workernames=["sed-hoses-mac02"]
      ,tags=["core","tracked","macos","clang10","x64"]
      ,factory=tracked_factory( branch='trunk', runUnitTest=False)
      ,properties={'generator':'Ninja'
                   ,'toolchain':'macos-yosemite'
                   ,'toolchain_sys_root':'macos-yosemite'
                   ,'cross':'false'
                   ,'howtos':'ON'
                   ,'os':'macos'
                   ,'arch':'amd64'
                   ,'parallel_limit' : ''
                   ,'external_dir':'macos-yosemite'
                   }
    )
  )
 
  builders.append(
    util.BuilderConfig(name="libBioGears_linux_gcc9-amd64"
      ,workernames=["sed-hoses-ub01","sed-biogears-ub02"] 
      ,tags=["core","tracked","linux","gcc9","x64"]
      ,factory=tracked_factory(branch='trunk', runUnitTest=True)
      ,properties={'generator':'Ninja'
                   ,'toolchain':'x86_64-linux-gnu-gcc-9'
                   ,'toolchain_sys_root':'linux-gcc9-amd64'
                   ,'cross':'false'
                   ,'howtos':'ON'
                   ,'os':'linux'
                   ,'arch':'amd64'
                   ,'parallel_limit' : ''
                   ,'external_dir':'linux-gcc9-amd64'
                   }
    )
  )
  builders.append(
    util.BuilderConfig(name="libBioGears_linux_gcc9-armhf" 
      ,workernames=["sed-hoses-ub01","sed-biogears-ub02"] 
      ,tags=["core","tracked","linux","gcc9","armhf"]
      ,factory=tracked_factory(branch='trunk', runUnitTest=False, isCrossBuild=True)
      ,properties={'generator':'Ninja'
                  ,'toolchain':'arm-linux-gnueabihf-gcc-9'
                  ,'toolchain_sys_root':'linux-gcc9-armhf'
                  ,'cross':'true'
                  ,'howtos':'OFF'
                  ,'os':'linux'
                  ,'arch':'armhf'
                  ,'parallel_limit' : ''
                  ,'external_dir':'linux-gcc9-amd64'
                  }
    )
  )
  builders.append(
    util.BuilderConfig(name="libBioGears_linux_gcc9-aarch64" 
      ,workernames=["sed-hoses-ub01","sed-biogears-ub02"] 
      ,tags=["core","tracked","linux","gcc9","aarch64"]
      ,factory=tracked_factory(branch='trunk', runUnitTest=False, isCrossBuild=True)
      ,properties={'generator':'Ninja'
                  ,'toolchain':'aarch64-linux-gnu-gcc-9'
                  ,'toolchain_sys_root':'linux-gcc9-aarch64'
                  ,'cross':'true'
                  ,'howtos':'OFF'
                  ,'os':'linux'
                  ,'arch':'aarch64'
                  ,'parallel_limit' : ''
                  ,'external_dir':'linux-gcc9-amd64'
                  }
    )
  )
  builders.append(
    util.BuilderConfig(name="libBioGears_windows_msvc15"
      ,workernames=["sed-biogear-w01", "sed-biogear-w02"]
      ,tags=["core","tracked","windows","msvc15","x64"]
      ,factory=tracked_factory(branch='trunk', runUnitTest=True, onWindows=True)
      ,properties={'generator':'Visual Studio 15 2017 Win64'
                  ,'toolchain':'windows-vc15-amd64'
                  ,'toolchain_sys_root':'windows-vc15-amd64'
                  ,'cross':'false'
                  ,'howtos':'ON'
                  ,'os':'windows'
                  ,'arch':'amd64'
                  ,'parallel_limit' : '3'
                  ,'external_dir':'windows-vc15-amd64'
                  }
    )
  )
  builders.append(
    util.BuilderConfig(name="libBioGears_windows_msvc16"
      ,workernames=["sed-biogear-w01", "sed-biogear-w02"]
      ,tags=["core","tracked","windows","msvc16","x64"]
      ,factory=tracked_factory(branch='trunk', runUnitTest=True, onWindows=True)
      ,properties={'generator':'Visual Studio 16 2019'
                  ,'toolchain':'windows-vc16-amd64'
                  ,'toolchain_sys_root':'windows-vc16-amd64'
                  ,'cross':'false'
                  ,'howtos':'ON'
                  ,'os':'windows'
                  ,'arch':'amd64'
                  ,'parallel_limit' : '3'
                  ,'external_dir':'windows-vc16-amd64'
                  }
    )
  )
  
  #Nightly Builders
  builders.append(
    util.BuilderConfig(name="nightly_libBioGears_macos-catalina"
      ,workernames=["sed-hoses-mac01"]
      ,tags=["core","nightly","macos","clang11","x64"]
      ,factory=nightly_factory(branch='trunk', runUnitTest=False, isNightly=True, isWeekly=True, isMonthly=True)
      ,properties={'generator':'Ninja'
                   ,'toolchain':'macos-catalina'
                   ,'toolchain_sys_root':'macos-catalina'
                   ,'cross':'false'
                   ,'howtos':'ON'
                   ,'os':'macos'
                   ,'arch':'amd64'
                   ,'parallel_limit' : ''
                   ,'prefix_path':  '/usr/local/opt/:/usr/local/opt/qt5'
                   ,'external_dir':'macos-catalina' 
                   }
    )
  )
  builders.append(
    util.BuilderConfig(name="nightly_libBioGears_macos-yosemite"
      ,workernames=["sed-hoses-mac02"]
      ,tags=["core","nightly","macos","clang10","x64"]
      ,factory=nightly_factory(branch='trunk', runUnitTest=False, isNightly=True, isWeekly=True, isMonthly=True)
      ,properties={'generator':'Ninja'
                   ,'toolchain':'macos-yosemite'
                   ,'toolchain_sys_root':'macos-yosemite'
                   ,'cross':'false'
                   ,'howtos':'ON'
                   ,'os':'macos'
                   ,'arch':'amd64'
                   ,'parallel_limit' : ''
                   ,'external_dir':'macos-yosemite' 
                   }
    )
  )
  builders.append(
    util.BuilderConfig(name="nightly_libBioGears_linux_gcc9-amd64" 
      ,workernames=["sed-hoses-ub01","sed-biogears-ub02"] 
      ,tags=["core","nightly","linux","gcc9","x64"]
      ,factory=nightly_factory(branch='trunk', runUnitTest=True, isNightly=True, isWeekly=True, isMonthly=True)
      ,properties={'generator':'Ninja'
                   ,'toolchain':'x86_64-linux-gnu-gcc-9'
                   ,'toolchain_sys_root':'linux-gcc9-amd64'
                   ,'cross':'false'
                   ,'howtos':'ON'
                   ,'os':'linux'
                   ,'arch':'amd64'
                   ,'parallel_limit' : ''
                   ,'external_dir':'linux-gcc9-amd64'
                   }
    )
  )

  builders.append(
    util.BuilderConfig(name="nightly_libBioGears_linux_gcc9-armhf" 
      ,workernames=["sed-hoses-ub01","sed-biogears-ub02"] 
      ,tags=["core","nightly","linux","gcc9","armhf"]
      ,factory=nightly_factory(branch='trunk', runUnitTest=False, isNightly=True, isWeekly=True, isMonthly=True, isCrossBuild=True)
      ,properties={'generator':'Ninja'
                  ,'toolchain':'arm-linux-gnueabihf-gcc-9'
                  ,'toolchain_sys_root':'linux-gcc9-armhf'
                  ,'cross':'true'
                  ,'howtos':'OFF'
                  ,'os':'linux'
                  ,'arch':'armhf'
                  ,'parallel_limit' : ''
                  ,'external_dir':'linux-gcc9-amd64'
                  }
    )
  )

       
  builders.append(
    util.BuilderConfig(name="nightly_libBioGears_linux_gcc9-aarch64" 
      ,workernames=["sed-hoses-ub01","sed-biogears-ub02"] 
      ,tags=["core","nightly","linux","gcc9","aarch64"]
      ,factory=nightly_factory(branch='trunk', runUnitTest=False, isNightly=True, isWeekly=True, isMonthly=True, isCrossBuild=True)
      ,properties={'generator':'Ninja'
                  ,'toolchain':'aarch64-linux-gnu-gcc-9'
                  ,'toolchain_sys_root':'linux-gcc9-aarch64'
                  ,'cross':'true'
                  ,'howtos':'OFF'
                  ,'os':'linux'
                  ,'arch':'aarch64'
                  ,'parallel_limit' : ''
                  ,'external_dir':'linux-gcc9-amd64'
                  }
    )
  )

  builders.append(
    util.BuilderConfig(name="nightly_libBioGears_windows_msvc15"
      ,workernames=["sed-biogear-w01", "sed-biogear-w02"]
      ,tags=["core","nightly","windows","msvc15","x64"]
      ,factory=nightly_factory(branch='trunk', onWindows=True, runUnitTest=True, isNightly=True, isWeekly=True, isMonthly=True)
      ,properties={'generator':'Visual Studio 15 2017 Win64'
                  ,'toolchain':'windows-vc15-amd64'
                  ,'toolchain_sys_root':'windows-vc15-amd64'
                  ,'cross':'false'
                  ,'howtos':'ON'
                  ,'os':'windows'
                  ,'arch':'amd64'
                  ,'parallel_limit' : '3'
                  ,'external_dir':'windows-vc15-amd64'
                  }
                  
    )
  )
  builders.append(
    util.BuilderConfig(name="nightly_libBioGears_windows_msvc16"
      ,workernames=["sed-biogear-w01", "sed-biogear-w02"]
      ,tags=["core","nightly","windows","msvc16","x64"]
      ,factory=nightly_factory(branch='trunk', onWindows=True, runUnitTest=True, isNightly=True, isWeekly=True, isMonthly=True)
      ,properties={'generator':'Visual Studio 16 2019'
                  ,'toolchain':'windows-vc16-amd64'
                  ,'toolchain_sys_root':'windows-vc16-amd64'
                  ,'cross':'false'
                  ,'howtos':'ON'
                  ,'os':'windows'
                  ,'arch':'amd64'
                  ,'parallel_limit' : '3'
                  ,'external_dir':'windows-vc16-amd64'
                  }
    )
  )


  builders.append(
    util.BuilderConfig(name="upload-testing"
      ,workernames=["sed-hoses-ub01","sed-biogears-ub02"] 
      ,tags=["core","tracked","linux","gcc9","x64"]
      ,factory=nightly_factory(branch='trunk', runUnitTest=False,  doBuild=False, isNightly=False, isWeekly=False, isMonthly=False)
      ,properties={'generator':'Ninja'
                   ,'toolchain':'x86_64-linux-gnu-gcc-9'
                   ,'toolchain_sys_root':'linux-gcc9-amd64'
                   ,'cross':'false'
                   ,'howtos':'ON'
                   ,'os':'linux'
                   ,'arch':'amd64'
                   ,'parallel_limit' : ''
                   ,'external_dir':'linux-gcc9-amd64'
                   }
    )
  )

  return builders

def codebases():
  return {
              'corelib' : {'repository' : 'https://github.com/BioGearsEngine/core.git', 'branch' : 'trunk','revision' : None }
             ,'verification' :   {'repository' : 'ssh://git@sed-stash.us.ara.com:7999/bg/validation.git' , 'branch' : 'master','revision' : None}
         }

def schedules():
  schedules = []

  hoses_codebases= { **codebases(), **external.codebases()}
 
  hoses_force_codebases = [] #A list of strings, where each string is a key from the dictionary

  for key in hoses_codebases.keys():
     hoses_force_codebases .append(
      util.CodebaseParameter( #parameter group to specify sourcestamp for given codebase
          key #'codebase=key'
          ,label=key
          ,branch=util.StringParameter(name="branch", default=hoses_codebases[key]['branch'])
          ,revision=util.FixedParameter(name="revision", default="")
          ,repository=util.FixedParameter(name="repository", default=hoses_codebases[key]['repository'])
          ,project=util.FixedParameter(name="project", default="")
      )
    )
 
  schedules.append(schedulers.ForceScheduler(
                   name="core-build"
                   ,label="Manually Build"
                   ,builderNames=[ #a list of builders where the force button should appear
                                "libBioGears_macos-catalina"
                                ,"libBioGears_macos-yosemite"
                                ,"libBioGears_linux_gcc9-aarch64"
                                ,"libBioGears_linux_gcc9-armhf"
                                ,"libBioGears_linux_gcc9-amd64"
                                ,"libBioGears_windows_msvc15"
                                ,"libBioGears_windows_msvc16"
                                ,"nightly_libBioGears_macos-catalina"
                                ,"nightly_libBioGears_macos-yosemite"
                                ,"nightly_libBioGears_linux_gcc9-amd64"
                                ,"nightly_libBioGears_linux_gcc9-armhf"
                                ,"nightly_libBioGears_linux_gcc9-aarch64"
                                ,"nightly_libBioGears_windows_msvc15"
                                ,"nightly_libBioGears_windows_msvc16"
                                ,"upload-testing"
                                ]
                  ,properties=[util.FixedParameter(name="name",default="force")]
                  ,buttonName="Build Now"
                  ,codebases=hoses_force_codebases #a list of the names of the codebases
                  ,reason=util.StringParameter(name="reason", label="reason:", required=False, size=80)
                  ,username=util.UserNameParameter(label="email:", default="buildbot@hoses.dev", size=80)
               ))
  schedules.append(schedulers.ForceScheduler(
                   name="core-test"
                   ,label="Manually Test"
                   ,builderNames=[ #a list of builders where the verify button should appear
                                "libBioGears_macos-catalina"
                                ,"libBioGears_macos-yosemite"
                                ,"libBioGears_linux_gcc9-amd64"
                                ,"libBioGears_windows_msvc15"
                                ,"libBioGears_windows_msvc16"
                                ]
                  ,properties=[util.FixedParameter(name="name",default="nightly")]
                  ,buttonName="Test Now"
                  ,codebases=hoses_force_codebases #a list of the names of the codebases
                  ,reason=util.StringParameter(name="reason", label="reason:", required=False, size=80)
                  ,username=util.UserNameParameter(label="email:",size=80)
               ))
  schedules.append(schedulers.ForceScheduler(
                   name="core-validate"
                   ,label="Manually Validate"
                   ,builderNames=[ #a list of builders where the verify button should appear
                                "libBioGears_macos-catalina"
                                ,"libBioGears_macos-yosemite"
                                ,"libBioGears_linux_gcc9-amd64"
                                ,"libBioGears_windows_msvc15"
                                ,"libBioGears_windows_msvc16"
                                ]
                  ,properties=[util.FixedParameter(name="name",default="weekly")]
                  ,buttonName="Validate Now"
                  ,codebases=hoses_force_codebases #a list of the names of the codebases
                  ,reason=util.StringParameter(name="reason", label="reason:", required=False, size=80)
                  ,username=util.UserNameParameter(label="email:",size=80)
               ))
  schedules.append(schedulers.Nightly(
                     name='core-nightly'
                     ,builderNames=[
                                 "nightly_libBioGears_macos-catalina"
                                ,"nightly_libBioGears_macos-yosemite"
                                ,"nightly_libBioGears_linux_gcc9-amd64"
                                ,"nightly_libBioGears_linux_gcc9-armhf"
                                ,"nightly_libBioGears_linux_gcc9-aarch64"
                                ,"nightly_libBioGears_windows_msvc15"
                                ,"nightly_libBioGears_windows_msvc16"
                                ]
                     ,properties={'name':'nightly', 'isNightly':True, 'isWeekly':True, 'isMonthly':True}
                     ,dayOfWeek=[0,1,2,3,4]
                     ,hour=19,minute=30
                     ,createAbsoluteSourceStamps=True
                     ,codebases = hoses_codebases
                     #,onlyIfChanged=True
                 ))

  schedules.append(schedulers.AnyBranchScheduler(
                    name='core-tracked'
                    ,builderNames=[
                                "libBioGears_macos-catalina"
                                ,"libBioGears_macos-yosemite"
                                ,"libBioGears_linux_gcc9-aarch64"
                                ,"libBioGears_linux_gcc9-armhf"
                                ,"libBioGears_linux_gcc9-amd64"
                                ,"libBioGears_windows_msvc15"
                                ,"libBioGears_windows_msvc16"
                                ]
                    ,fileIsImportant=isImportant
                    ,properties={'name':'tracked'}
                    ,codebases = hoses_codebases
                    ,treeStableTimer = 300
                 ))
  return schedules
