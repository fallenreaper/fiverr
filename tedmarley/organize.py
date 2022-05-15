import os
from argparse import ArgumentParser
import shutil
import sys

def validate(path:str):
  """Validate a path"""
  if not os.path.exists(path):
    raise Exception("Path doesnt exist")
  if not os.path.isdir(path):
    raise Exception("Target is not a Folder or Directory")

def process(path: str, DEBUG=False):
  if DEBUG: print(f"Processing Path: {path}")
  try:
    validate(path)
  except Exception as e:
    raise e
  dirContents = os.listdir(path)
  dirContents.sort()
  if DEBUG: print(f"Directory Contents: ", dirContents)
  contents = [x.lower() for x in dirContents]
  if DEBUG: print(contents)
  # If 5 or more files have the first 10+ characters matching.
  _d = {}
  for n in contents:
    if len(n) < 10:
      continue
    _sub = n[:10]
    _d[_sub] = _d.get(_sub, 0) + 1
  if DEBUG: print(_d)
  for n in dirContents:
    if len(n) < 10:
      continue
    _p = os.path.join(path, n)
    _sub = n[:10]
    if _d.get(_sub.lower(), 0) >= 5:
      # 5 matches for this was found.
      dirs = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
      foundList = [x for x in dirs if x.startswith(n[:10])]
      # check to see if a folder exists starting with the first 10 characters.
      if len(foundList) > 0:
        # Move it into there
        shutil.move(_p, os.path.join(path, foundList[0], n))
      else:
        # Make folder and then move into there
        shutil.move(_p, f"{_p}bk")
        os.mkdir(_p)
        shutil.move(f"{_p}bk", os.path.join(path, n, n))

def buildsampledata(path: str):
  names = ['ApplesAndBananas10.txt', 'ApplesAndBananas1.txt', 'ApplesAndBananas2.txt', 'ApplesAndBananas3.txt', 'ApplesAndBananas4.txt', 'ApplesAndBananas5.txt', 'ApplesAndBananas6.txt', 'ApplesAndBananas7.txt', 'ApplesAndBananas8.txt', 'ApplesAndBananas9.txt', 'PeachesAndGrapes1.txt', 'PeachesAndGrapes2.txt']
  if not os.path.exists(path):
    os.mkdir(path)
  for f in names:
    with open(os.path.join(path, f), "w") as fp:
      fp.write("Test")

def main():
  x = ArgumentParser(__file__, description='We want to be able to parse and organize files by filename.')
  x.add_argument('-p', '--path', help='Absolute Path of folder to Organize', type=str, required=True)
  # x.add_argument('-o', help='Output Location.  If this is supplied it will change from src location to this new location.', type=str)
  x.add_argument('-b', help="Builds a Sample Set at --path.", action='store_true')
  x.add_argument('-d', '--debug', help="Run with Debugging On.", action='store_true')
  args = x.parse_args(sys.argv[1:])
  if not args.path:
    x.print_help()
    exit(1)
  if args.b:
    buildsampledata( os.path.join(args.path))
  print("Starting to Process..")
  try:
    _debug = not not args.debug
    process(args.path, DEBUG=_debug)
  except Exception as e:
    print(f"Path Error. Use Absolute Path. {e}")
    exit(1)
  print("..Processing Complete.")
  exit(0)

if __name__ == '__main__':
  main()
