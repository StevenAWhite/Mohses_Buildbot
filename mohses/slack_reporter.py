# Based on the gitlab reporter from buildbot

from __future__ import absolute_import, print_function
from future.utils import string_types

from twisted.internet import defer

from buildbot.process.properties import Properties
from buildbot.process.results import statusToString
from buildbot.reporters import utils, http
from buildbot.util import httpclientservice
from buildbot.util.logger import Logger
import buildbot.reporters.utils 


from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import requests
import json

logger = Logger()

STATUS_EMOJIS = {
    "success": ":partying_face:",
    "warnings": ":warning:",
    "failure": ":face_palm::skin-tone-3:",
    "skipped": ":kangaroo:",
    "exception": ":thunder_cloud_and_rain:",
    "retry": ":umbrella_with_rain_drops: ",
    "cancelled": ":octagonal_sign:",
}

# not used currently, could be if we use a different slack message format that allows for color
# highlighting
STATUS_COLORS = {
    "success": "#36a64f",
    "warnings": "#fc8c03",
    "failure": "#fc0303",
    "skipped": "#fc8c03",
    "exception": "#fc0303",
    "retry": "#fc8c03",
    "cancelled": "#fc8c03",
}

class SlackStatusPush(http.HttpStatusPushBase):
    name = "SlackStatusPush"
    neededDetails = dict(wantProperties=True)
    
    def __init__(self, *args, channel="#buildbot", oAuth="xoxb-174499064804-1914540108341-J6biEufgHnsQZNIzkgy1HIqr", verbose=False, **kwargs):
      super().__init__(*args, **kwargs)
      self.channel = channel
      self.oAuth = oAuth
      self.verbose = verbose
      self.client = WebClient(token=oAuth)
      self.project_ids = {}


    def checkConfig( self, channel=None, oAuth=None, **kwargs ):
        if channel and not isinstance(channel, str):
            logger.warning(
                "[SlackStatusPush] channel must be a string, got '%s' instead",
                type(channel).__name__,
            )
        if oAuth and not isinstance(oAuth, str):
            logger.warning(
                "[SlackStatusPush] oAuth must be a string, got '%s' instead",
                type(oAuth).__name__,
            )
 
    def GetResponsibleUserHandles(self, responsibleUsers):
      userList = None
      message = ""

      try:
        userList = self.client.users_list()
      except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        return  "".join(responsibleUsers)

      emailAndIDs = {}

      for user in userList['members']:
          if not user['is_bot'] and not user['deleted']:
              if 'profile' in user.keys():
                  if 'email' in user['profile'].keys():
                      emailAndIDs[user['profile']['email']] = "<@" + user['id'] + ">"


      for user in responsibleUsers:
          if user in emailAndIDs.keys():
              message += (emailAndIDs[user] + "\n")

      if message == "":
          return "".join(responsibleUsers)
      return message


    @defer.inlineCallbacks
    def reconfigService( self, channel="#buildbot", oAuth=None, attachments=True, verbose=False, **kwargs):
        yield super().reconfigService(**kwargs)
        if channel is not None:
          self.channel = channel
        if oAuth is not None:
          self.oAuth = oAuth
          self.client = WebClient(token=oAuth)
        self.verbose = verbose
        self.project_ids = {}

    @defer.inlineCallbacks
    def getBuildDetailsAndSendMessage(self, build, key):
        slackData = {}
        yield utils.getDetailsForBuild(self.master, build, **self.neededDetails)
        message = yield self.getMessage(build, key)
        slackData['text'] = message
        return slackData

    @defer.inlineCallbacks
    def getMessage(self, build, event_name):
        properties = build["properties"]
        builderName = build["builder"]["name"]
        buildNumber = str(build["number"])
        results = statusToString(build["results"])
        workerName = properties["workername"][0] 
        owners = yield utils.getResponsibleUsersForBuild(self.master, build["buildid"])
        ownersStr = ''.join(owners)
        url = build["url"]
        osVersion = properties["os_version"][0]
        resultEmoji = STATUS_EMOJIS.get(statusToString(build["results"]), ":facepalm:")
        messageStr = ''
        gotRevisionStr = ""
        responsibleUsersHandleStr = self.GetResponsibleUserHandles(owners)

        if "got_revision" in properties.keys():
            if type(properties["got_revision"][0]) == str:
                gotRevisionStr = "\t" + properties["got_revision"][0]
            elif isinstance(properties["got_revision"][0], dict):
                for key in properties["got_revision"][0]:
                    gotRevisionStr += "\t{0} : {1}\n".format(key, properties['got_revision'][0][key])

        if ownersStr == "":
            ownersStr = "Automatic"

        if event_name == "new":
            messageStr = "*Starting Build*" +  "\n<" + url + " | " + builderName + "> " + buildNumber

        elif event_name == "finished":
            messageStr = ("*Build Finished*\n" 
                + "<" + url + " | " + builderName + "> " + buildNumber + " completed with result: "
                + results + ' ' + resultEmoji + "\n*Change Set:* \n" + gotRevisionStr 
                + "\n*Worker:*\n\t" + workerName + "\n*Responsible Users:*\n\t" 
                + responsibleUsersHandleStr + "\n")
   
        return messageStr                    

    # returns a Deferred that returns None
    def buildStarted(self, key, build):
        return self.send(build, key[2])

    # returns a Deferred that returns None
    def buildFinished(self, key, build):
        return self.send(build, key[2])


    @defer.inlineCallbacks
    def send(self, build, key, builderName=None,
                    results=None, builds=None, users=None,
                    patches=None, logs=None, worker=None):
        slackData = yield self.getBuildDetailsAndSendMessage(build, key)

        if not slackData:
            return
        try:
           initial = self.client.chat_postMessage(channel=self.channel, link_names=True, text=slackData['text'])
           response = self.client.chat_postMessage(channel='#buildbot', text="{}".format(build),
                   thread_ts=initial["message"]["ts"])
        except SlackApiError as e:
           logger.error("Slack_SDK call came back in Error, the response is:\n%s".format(e.response['error']))
