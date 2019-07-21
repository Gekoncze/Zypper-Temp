#!/usr/bin/python3


# IMPORTS BELONG HERE:

import os
import sys
import platform
import itertools
import subprocess


# DEFINITIONS BELONG HERE:

class Info:
    name = "Zypper Temp"
    version = "0.1.0"
    description = "Temporary installation of packages using zypper package manager."
    usage = (
        "Usage:\n"
        "    ZypperTemp.py install <dst cache file name> <package names>\n"
        "    ZypperTemp.py remove <src cache file name>"
    )
    options = (
        "Options:\n"
        "    -h --help      displays this help message\n"
        "    install        installs given packages, saving list of all installed packages into a cache file\n"
        "    remove         removes packages loaded from a list from a cache file\n"
    )

class Options:
    info = False
    install = False
    remove = False

def printHelp(message = None):
    if(message is not None): print(message)
    print(info.name + " (version: " + info.version + ")")
    print(info.description)
    print(info.usage)
    print(info.options)
    sys.exit("")
    
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
    cmd = "rpm -qa --last"
    output = runForOutput(cmd)
    lines = parseLines(output)
    packages = list()
    for line in lines:
        tokens = parseTokens(line)
        packages.insert(0, tokens[0])
    return packages
        
def installPackages(packages):
    cmd = "sudo zypper install " + packages
    runForExecution(cmd)
    
def removePackages(packages):
    cmd = "sudo zypper remove " + packages
    runForExecution(cmd)
    
def diffPackages(oldPackages, newPackages):
    lastOldPackage = oldPackages[-1]
    searching = True
    diff = list()
    for package in newPackages:
        if searching == True:
            if package == lastOldPackage:
                searching = False
        else:
            diff.append(package)
            
    return diff


# ACTUAL SCRIPT BELONG HERE:
 
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

if options.info == True: printHelp("INFO: help == True")
if len(sys.argv) <= 1: printHelp("ERROR: len(sys.argv) <= 1")
if options.install == True and options.remove == True: printHelp("ERROR: install == True and remove == True")
if options.install == False and options.remove == False: printHelp("ERROR: install == False and remove == False")
if len(sys.argv) < 3: printHelp("ERROR: len(sys.argv) < 3")

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
    
    print("Saving cache file...")
    try:
        savePackagesFile(cache, diff)
    except:
        print("Error: Could not save cache file '" + cache + "'.")
        print("       Use 'rpm -qa --last' to find recently installed packages and remove them manually.")
        raise
    
if options.remove == True:
    cache = getCache()
    
    print("Loading cache file...")
    try:
        packages = readPackagesFile(cache)
    except:
        print("Error: Could not read cache file '" + cache + "'.")
        raise
        
    print("Removing packages...")
    if len(" ".join(packages).strip()) > 0:
        try:
            removePackages(" ".join(packages))
        except:
            print("Error: Could not remove packages.")
            raise
        
        print("Clearing cache file...")
        try:
            clearPackagesFile(cache)
        except:
            print("Error: Could not clear cache file. Clear it manually.")
            raise
