# Zypper Temp (version: 0.1.0 alpha)</br>
<pre>Temporary installation of packages using zypper package manager.
IMPORTANT NOTE: Carefully check installed and removed packages list. Sometimes new packages get glued to the system somehow (WTF????), wiping out the whole system by dependencies.
Usage:
    ZypperTemp.py install cache packages
    ZypperTemp.py remove cache
    Note: cache is a destination file name that will be overwritten, you can pick another name
Options:
    -h --help      displays this help message
    install        installs given packages, saving list of all installed packages into a cache file
    remove         removes packages loaded from a list from a cache file</pre>
