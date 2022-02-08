# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 10:51:11 2018
datamine_functions
@author: j.gunstone
"""

import re
import pandas as pd
import time
import os
import fnmatch


def does_drive_exist(letter):
    '''
    e.g. does_drive_exist('J')
    '''
    import win32file
    return (win32file.GetLogicalDrives() >> (ord(letter.upper()) - 65) & 1) != 0


def extract_digit(string):
    '''
    exracts digits only from strings
    Arg: 
        string including char, digits, ascii etc.
    Returns: 
        digits only 
    '''
    result=re.sub("\D", "", string)
    result=int(result)
    return result
    
#result = [extract_digit(im) for im in img]

def list_files(path):
    '''
    list all files within path
    '''
    return [f for f in os.listdir(path) if os.path.isfile(f)]



def make_folder(directory):
    '''
    check if folder exists, if not, make a new folder using python
    '''
    import os, errno

    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def extrct_units_in_brckts(string):
    '''
    name: 
        20180619~3870~dev~pyfnctn~jg~extract text from within brackets ~A~0
    tags: 
        strings, brackets, units, 
    Args: 
        string (string): 
    '''
    substring=string[string.find("(")+1:string.find(")")]
    return substring

### Functions for extracting the data from the .inp files


# function: define text search 
def find_word(text, search, enclosed_by_spaces=False):
    '''
    search for text within a string

    Name: 

    Args: 
        text (string): text to search
        search (string): word to search for in 'text'
        **enclosed_by_spaces (bool): define if the 'search' word is enclosed by spaces (defaults to False)

    Returns: 
        bool (True or False)
    '''
    if enclosed_by_spaces==False:
        result = re.findall('\w*'+''+search+''+'\w*', text, flags=re.IGNORECASE)
    else:
        result = re.findall('\w*'+' '+search+' '+'\w*', text, flags=re.IGNORECASE)
   #result = re.findall('\w*'+' '+search+' '+'\w*', text, flags=re.ASCII)
    
    if len(result)>0:
        return True
    else:
        return False

def file_len(fname):
    '''count how many lines in a (.txt?) file'''
    with open(fname) as f:
        for i in enumerate(f):
            pass
    return i + 1

# function: return job_no as value from file directory
def jobno_fromdir(dir):
    '''
    returns the job number from a given file directory

    Name: 

    Args: 
        dir (filepath): file-directory
    Returns: 
        job associated to file-directory
    '''
    string = dir
    # string = string.strip('J:\J') - changed from this as issues arise when there is lowercase
    string = string[4:]
    job_no=string[:4]
    return job_no

def df_time_meta_data(pth,sort_by='time_of_file_creation'):
    '''
    creates a df of file paths of files within a given folder 
    with their associated meta-data. 
    
    Args:
        pth(string): folder file path
        **sort_by(string): what time meta characteric to sort_by:
            'time_of_file_creation' (default)
            'time_of_most_recent_access'
            'time_of_most_recent_content_modification'
            
    Returns:
        df (pd.DataFrame): with all files within "pth" sorted by 
            "sort_by" characteristic
    
    Requires:
        from datamine_functions import time_meta_data
    '''
    if os.path.isfile(pth):
        fpths = [pth]
    else:
        nms=os.listdir(pth)
        fpths=[os.path.join(pth, nm) for nm in nms]
    df=pd.DataFrame(columns=['fdir','time_of_file_creation','time_of_most_recent_access','time_of_most_recent_content_modification'])
    for fpth in fpths:
        df=df.append(time_meta_data(fpth)) 
    df=df.sort_values(by=[sort_by],ascending=False)
    df=df.reset_index(drop=True)
    return df   

def time_meta_data(fpth,as_DataFrame=True):
    
    '''    
    extract time based metadata about a file 
    
    Name: 
        20180916~3870~dev~pyfnctn~jg~get time based metadata for a file~A~0
    
    Args: 
        fdir (string): file-directory
        
    See Also:
        list of metadata available from os.stat(fdir): https://docs.python.org/3/library/os.html
        write docstrings like google: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
        Google python code style guide: https://github.com/google/styleguide/blob/gh-pages/pyguide.md
        
    References:
        https://docs.python.org/3/library/os.html
            shows other info available from os.stat
        
    Returns: 
        df (pd.DataFrame):
            time_of_file_creation (string):
            time_of_most_recent_access (string):
            time_of_most_recent_content_modification (string):
            
    To Do:
        add optionally extract other meta-data available from os.stat
        this should be *args inputs
        
      
    '''
    def string_of_time(t):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
    
    di={}
    meta = os.stat(fpth)
    di['fpth']=fpth
    di['time_of_file_creation']= string_of_time(meta.st_ctime)
    di['time_of_most_recent_access'] = string_of_time(meta.st_atime)
    di['time_of_most_recent_content_modification']= string_of_time(meta.st_mtime)
    
    if as_DataFrame==True:
        return pd.DataFrame.from_dict(di,orient='index').T
    
    else:
        return di
    

### Functions to find and filter out .inp files

def list_filetypes(folder,suffix):
    '''    
    traverse the specified folder searching for filetype
    that matches the specified suffix and generate a list of directories.
    note: as this command compiles to a list before reporting when searching
    large directories it can take a long time with no useful outputs until 
    it has completely finished running
    
    Name: 
        20180916~3870~dev~pyfnctn~jg~list_filetypes(folder,suffix)~A~0
    
    Args: 
        folder (string): folder path to search in
        suffix (string): file extension to search for in folder
    
    See Also:
        napolean docstring guide: https://github.com/sphinx-contrib/napoleon
        Google python code style guide: https://github.com/google/styleguide/blob/gh-pages/pyguide.md

    Returns: 
        li (list): list with filedirectory of files within 'suffix'

    '''

    # import os
    li = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(suffix):
                 li.append(os.path.join(root, file))

    return li

def define_inp_type(inp_dir, time_data=True):
    '''    
    extract type characteristics (e.g. SBEM, BRUKL, epc) from IES .inp results file
    clean up and put into pd.DataFrame
    (optional) extract time-based metadata about .inp file and add to dataframe
    
    Name: 
        20180916~4047~dev~pyfnctn~jg~define IES .inp file-type and metadata~A~0
    
    Args: 
        inp_dir (string): file-directory of .inp file
        **time_data (bool): attach time based meta data about the file to dataframe or not
    
    See Also:
        write docstrings like google: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
        Google python code style guide: https://github.com/google/styleguide/blob/gh-pages/pyguide.md
        requires function: 20180916~3870~dev~pyfnctn~jg~get time based metadata for a file~A~0 

    Returns: 
        df (pd.DataFrame): contain the following cols:
            inp_dir (file-directory of .inp file)
            project_type (S-BEM, EPC etc.)
            C-NAME (certifier name)
            C-REG-NUMBER (certifier registration number)
            and if **time_data (bool) = True:
                time_of_file_creation (string):
                time_of_most_recent_access (string):
                time_of_most_recent_content_modification (string):

    '''
    # import re
    
    # create dataframe to populate with info
    cols=['inp_dir','C_NAME','C_REG_NUMBER','project_type']
    df=pd.DataFrame(columns = cols)
    df.inp_dir = list(range(0,1))
    n=0
    df.inp_dir = inp_dir
    
    # populate dataframe with info
    searchfile = open(inp_dir, "r")
    for line in searchfile:
        if find_word(line,'= GENERAL'):df.project_type[n]=line
        if find_word(line,'C-NAME'):df.C_NAME[n]=line
        if find_word(line,'C-REG-NUMBER'):df.C_REG_NUMBER[n]=line
    
    df=df.fillna(0) 
    
    # clean extracted info from lines extracted from .inp file
    if df.project_type[n]!= 0:
        userInputtedText=df.project_type[n]
        quoted = re.compile('"[^"]*"')
        for value in quoted.findall(userInputtedText):
            value= value.replace('"', "")
            df.project_type[n]=(value)
            
    if df.C_REG_NUMBER[n]!= 0:
        userInputtedText=df.C_REG_NUMBER[n]
        quoted = re.compile('"[^"]*"')
        for value in quoted.findall(userInputtedText):
            value= value.replace('"', "")
            df.C_REG_NUMBER[n]=(value)
              

    if df.C_NAME[n]!= 0:
        userInputtedText=df.C_NAME[n]
        quoted = re.compile('"[^"]*"')
        for value in quoted.findall(userInputtedText):
            value= value.replace('"', "")
            df.C_NAME[n]=(value)
    
    # attach time-based metadata to the pandas row
    if time_data==True:
        time=time_meta_data(inp_dir)
        del time['fdir']
        df = pd.concat([df, time], axis=1)
    
    return df

def index_df_temp(df_temp):

    '''
    renames IES extraction variables such 
    that they can be used as column names and 
    then indexes the dataframe by ies_var name
    '''
    
    df_temp['ies_var_col_name']=0
    end = len(df_temp)
    
    for n in range(0,end):
        v_list=list(df_temp.ies_var[n])
        end2=len(v_list)
        for m in range(0,end2):
            v_list[m]=v_list[m].replace("/", "_")
            v_list[m]=v_list[m].replace("-", "_")

        v_list="".join(v_list)  
        df_temp.ies_var_col_name[n]=v_list
    
    df_temp.set_index(keys="ies_var_col_name",inplace=True,drop=True,append=False)
        
    return df_temp

def temp_to_main(df_temp,df2,job_index):
    
    '''
    parses the values in the extracted 
    temporary database to the main dataframe
    
    note. this could be done more efficiently by merging dataframes 
    c.f. JakeVanderPlas pythonbookofdatascience
    '''

    col='var_value'
    end=len(df_temp)
    var=df_temp.index.values

    for n in range(0,end):
        ies_var=var[n]
        df2[ies_var][job_index]=df_temp[col][ies_var]


def m_df_temp(lookup_len):
    
    '''
    create a temporary df to parse data extracted 
    from the .inp file to (the df_temp gets re-defined for each new file)
    
    Args:
        lookup_len(int): number of rows (vars to extract) in 'df_lookup'
        
    Returns:
        m_df_temp (pd.DataFrame): 
            ies_extract: column containing the names of the variables being extracted
            var_des: column containing the associated value of the variable
    '''
    
    columns = ['ies_extract','var_des']
    m_df_temp = pd.DataFrame(columns=columns)
    m_df_temp.ies_extract = list(range(0,lookup_len))
    m_df_temp.ies_extract = 'n/a = n/a'
    
    return m_df_temp

def extract(inp_dir,df_temp,df_lookup):
    
    '''
    finds a line of the .inp file that 
    contains a word within the look-up table (df_lookup)
    then extracts that line to df (df_temp)

    Name: 
        20180916~3870~dev~pyfnctn~jg~extract(r_index,df_temp), mine inp~A~0

    Args: 
        inp_dir (string): file-directory of .inp file
        df_temp (pd.DataFrame): temporary dataframe to populate
        df_lookup (pd.DataFrame): lookup df wih parameters you want to get out of the .inp file
    Returns: 
        df_temp
    '''    
	
    # loop through all lines in the look-up table and print associated line from IES file
    idx = len(df_temp)
    file = open(inp_dir, 'r')
    yourResult = [line for line in file.readlines()]
    num_lines=len(yourResult)
    for l in range(0,num_lines):
        yourResult[l]=' '+yourResult[l]
        
    for n in range(0, idx): 
        count=0
        m =0
        for m in range(0,num_lines):
            count = count +1
            if find_word(yourResult[m],df_lookup.ies_var[n]):
                check=yourResult[m]
                check1=check.split('=')
                check1[0]=check1[0].replace(" ", "")
                if check1[0] == df_lookup.ies_var[n]:
                    df_temp.ies_extract[n] = yourResult[m]
                    break 
                
            elif num_lines-count==1:
                df_temp.ies_extract[n] = df_lookup.ies_var[n] +'=' '-1' # -1 = 'look up value not in .inp file'
                break 
    
    return df_temp

def clean_df(df_temp, df_lookup):
    '''
    clean the columns that were extracted from IES 
    string and look-up long variable name to match ies short name
    
    '''
    
    idx = len(df_temp)
    for n in range(0,idx):
        # strip of the '\n' that is stuck on for some reason...?
        df_temp.var_value[n] = df_temp.var_value[n].strip('\n')

        # look-up variable description from ies variable name
        var = df_lookup.ies_var[n]
        df_temp.var_des[n] = df_lookup.var_des[df_lookup['ies_var'] == var].values[0] 
    return df_temp

###############################################
#############THIS IS THE MAIN ONE!#############
###############################################

def extract_lookup_data_from_inp(inp_dir, df_lookup):
    '''
    extracts 'df_lookup' data from 'inp_dir' file and places 
    it in a dataframe

    Name: 
        20180916~3870~dev~pyfnctn~jg~extract_lookup_data_from_inp(inp_dir, df_lookup)~A~0
        
    Args: 
        inp_dir (filepath): file-directory of inp file
        df_lookup (pd.DataFrame): pandas dataframe containing lookup values
            ies_var (col name): name of lookup variable
            var_des (col name): description of lookup variable
            
    See Also:
        functions called:
            def clean_df(df_temp):
            def extract(inp_dir,df_temp):
            def m_df_temp(lookup_len):
            def index_df_temp(df_temp):
            
    Returns: 
        df_temp (pd.DataFrame): dataframe containing extracted values from .inp file
    '''    
    lookup_len=len(df_lookup)
    
    # create df_temp and poulate 
    df_temp = m_df_temp(lookup_len)

    # extract data from .inp file and populate dataframe
    df_temp = extract(inp_dir,df_temp)

    # Split delimited values in a DataFrame column into two new columns
    df_temp['ies_var'], df_temp['var_value'] = zip(*df_temp['ies_extract'].apply(lambda x: x.split('=', 1)))
    
    # clean the extracted columns and add description (var_des) to ies variable (ies_var)
    df_temp = clean_df(df_temp)

    # delete the now redundant extracted string
    del df_temp['ies_extract']

    # get rid of the /n (?)
    df_temp.var_value = df_temp['var_value'].str.strip()    
    df_temp.ies_var = df_temp['ies_var'].str.strip()  

    # index the temporary dataframe by ies_var
    index_df_temp(df_temp)
    
    return df_temp
    
###############################################
#############THIS IS THE MAIN ONE!#############
###############################################

import glob
def recursive_glob(rootdir='.', pattern='*', recursive=True):
    """ 
    Search recursively for files matching a specified pattern.
    
    name: 
        20180506~3870~code~pyfnctn~jg~recursive_glob~A~0
    tags: 
        rootdir, pattern, finding-files
    Reference: 
        Adapted from: http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
        string pattern matching: https://jakevdp.github.io/WhirlwindTourOfPython/14-strings-and-regular-expressions.html
    Args:
        **rootdir (string): the directory that you would like to recursively search. 
            recursive means it will automatically look in all folders within this directory
        **pattern (string): the filename pattern that you are looking for.
		**recursive (bool): define if you want to search recursively (in sub-folders) or not. 
		
	Returns:
		matches(list): list of filedirectories that match the pattern
    Example:
        rootdir='J:\J'+'J9999'
        pattern='????????_????_?*_?*_?*_?*_?*_?*'
        recursive_glob(rootdir=rootdir, pattern=pattern, recursive=True)
    """
    matches=[]
    if recursive ==True:
        for root, dirnames, filenames in os.walk(rootdir):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))

    else:
        #a = glob.glob(pattern)
        for filename in glob.glob1(rootdir,pattern):
            matches.append(os.path.join(rootdir,filename))
            
    return matches

from datetime import datetime
def get_duration(then, now = datetime.now(), interval = "default", show =True, return_ints=True):

    # Returns a duration as specified by variable interval
    # Functions, except totalDuration, returns [quotient, remainder]

    def years():
        return divmod(duration_in_s, 31536000) # Seconds in a year=31536000.

    def days(seconds = None):
        return divmod(seconds if seconds != None else duration_in_s, 86400) # Seconds in a day = 86400

    def hours(seconds = None):
        return divmod(seconds if seconds != None else duration_in_s, 3600) # Seconds in an hour = 3600

    def minutes(seconds = None):
        return divmod(seconds if seconds != None else duration_in_s, 60) # Seconds in a minute = 60

    def seconds(seconds = None):
        if seconds != None:
            return divmod(seconds, 1)   
        return duration_in_s

    def total_duration():
        y = years()
        d = days(y[1]) # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])
        
        di={
            'years':years(),
            'days':days(y[1]),
            'hours':hours(d[1]),
            'minutes':minutes(h[1]),
            'seconds':seconds(m[1])       
        }
        
        if show==True:
            print('Time between dates: ')
            [print('{0}: {1}'.format(k,int(v[0]))) for k,v in di.items()];
        if return_ints==True:
            for k,v in di.items():
                di[k] = int(v[0])
            
        return di
    
    duration = now - then # For build-in functions
    duration_in_s = duration.total_seconds() 
    return total_duration() 

