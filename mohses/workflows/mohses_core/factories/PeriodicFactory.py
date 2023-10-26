#!/usr/env python
# -*- python -*- vi:ft=python:
# vim:set ts=2 sw=2 sts=2 et:
import sys
import re

import datetime
import os

from .Common import *
from buildbot.plugins import*

def periodic_factory( repo=r'https://github.com/StevenAWhite/Mohses_Refactor.git', branch='trunk',
                      isCrossBuild=False, runUnitTest=False, isMonthly=False, isWeekly=False, isDaily=False):
  factory =  create_specified_factory(repo=repo
                                      ,fallback_commit=branch 
                                   ,crossCompile=isCrossBuild)
  
  addStep_build_libraries(factory)
  addStep_native_bundle(factory)

  return factory

