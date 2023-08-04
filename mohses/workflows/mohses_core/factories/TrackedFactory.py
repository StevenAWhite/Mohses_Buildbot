#!/usr/env python
# -*- python -*- vi:ft=python:
# vim:set ts=2 sw=2 sts=2 et:
import sys
import re

import datetime
import os

from .Common import *
from buildbot.plugins import*

def tracked_factory( repo=r'https://github.com/StevenAWhite/Mohses_Refactor.git', branch='trunk', isCrossBuild=False, runUnitTest=False, release=False):
  factory =  create_tracked_factory(repo=repo, fallback_commit=branch, crossCompile=isCrossBuild)
  addStep_build_libraries(factory)
  return factory

