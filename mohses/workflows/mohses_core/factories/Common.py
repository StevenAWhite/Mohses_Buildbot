#l;!/usr/env python
# -*- python -*- vi:ft=python:
# vim:set ts=2 sw=2 sts=2 et:
import sys
import re

from datetime import datetime
import os

from buildbot.plugins import *

#TODO: Pull VERSION of build using HasRev and set the INSTALL_PREFIX to mohses_rev-<TAG>
#TODO: Improve Branding of Artifacts

@util.renderer
def compute_artifact_filename(props):
    # Get the output of the `make print-BINARYDIST_FILENAME` step
    property_name = "{scheduler}_{ts}.tgz"  
    now_ts = datetime.now()
    return {
        "local_filename": "mohses_sdk",
        "upload_filename": property_name.format(scheduler=props["buildername"],ts=now_ts.strftime("%Y%m%d_%H%M"))
    }

@util.renderer
def generate_cmake_definitions(props):
    definitions = {
                  'CMAKE_BUILD_TYPE': 'Release'
                  ,'MOHSES_FETCH_THIRDPARTY' : 'OFF'
              }
    if "prefix_path" in props:
        definitions['CMAKE_PREFIX_PATH'] = util.Interpolate("%(prop:prefix_path)s")
    if "toolchain_file" in props:
        definitions['CMAKE_TOOLCHAIN_FILE'] = util.Interpolate("%(prop:builddir)s/toolchains/%(prop:toolchain_file)s")
    if any(key in props for key in ('root_find_path', 'sysroot_path')):
        definitions['CMAKE_FIND_ROOT_PATH'] =  util.Interpolate("%(prop:root_find_path)s;%(prop:sysroot_path)s") 
    if "parallel_jobs" in props:
        definitions['CMAKE_BUILD_PARALLEL_LEVEL'] = util.Interpolate("%(prop:parallel_jobs)s")
    definitions['CMAKE_INSTALL_PREFIX'] = 'mohses_sdk' 
    return definitions

def  create_tracked_factory(repo, fallback_commit='trunk', crossCompile=False):
  factory = util.BuildFactory()
  factory.addStep(steps.MakeDirectory(dir="source"
                     ,name="Making Directory: source"
                )
  )

  
  factory.addStep(steps.Git(repourl=repo, branch=fallback_commit
                       ,name="Pulling Mohses"
                       ,description="Pulling Mohses."
                       ,mode='full'  ,submodules=True
                       ,progress=True ,method='fresh'
                       ,config={"http.sslVerify":"false"}
                       ,workdir='source/core'
                       ,codebase='mohses'
                  )
  )


  factory.addStep(steps.RemoveDirectory(dir=util.Interpolate("build")
                       ,name="Cleaning Build Directory"
                  )
  )

  if crossCompile:
     factory.addStep(steps.FileDownload(
                           mastersrc=util.Interpolate("toolchains/%(prop:toolchain_file)s")
                          ,workerdest=util.Interpolate("%(prop:builddir)s/toolchains/%(prop:toolchain_file)s")
                     )
     )
  return factory

def create_specified_factory(repo, fallback_commit, crossCompile=False):
  factory = util.BuildFactory()
  factory.addStep(steps.MakeDirectory(dir="source"
                     ,name="Making Directory: source"
                )
  )
  factory.addStep(steps.Git(repourl=repo, branch=fallback_commit
                       ,name="Pulling Mohses"
                       ,description="Pulling Mohses."
                       ,mode='full'  ,submodules=True
                       ,progress=True ,method='fresh'
                       ,config={"http.sslVerify":"false"}
                       ,workdir='source/core'
                       ,codebase='mohses'
                  )
  )
  factory.addStep(steps.RemoveDirectory(dir=util.Interpolate("build")
                       ,name="Cleaning Build Directory"
                  )
  )
  if crossCompile:
     factory.addStep(steps.FileDownload(
                           mastersrc=util.Interpolate("toolchains/%(prop:toolchain_file)s")
                          ,workerdest=util.Interpolate("%(prop:builddir)s/toolchains/%(prop:toolchain_file)s")
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
                                          ,"--target", "create_distribution_bundle"
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
def addStep_native_bundle(factory):
  factory.addStep(steps.Compile(command=["cmake", "--build"
                                          ,util.Interpolate("%(prop:builddir)s/build") 
                                          ,"--config", "Release"
                                          ,"--target", "install"
                                          ]
                        ,name="Staging Runtime Dir"
                        ,warningPattern="^Warning: "
                        ,description="Staging runtime dir"
                        ,timeout=7200
                  )
  )
  factory.addStep(steps.SetProperties(properties=compute_artifact_filename))
  factory.addStep(steps.ShellCommand(command=["tar", "cfz", util.Interpolate("%(prop:upload_filename)s"), util.Interpolate("%(prop:local_filename)s")]
                                     ,flunkOnFailure=True
                                     ,workdir="build")
  )
  factory.addStep(steps.FileUpload(
                                workersrc=util.Interpolate("%(prop:upload_filename)s"),
                                flunkOnFailure=True,
                                masterdest=util.Interpolate("%(prop:artifact_upload)s/%(prop:upload_filename)s"),
                 )
  )
def addStep_cross_bundle(factory):
  factory.addStep(steps.ShellCommand(command=["cmake","-E","remove","-f","email.cfg"]
                       ,name="Delete email.cfg from runtime"
                       ,workdir=util.Interpolate("%(prop:builddir)s/build/runtime")
                  )
  )
  return factory

