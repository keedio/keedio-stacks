import re

class FlumeExtraFile:

  owner='nobody'
  group='nobody'
  mode=0644
  path=None
  parsed=False
  content=""
   
  def __init__(self,input):
    patern=re.compile('<\?(\w+)\?>(.*)')
    for line in input.split('\n'):
      match=patern.match(line)
      if match is None:
        self.content+=line+"\n"
        continue
      if match.group(1) == 'owner':
        self.owner=match.group(2)
      if match.group(1) == 'group':
        self.group=match.group(2)
      if match.group(1) == 'mode':
        self.mode=int(match.group(2),8)
      if match.group(1) == 'path':
        self.path=match.group(2)
    if self.path is not None: 
      self.parsed=True
