import os 
import ntpath
import pandas as pd
#import io
#from IPython.nbformat import current
try:
    from shutil import copyfile
except:
    pass
import datetime
#import IPython
import ast
import subprocess

def ppath(n):
    '''
    return pythonpath variable by index
    '''
    ppath=os.environ['pythonpath']
    return ppath[n]


def ss_file(fpth,to_generic_ss=False):
    '''
    function creates superceded folder (if one doesn't already exist) and
    copy and pastes a timestamp copy of file to ss before overwriting
    
    Name:
        20180918~3870~dev~pyfnctn~jg~ss_file(fnm)~A~0
    Args: 
        fnm (string): filename directory
    Returns:'''
    #import ntpath
    #ntpath.basename(fnm) #to get fname
    head,tail = os.path.split(fpth)
    
    if to_generic_ss == False:
        newpath = head+'\\'+'ss_' +os.path.splitext(tail)[0]
        if not os.path.exists(newpath):
            os.makedirs(newpath)
    
    if to_generic_ss == True:
        newpath = head+'\\'+'ss'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
            
    now= datetime.datetime.now()
    dst=newpath+'\\'+now.strftime("%Y%m%d %H%M")+'_ss_'+tail
    copyfile(fpth, dst)
    print('file superceded')

def rename_file(old_fpth,new_fpth, pr=False):
    '''
    https://stackoverflow.com/questions/2491222/how-to-rename-a-file-using-python
    '''
    os.rename(old_fpth, new_fpth)
    if pr ==True:
        print('{0} renamed to {1}'.format(old_fpth,new_fpth))
    else:
        pass

def fpth_chg_extension(fpth, new_ext='docx'):
    return os.path.join(os.path.dirname(fpth), os.path.splitext(fpth)[0] + '.' + new_ext)
    
def make_dir(fpth):
    '''check if directory exists
    if it doesnt then make it'''
    
    if not os.path.exists(fpth):
        os.makedirs(fpth)
        


def open_file(filename):
    '''Open document with default application in Python.'''
    try:
        os.startfile(filename)
    except AttributeError:
        subprocess.call(['open', filename])



def path_leaf(path):
    '''
    returns file name only (with extension)
    '''
    import ntpath
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def path_fol(path):
    '''
    returns file name only (with extension)
    '''
    import ntpath
    head, tail = ntpath.split(path)
    return head

def fnm_from_fpth(fpth,drop_extension=False):
    '''
    returns file name only without dir or extension
    '''
    if drop_extension ==False:
        return path_leaf(fpth)
    else:
        return os.path.splitext(path_leaf(fpth))[0]


from pathlib import Path
class DisplayablePath(object):

    #""" 
    #prints folder structure of a given path #
    #
    #Example:
    #paths = DisplayablePath.make_tree(Path(r'C:\Users\j.gunstone\git_mf\pyRevit\MFTools.extension'))
    #for path in paths:
    #    print(path.displayable())
    #"""
    from pathlib import Path
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


def make_dirs_from_dict(d, current_dir='./'):
    '''
    pass a dict and create folders with the 
    **current_dir directory
    '''

    for key, val in d.items():
        os.mkdir(os.path.join(current_dir, key))
        if type(val) == dict:
            make_dirs_from_dict(val, os.path.join(current_dir, key))    

def copy_rename(li,pr=False):
    '''
    copy renames files from a list of dicts
    
    Args: 
        li (list of dicts): list of old_fpths and new_fpths to rename
            keys:
                'old_fpth':
                'new_fpth':
        pr (bool): prints number of renamed files or not
    Returns:
        nothing. renamed files.
    Example:
        li = [{'old_fpth': 'Pdts\\raw\\ExportFolder\\BIMToolkit-ObjectDefinition_Ac_05_50_91.xlsx',
                'new_fpth': 'Pdts\\AllPdts\\Ac_05_50_91-TimberSourcing.xlsx'}]
        copy_rename(li,pr=True)

    '''
    for l in li:
        make_dir(path_fol(l['new_fpth']))
        copyfile(l['old_fpth'], l['new_fpth'])
    end=len(li)
    if pr==True:
        print('{0} files copied and renamed'.format(end))

def read_module_docstring(fpth):
    """
    Args:
        fpth(str): filepath of the script
    Returns
        docstring(str): module docstring
    """
    with open(fpth, 'r') as f:
        tree = ast.parse(f.read())
    docstring = ast.get_docstring(tree)
    return docstring

import tarfile
def extract_tarfile(fpth,extract_to='.'):
    """
    extract a tarfile
    Args:
        fpth(str): filepath of the tarfile
        extract_to(str): where to extract files to
    Returns:

    """

    if fpth.endswith("tar.gz"):
        tar = tarfile.open(fpth, "r:gz")
    elif fpth.endswith("tar"):
        tar = tarfile.open(fpth, "r:")
    else:
        return 'not a tarfile'
    tar.extractall(path = extract_to)
    tar.close()

def copy_files(fdir_from, fdir_to, rel_dir, files=[None]):
    """

    Args:
        fdir_from: src dir
        fdir_to: dst dir
        rel_dir: rel fol to dst dir
        files: list of files to copy

    Returns:

    """
    srcs = [os.path.join(fdir_from, file) for file in files]
    dstn_dir = os.path.join(fdir_to, rel_dir)
    make_dir(dstn_dir)
    dstns = [os.path.join(dstn_dir, file) for file in files]
    for k, v in dict(zip(srcs, dstns)).items():
        copyfile(k, v)

    return dstns


# from win32com.client import Dispatch
def createShortcut(path, target='', wDir='', icon=''):
    """
    create a windows shortcut link
    Args:
        path(str): path of shortcut you want to create
        **target(str): path of file to be opened when shortcut clicked
        **wDir(str): directory to start in (%v for same dir as the shortcut)
        **icon(str): path to .ico image file
    Returns:
        None

    Example:
        import os
        from mf_modules.file_operations import createShortcut
        path = os.path.join(os.environ['userprofile'],'Desktop', 'test.lnk')
        target = r"C:\engDev\git_mf\engDevSetup\dev\launch\gantt-CopyToJob.bat"
        wDir = r"%v"
        icon = r"C:\engDev\git_mf\engDevSetup\dev\icons\icon_ico\engineer-icon.ico"
        createShortcut(path, target=target, wDir=wDir, icon=icon)
    """
    if wDir=='':
        wDir='%V'
    ext = path[-3:]
    if ext == 'url':
        shortcut = file(path, 'w')
        shortcut.write('[InternetShortcut]\n')
        shortcut.write('URL=%s' % target)
        shortcut.close()
    else:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        if icon == '':
            pass
        else:
            shortcut.IconLocation = icon
        shortcut.save()
