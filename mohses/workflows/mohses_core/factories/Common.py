#l;!/usr/env python
# -*- python -*- vi:ft=python:
# vim:set ts=2 sw=2 sts=2 et:
import sys
import re

import datetime
import os

from buildbot.plugins import *

@util.renderer
def generate_cmake_definitions(props):
     return {
               'CMAKE_BUILD_TYPE': 'Release'
              ,'CMAKE_PREFIX_PATH'     : util.Interpolate("%(prop:prefix_path)s")
              ,'CMAKE_TOOLCHAIN_FILE'  : util.Interpolate("%(prop:toolchain_file)s")
              ,'CMAKE_FIND_ROOT_PATH'  : util.Interpolate("%(prop:root_path)s")
              ,'CMAKE_BUILD_PARALLEL_LEVEL' : util.Interpolate("%(prop:parallel_jobs)s")
              ,'MOHSES_FETCH_THIRDPARTY ' : 'OFF'
           }

def  create_tracked_factory(repo, fallback_commit='trunk', crossCompile=False):
  factory = util.BuildFactory()
  factory.addStep(steps.MakeDirectory(dir="source"
                     ,name="Making Directory: source"
                )
  )
  factory.addStep(steps.Git(repourl=repo, branch=fallback_commit
                       ,name="Pulling Core Source"
                       ,description="Pulling Core source."
                       ,mode='full'  ,submodules=True
                       ,progress=True ,method='fresh'
                       ,config={"http.sslVerify":"false"}
                       ,workdir='source/core'
                       ,codebase='mohses'
                  )
  )

  if crossCompile:
    pass

  factory.addStep(steps.RemoveDirectory(dir=util.Interpolate("build")
                       ,name="Cleaning Build Directory"
                  )
  )
  return factory

def create_specified_factory(repo, fallback_commit, crossCompile=False):
  factory = util.BuildFactory()
  factory.addStep(steps.MakeDirectory(dir="source"
                     ,name="Making Directory: source"
                )
  )
  factory.addStep(steps.Git(repourl=r'https://github.com/BioGearsEngine/core.git'
                       ,name="Pulling Core Source"
                       ,description="Pulling Core source."
                       ,mode='full'  ,submodules=True
                       ,progress=True ,method='fresh'
                       ,config={"http.sslVerify":"false"}
                       ,workdir='source/core'
                       ,branch=fallback_commit
                       ,alwaysUseLatest=True
                  )
  )
  if crossCompile:
    pass

  factory.addStep(steps.RemoveDirectory(dir=util.Interpolate("build")
                       ,name="Cleaning Build Directory"
                  )
  )
  return factory

def addStep_build_libraries(factory):
  factory.addStep(steps.CMake(generator=util.Interpolate("%(prop:generator)s")
                       ,name="Configuring CMake"
                       ,path=util.Interpolate("%(prop:builddir)s/source/core/")
                       ,definitions=generate_cmake_definitions
                       ,options= ['-Wno-dev']
                       ,workdir=util.Interpolate("build")
                       ,description="Configuring CMake"
                  )
  ) 
  #It looks like parallel really slows down MSVC. So instead of having
  #MSVC not have parallel while other OSes do I'm currently not passing them.
  factory.addStep(steps.Compile(command=["cmake", "--build"
                                          ,util.Interpolate("%(prop:builddir)s/build") 
                                          ,"--config", "Release"
                                          ]
                        ,name="Building All"
                        ,warningPattern="^Warning: "
                        ,description="Building All"
                        ,timeout=7200
                  )
  )
  return factory

def addStep_build_unittests(factory):
  factory.addStep(steps.Compile(command=["cmake", "--build"
                                          ,util.Interpolate("%(prop:builddir)s/build") 
                                          ,"--config", "Release"
                                          ,"--target", "unittest"
                  #                       ,"--parallel", util.Interpolate("%(prop:parallel_jobs)s")
                                          ]
                       ,name="Build unittest"
                       ,warningPattern="^Warning: "
                       ,description="Build unittests"
                       ,timeout=7200
                  )
  )
  return factory

def addStep_build_all(factory):
  factory.addStep(steps.Compile(command=["cmake", "--build"
                                          ,util.Interpolate("%(prop:builddir)s/build") 
                                          ,"--config", "Release"
                   #                       ,"--parallel", util.Interpolate("%(prop:parallel_jobs)s")
                                          ]
                       ,name="Build all other targets"
                       ,warningPattern="^Warning: "
                       ,description="Build remaining targets"
                       ,timeout=7200
                  )
  )
  return factory

def addStep_build_gather_runtime_dependencies(factory):
  factory.addStep(steps.Compile(command=["cmake", "--build"
                                          ,util.Interpolate("%(prop:builddir)s/build") 
                                          ,"--config", "Release"
                                          ,"--target", "gather_runtime_dependencies"
                                          ,"--parallel", util.Interpolate("%(prop:parallel_jobs)s")
                                          ]
                        ,name="Staging Runtime Dir"
                        ,warningPattern="^Warning: "
                        ,description="Staging runtime dir"
                        ,timeout=7200
                  )
  )
  return factory 

def addStep_email_configure(factory):
  factory.addStep(steps.FileDownload(mastersrc="email.cfg"
                       ,name="Downloading email.cfg to runtime"
                       ,workerdest=util.Interpolate("%(prop:builddir)s/build/runtime/email.cfg")
                  )
  )
  return factory

def addStep_email_cleanup(factory):
  factory.addStep(steps.ShellCommand(command=["cmake","-E","remove","-f","email.cfg"]
                       ,name="Delete email.cfg from runtime"
                       ,workdir=util.Interpolate("%(prop:builddir)s/build/runtime")
                  )
  )
  return factory

