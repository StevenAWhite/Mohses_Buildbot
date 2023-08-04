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
#   Buildbot build configuration. Combines worker, factory, and properties 
#
# Build Schedules      : schedules()
#  Buildbot scheduler combiantions preffered for each builder. You can reuse 
#  builders to make your own schedules. Defaults to Tracked, Timmed and Manual 
#  for each builder

def repo_codebase_map():
  return mohses_core.repo_codebase_map()

#Append Pollers from imported workflows
def pollers():
  return mohses_core.pollers()

#Append Builders from imported workflows
def builders():
  return mohses_core.builders()

#Append Schedulers from imported workflows
def schedules():
  return mohses_core.schedules()
