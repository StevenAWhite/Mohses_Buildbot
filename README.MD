# Introduction
This repo stores the configuration files for buildbot and its workers. It is a work in progress and will eventually have 
one folder for each worker along with the master config file. 
The purpose of this repo is to avoid a loss of configuration files due to rm -rf mistakes

# Usuage
The easiest way to use this REPO is with virtualenv from python3.9. You can run this on any OS, but it works best on POSIX like oses like macos and linux.

Install Python 3.9
pip3.9 install virtual env
python3.9 -m venv path/to/env
cd path/to/env
source bin/activate

pip3 install buildbot[bundle]
pip3 insall buildbot-badges
pip3 install lz4

Edit specifics in biogears/buildbot.py
Edit specifics in buildbot.tac

buildbot start

Each build-worker will need to then be setup with a python3.9 virtual environent with buildbot-worker. 
Each machine including master will need some method of starting the services at startup to avoid disruption and 
if you are using ssh to clone for stash you will need to setup ssh-keys for each machine on a profile to allow cloaning
