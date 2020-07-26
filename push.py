import sys
import os
msg = ''
if len(sys.argv) >= 2:
  msg = sys.argv[1]
else:
  msg = "update content"

os.system('git add .')
os.system('git commit -m "' + msg + '"')
os.system('git push origin master')
