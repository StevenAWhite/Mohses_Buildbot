import sys
import os
import io
from slackclient import SlackClient

uploadFile = sys.argv[1]
uploadTime = sys.argv[2]
if len(sys.argv) >= 4:
  blameList = sys.argv[3]
else:
  blameList = ""

slack_token = "xoxb-174499064804-537869877826-GAC5u45bptmJRKV1bM2gAqFt"
sc = SlackClient(slack_token);

if not os.path.isfile(uploadFile):
  sc.api_call(
     "chat.postMessage",
     channel="#testing",
     text= uploadFile + " Not Found\n" + blameList + "\n" + uploadTime
  )
  sys.exit()
if os.stat(uploadFile).st_size == 0:
  sc.api_call(
    "chat.postMessage",
    channel="#testing",
    text= uploadFile + " is empty\n" + blameList + "\n" + uploadTime
  )
  sys.exit()
stringToPublish = blameList
if uploadFile == "TestResults.txt":
  stringToPublish += "\n"
  fi = open("TestResults.txt")
  line = fi.readline()
  finalResults = False
  while line:
    if "Global test environment tear-down" in line:
      finalResults = True
      line = fi.readline()
      continue
    if finalResults:
      stringToPublish += line
    print(line)
    line = fi.readline()
  fi.close()

with open(uploadFile, 'rb') as f:
    sc.api_call(
        "files.upload",
        channels='#testing',
        filename=uploadFile,
        title=uploadFile + " " + uploadTime,
        initial_comment=stringToPublish,
        file=io.BytesIO(f.read())
    )
