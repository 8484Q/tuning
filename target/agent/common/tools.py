import os
import re

from collections import defaultdict
from agent.common.system import sysCommand
from agent.plugin.methods import strip


class ConfigFile:
    def __init__(self, path, pattern = r"^(.+)\s*=\s*(.+)"):
        self.path = path  
        self.pattern = pattern
    
    def readValue(self, key):
        with open(self.path, 'r') as f:
            content = f.read()
        
        for k,v in re.findall(self.pattern, content):
            if k.strip() == key.strip():
                return v
        return None
    
    def writeValue(self, key, value):
        sysCommand("echo {key} = {value} >> {path}".format(
            key = key,
            value = value,
            path = self.path
        ))
        
    def removeDuplicate(self):
        with open(self.path, 'r') as f:
            content = f.read()
        
        content_lines = [i for i in content.split('\n') if i != '']
        no_duplicate_dict = defaultdict(str)
        no_duplicate_content = ""
        
        for line in content_lines:
            if line.startswith("#"):
                no_duplicate_content += line + '\n'
                
            elif re.search(self.pattern, line):
                key = re.search(self.pattern, line).group(1)
                no_duplicate_dict[key] = line
        
        for _, line in no_duplicate_dict.items():
            no_duplicate_content += line + '\n'
        
        with open(self.path, 'w') as f:
            f.write(no_duplicate_content)


def adaptiveCall(args, adaptive_args, func):
    assert isinstance(args, list)
    
    if isinstance(adaptive_args, list):
        for arg, adaptive_arg in zip(args, adaptive_args):
            func(arg, adaptive_arg)
    else:
        for arg in args:
            func(arg, adaptive_args)


def getActiveOption(options, dosplit = True):
    m = re.match(r'.*\[([^\]]+)\].*', options)
    if m:
        return m.group(1)
    if dosplit:
        return options.split()[0]
    return options


def stretchWildcard(path):
    paths = _stretchWildcard([path])
    return [p for p in paths if os.path.exists(p)]


def _stretchWildcard(path_list:list):
    """ replace '*' wildcard in path and return all matched path

    """
    def _splitByWildcard(path):
        prefix   = '/'
        wildcard = ''
        suffix   = ''
        
        for _p in path.split('/'):
            if wildcard != '':
                suffix = os.path.join(suffix, _p)
            elif '*' in _p:
                wildcard = _p
            else:
                prefix = os.path.join(prefix, _p)
        return prefix, wildcard, suffix
    
    def _replaceWildcard(prefix, wildcard, suffix):
        if not os.path.exists(prefix):
            return []

        candidates = os.listdir(prefix)                        
        pattern = re.compile(re.sub(r"\*", ".*", wildcard))
        valid_candidate = [c for c in candidates if re.match(pattern, c)]
        
        result = []
        for c in valid_candidate:
            result.append(os.path.join(prefix, c, suffix))
        return result
    
    result = []
    for path in path_list:
        if "*" not in path:
            result.append(path)
        else:
            prefix, wildcard, suffix = _splitByWildcard(path)
            _res = _replaceWildcard(prefix, wildcard, suffix)
            result += _stretchWildcard(_res)
    return result