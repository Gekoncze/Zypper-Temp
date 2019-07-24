#!/usr/bin/python3


# IMPORTS

import os
import sys
import platform
import itertools
import subprocess


# CLASSES

class Info:
    name = "Zypper Temp"
    version = "0.2.0"
    description = (
        "Temporary installation of packages using zypper and rpm.\n"
    )
    usage = (
        "Usage:\n"
        "    ZypperTemp.py <install or remove> <dst cache file name> <package names>\n"
    )
    examples = (
        "Examples:\n"
        "    ZypperTemp.py install cache gcc make\n"
        "    ZypperTemp.py remove cache\n"
    )
    options = (
        "Options:\n"
        "    -h --help      displays this help message\n"
        "    install        installs given packages, saving the list of all new packages into a cache file\n"
        "    remove         removes packages from a list loaded from a cache file\n"
    )

class Options:
    info = False
    install = False
    remove = False


# FUNCTIONS

def printHelp():
    print(info.name + " (version: " + info.version + ")")
    print(info.description)
    print(info.usage)
    print(info.examples)
    print(info.options)
    
def parseLines(text):
    return list(filter(None, text.split("\n")))
    
def parseTokens(text):
    return list(filter(None, text.split(" ")))    

def runForOutput(cmd):
    args = list(filter(None, cmd.split(" ")))
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')
    
def runForExecution(cmd):
    args = list(filter(None, cmd.split(" ")))
    p = subprocess.run(args)
    
def readFile(path):
    f = open(path, "r")
    content = f.read()
    f.close()
    return content
    
def saveFile(path, content):
    f = open(path, "a")
    f.write(content)
    f.close()
    
def clearFile(path):
    f = open(path, "w")
    f.close()
    
def readPackagesFile(cache):
    return parseLines(readFile(cache))
    
def savePackagesFile(cache, packages):
    saveFile(cache, "\n".join(packages) + "\n");
    
def clearPackagesFile(cache):
    clearFile(cache)
    
def getCache():
    return sys.argv[2]
    
def getPackages():
    names = ""
    for i in range(3,len(sys.argv)):
        names = names + " " + sys.argv[i]
    return names
    
def installedPackages():
    cmd = "RpmQuery.py -sn -m"
    output = runForOutput(cmd)
    lines = parseLines(output)
    packages = list()
    for line in lines:
        tokens = parseTokens(line)
        if tokens[0] != "gpg-pubkey":
            packages.insert(0, tokens[0])
    return packages
        
def installPackages(packages):
    cmd = "sudo zypper install " + packages
    runForExecution(cmd)
    
def removePackages(packages):
    cmd = "sudo rpm --erase --nodeps " + packages
    print(cmd)
    runForExecution(cmd)
    
def diffPackages(oldPackages, newPackages):
    diff = list()
    for np in newPackages:
        isNew = True
        for op in oldPackages:
            if op == np:
                isNew = False
                break
        if isNew:
            diff.append(np)
    return diff


# SCRIPT
 
os.environ["LANG"] = "en_US"  # requires english locale
info = Info()
options = Options()

if len(sys.argv) >= 2:
    arg = sys.argv[1]
    if arg == "-h" or arg == "--help":
        options.info = True
    if arg == "install":
        options.install = True
    if arg == "remove":
        options.remove = True

if options.info == True or len(sys.argv) <= 1:
    printHelp()
    sys.exit("")
    
if options.install == True and options.remove == True: raise Exception("ERROR: install == True and remove == True")
if options.install == False and options.remove == False: raise Exception("ERROR: install == False and remove == False")
if len(sys.argv) < 3: raise Exception("ERROR: len(sys.argv) < 3")

if options.install == True:
    cache = getCache()
    packages = getPackages()

    print("Loading installed packages...")
    try:
        oldPackages = installedPackages()
    except:
        print("Error: Could not get old installed package names.")
        raise
    
    print("Installing new packages...")
    try:
        installPackages(packages)
    except:
        print("Error: Could not install new packages.")
        raise
        
    print("Loading installed packages...")
    try:
        newPackages = installedPackages()
    except:
        print("Error: Could not get new installed package names.")
        print("       Use 'rpm -qa --last' to find recently installed packages and remove them manually.")
        raise
        
    diff = diffPackages(oldPackages, newPackages)
    if len(diff) > 0:
        print("Saving cache file...")
        try:
            savePackagesFile(cache, diff)
        except:
            print("Error: Could not save cache file '" + cache + "'.")
            print("       Use 'rpm -qa --last' to find recently installed packages and remove them manually.")
            raise
    else:
        print("Nothing to do.")
    
if options.remove == True:
    cache = getCache()
    
    print("Loading cache file...")
    try:
        packages = readPackagesFile(cache)
    except:
        print("Error: Could not read cache file '" + cache + "'.")
        raise
        
    print("Removing packages...")
    packageNames = " ".join(packages)
    if len(packageNames.strip()) > 0:
        print("Following packages are going to be removed:")
        print()
        print(packageNames)
        print()
        decision = input("Continue? (y/n): ")
        if decision == "y":
            try:
                removePackages(packageNames)
            except:
                print("Error: Could not remove packages.")
                raise
        elif decision == "n":
            print("Canceled.")
        else:
            raise Exception("Unknown decision " + decision);
    else:
        print("Nothing to do.")
