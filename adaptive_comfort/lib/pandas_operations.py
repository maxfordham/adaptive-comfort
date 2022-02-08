# Pandas operations

"""
See Also:
        list of metadata available from os.stat(fdir): https://docs.python.org/3/library/os.html
        write docstrings like google: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
        Google python code style guide: https://github.com/google/styleguide/blob/gh-pages/pyguide.md
        https://towardsdatascience.com/23-great-pandas-codes-for-data-scientists-cca5ed9d8a38
"""

import pandas as pd
import numpy as np
import os

try:
    import pandas.io.formats.excel
except:
    pass
# from IPython.display import display, Image, FileLink, FileLinks
try:
    from IPython.display import FileLink, Markdown
except:
    pass
# import seaborn as sns
# import matplotlib.pyplot as plt
import xlsxwriter as xw
from xlsxwriter.utility import xl_rowcol_to_cell
from file_operations import open_file

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt


def diff(li1, li2): 
    '''
    find the difference between 2 lists
    '''
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2] 
    return li_dif 

def graph(formula, x_range, plot=True, returndf=True):
    """
    generic graph plotter.
    pass a  and a range to plot over
    and returns a dataframe.
    Args:
        formula(str): formula as a string
        x_range(np.arange): formula as a string
        **plot(booll:
        **returndf(bool)
    Returns:
        df(pd.DataFrame):
    """
    try:
        x = np.array(x_range)
        y = eval(formula)
    except:
        li = []
        y = [li.append(eval(formula)) for x in x_range]
        x = x_range
        y = np.array(li)
    try:
        df = pd.DataFrame({'x': x, 'y': y}, columns=['x', 'y'])
    except:
        df = {'x': x, 'y': y}
    if plot == True:
        plt.plot(x, y)
        plt.show()
    if returndf == True:
        return df


def construct_query(column, filter_str, boolean_operator=None):
    """
    creates a filter string query from user input form
    """
    if boolean_operator:
        if boolean_operator.lower() == "and" or boolean_operator.lower() == "or":
            return "{0} {1}.str.contains(\'(?i){2}\') ".format(boolean_operator.lower(), column, filter_str)
        else:
            return "{0} ~{1}.str.contains(\'(?i){2}\') ".format("and", column, filter_str)
    else:
        return "{0}.str.contains(\'(?i){1}\') ".format(column, filter_str.lower())
        return "{0} == \'{1}\' ".format(column, filter_str)


def remove_spcs_from_colnms(df):
    """
    removes any spaces from all of the pandas column names
    """
    li = list(df)
    li1 = [l.replace(' ', '') for l in li]
    df = df.rename(columns=dict(zip(li, li1)))
    return df


def display_md_df(df, reset_index=True):
    if reset_index:
        display(Markdown(df.reset_index().to_markdown()))
    else:
        display(Markdown(df.to_markdown()))


def records_to_df(li, header=True):
    """
    converts list of lists to df
    """
    if header == True:
        df = pd.DataFrame.from_records(li[1:], columns=li[0])
    else:
        df = pd.DataFrame.from_records(li)
    return df


def df_tonumeric(df, col_exceptions=None, print_exceptions=False, rnd=None):
    """
    Function tries to make every column in a dataframe numeric.
    if print_exceptions=True it will print a list of non-numeric
    columns in the dataframe.

    Args:
        df(pd.DataFrame):
        ** print_exceptions(bool): False
        ** rnd (int): None. Input decimal to round to.
        ** col_exceptions (list): list of cols not to make numeric
    Return:
        df(pd.DataFrame): as df but with numeric cols

    """
    cols = list(df)
    if type(col_exceptions) == list:
        cols = diff(cols, col_exceptions)
    for col in cols:
        try:
            df[col] = pd.to_numeric(df[col])
            if round != None:
                df[col] = df[col].round(rnd)
        except:
            if print_exceptions != False:
                print(col + ' not turned to numeric')
    return df


def exportMFExcel(dataframe, fname):
    """
    Saves a dataframe to an excel spreadhseet with some nice default formatting.

    """

    pandas.io.formats.excel.header_style = None

    if ".xlsx" in fname:
        filename = fname
    else:
        filename = fname + ".xlsx"
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    dataframe.to_excel(writer, sheet_name='Sheet1', startrow=0)

    workbook = writer.book
    worksheet = workbook.worksheets()[0]

    header_format = workbook.add_format({'text_wrap': False})
    header_format.set_border(True)
    header_format.set_bold(True)
    header_format.set_bg_color('black')
    header_format.set_font_color('white')

    worksheet.set_row(0, None, header_format)

    worksheet.set_column("A:A", None, header_format)

    content_format = workbook.add_format({'text_wrap': True})
    content_format.set_border(True)
    content_format.set_bold(False)
    content_format.set_bg_color('white')
    content_format.set_font_color('black')

    for i in range(0, len(dataframe)):
        # worksheet.set_row(i+1, None, content_format)
        pass

    worksheet.freeze_panes(1, 1)

    writer.save()
    writer.close()


# Function: write pandas dataframe to xlsx
def df_toexcel(df, fpth):
    """
    export pandas df to excel

    Args:
        fpth(str): filepath to export to
        df(pd.DataFrame or list of pd.DataFrames):
            dataframes to export
            if list passed each df is a new sheet
    Returns:
        fpth(FileLink): filelink to created excel
    """
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(fpth, engine='xlsxwriter')

    if type(df) == list:

        # Convert the dataframe to an XlsxWriter Excel object.
        end = len(df)
        for n in range(0, end):
            nm = 'Sheet' + str((n + 1))
            df[n].to_excel(writer, sheet_name=nm)
    else:
        df.to_excel(writer, sheet_name='Sheet1')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return FileLink(fpth)


def fractional_array(array):
    """
    pass an array and return a fractional version of the array
    """
    fract_array = array / array.sum()
    return fract_array


def add_line_break(*params):
    """
    add line break between params
    """
    br = '\n'
    tag = ''
    for param in params:
        tag = tag + param + br

    return tag


def normalize_array(array):
    """
    pass an array and return a normalized version of the array

    Reference:
        https://chrisalbon.com/python/data_wrangling/pandas_normalize_column/
    """
    from sklearn import preprocessing
    # Create a minimum and maximum processor object
    min_max_scaler = preprocessing.MinMaxScaler()
    # Create an object to transform the data to fit minmax processor
    norm_array = min_max_scaler.fit_transform(array)
    return norm_array


def col_to_str(df, cols):
    """convert listed cols in df to str"""
    if type(cols) == list:
        for col in cols:
            df[col] = df[col].astype(str)
    else:
        df[cols] = df[cols].astype(str)
    return df


def duplicate_rows_by_param(df, param_col, ref_param, new_params):
    """
    duplicate rows which contain a specific val in a column
        used for copying floor parameters

    Args:
        df (pd.DataFrame):
        param_col (str): column index for col containing the ref parameter
        ref_param (?): the value used to filter rows for a gven 'param_col'
        new_params (list): when the rows are copied the "ref_param" is updated
                   with new_param in new_params

    Returns:
        df (pd.DataFrame): with rows added

    Example:
        ref_flr='01'
        new_flrs=['02','03']
        duplicate_rows_by_param(df2,'flr',ref_flr,new_flrs)
        >>> df2 #copies data from floor 1 to new floors 2&3
    """

    df_temp = df[df[param_col] == ref_param]
    for new_param in new_params:
        # df_temp[param_col]=new_param #this needs fixing
        df_temp.loc[:, param_col] = new_param  # this needs fixing
        df = df.append(df_temp, ignore_index=True)

    return df


def replace_str_in_series(df, cols, string, val):
    """
    replace string in column
    Args:
        df (pd.DataFrame):
        cols (str): string(list) of col name(s)
        string (str): string to search for in series cells
        val (?): value to replace string with
    Returns:
        df (pd.DataFrame):
    """

    if type(cols) == list:
        for col in cols:
            df[col].replace(regex=True, inplace=True, to_replace=string, value=0)
    else:
        df[cols].replace(regex=True, inplace=True, to_replace=string, value=0)
    return df


def fillna(df, cols):
    """fill na for listed col names within a df"""
    if type(cols) == list:
        for col in cols:
            df[col] = df[col].fillna(0)
    else:
        df[cols] = df[cols].fillna(0)
    return df


def col_to_num(df, cols):
    """convert listed cols in df to numeric"""
    if type(cols) == list:
        for col in cols:
            df[col] = df[col].astype(float)
    else:
        df[cols] = df[cols].astype(float)
    return df


def list_df_datatypes(df):
    """
    create a ref_dataframe that lists all column names of the
    input 'df' and defines the datatype of that column

    Args:
        df(pd.DataFrame): dataframe you want type data for

    Returns:
        df_types (pd.DataFrame):
            name: column name of input df
            type: datatype of column
    """

    cols = list(df)
    end = len(cols)
    columns = ['name', 'type']
    df_types = pd.DataFrame(columns=columns)
    df_types.name = list(range(0, end))
    df_types.type = list(range(0, end))

    for n in range(0, end):
        df_types.name[n] = cols[n]
        df_types.type[n] = df[cols[n]].dtype

    return df_types


def list_to_csv(list_name, filename):
    """
    function takes a dict list a specified
    filename and copies the list to the filename
    location
    """

    end = len(list_name)  # define columns to be populated in main database [df_main]

    columns = ['col1']
    df = pd.DataFrame(columns=columns)  # create df to populate
    df.col1 = list(range(0, end))
    df.col1 = pd.DataFrame.from_dict(list_name)  # copy list to df
    df.to_csv(filename, encoding='utf-8', index=False, header=False)  # save list to .csv file
    return df


def srch_tgs(df, clmn_nm, srch_tg, clmn_rtrn=None):
    """
    name:
        20180929~3870~dev~pyfnctn~jg~pandas indx mtch fnctn~B~0
    tags:
        index, match, search, tags, list, cross-reference
    Args:
        df (pd.DataFrame)=dataframe, containing a column with a tag to search for
        clmn_nm (string)=the column you want to search for a specific "srch_tg"
        srch_tg (string)=a string that you want to find in the column ['clmn_nm']
    Keyword Args:
        clmn_rtrn (string)=the column you want to output is ['clnm_nm']
            contains 'srch_tg'

    returns:
        if clmn_rtrn = None:
            li (list): a list of index values for the rows of the df where
            df['clmn_nm'] contained the search tag "srch_tg"
        elif: clmn_rtrn = var:
            li (list): a list of 'clmn_rtrn' values for the rows of the df
            where df['clmn_nm'] contained the search tag "srch_tg"

    """
    df[clmn_nm] = df[clmn_nm].astype(str)
    end = len(df)
    tag = srch_tg
    li = []
    for n in range(0, end):
        if tag in df.iloc[n][clmn_nm]:
            li.append(df.iloc[n].name)  # then return index

    if clmn_rtrn == None:
        return li
    else:
        return df.loc[li][clmn_rtrn]


def list_to_df(list_name, col_nm=None):
    """
    nm: 20180808~3870~data~pyfnctn~jg~list_to_df~A~0

    args:
        list_name (string), to parse
        **col_nm (string): column name of the parsed list

    Returns:
        pandas dataframe array of the list
    """

    columns = ['col1']
    df = pd.DataFrame(columns=columns)
    if list_name == []:
        df = df
    else:
        end = len(list_name)
        df.col1 = list(range(0, end))
        # copy list to df
        df.col1 = pd.DataFrame.from_dict(list_name)

    if col_nm != None:
        df = df.rename(columns={'col1': col_nm})

    return df


def find_nearest(array, value):
    """
    Name:
        20180804~3870~data~pyfnctn~jg~find_nearest - matches closest num
            in array to lookup num~A~0
    Args:
        array(array):
        value(numberic value)
    Returns:
        the value in the array that is closest to the lookup value
    Reference:
        https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array/2566508
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def df1_merge_df2(df1, key1, df2, key2):
    """
    merges 2no dataframes. uses "find_nearest" function to create a new column in
    df1 that matches exactly to the column in df2, allowing for approximate matches.

    Args:
        df1(pd.DataFrame):
        key1(str): col name used as merge key for df1
        df2(pd.DataFrame):
        key2(str): col name used as merge key for df2

    Returns:
        df3(pd.DataFrame): df2 merged onto df1

    Requires:
        def find_nearest(array, value):
    """
    df1['key'] = 0
    col_i = df1.columns.get_loc("key")
    df2['key'] = df2[key2]
    for n in range(0, len(df1)):
        df1.iloc[n, col_i] = find_nearest(df2[key2], df1[key1][n])
    df_merge = pd.merge(df1, df2, on='key')
    return df_merge


def map_files_to_df(srch_fol, df, col_mtch):
    """
    function looks in 'srch_fol' folder and creates a list of filenames and dirs.
    a new column (fpth) is added to df and if files have the same name as the
    value in df[col_mtch] then the the fpth is added to df['fpth'] in the correct row.

    Args:
        srch_fol(str): folder directory to list files (not recursive)
        df(pd.DataFrame):
        col_mtch (str): column name. contains strings that are expected to match
                 filenames

    Returns:
        df_merge(pd.DataFrame): df with df['fpth'] added with mapped directories
    """

    files = os.listdir(srch_fol)
    fpth = [srch_fol + '\\' + file for file in files]
    files = [os.path.splitext(file)[0] for file in files]
    df_files = list_to_df(fpth, 'fpth')
    df_files[col_mtch] = list_to_df(files, col_mtch)

    df_merge = pd.merge(df, df_files, on=col_mtch)

    return df_merge


def rename_fnms_from_df_vals(df, old_dir, new_fnm):
    """
    pass a dataframe with file-directories in column df[old_dir].
    function renames the files with the values in column df[new_fnm]
    and updates the df[old_dir] directories with the new directories.

    Args:
        df (pd.DataFrame):
        old_dir(str): col name in df with full directory
        new_fnm(str): col name with new proposed new filename
            note. it doesn't have folder dir or file extension

    Returns:
        df (pd.DataFrame): with the values within the old_dir
            column now updated to the new (renamed)directories.

    """

    df['old_nm'] = 0
    df['new_pth'] = 0

    # check if new_fnm is unique
    # if len(df.new_fnm.unique())
    for index, row in df.iterrows():
        df.loc[index, 'old_nm'] = os.path.splitext(os.path.basename(df.loc[index, old_dir]))[0]
        df.loc[index, 'new_pth'] = os.path.dirname(df.loc[index, old_dir])
        df.loc[index, 'new_pth'] = df.loc[index, 'new_pth'] + '\\' + df.loc[index, new_fnm] + \
                                   os.path.splitext(os.path.basename(df.loc[index, old_dir]))[1]
        try:
            os.replace(df.loc[index, old_dir], df.loc[index, 'new_pth'])
        except:
            print('error renaming {0} ->'.format(df.loc[index, old_dir],df.loc[index, 'new_pth']))

    df[old_dir] = df['new_pth']
    del df['old_nm']
    del df['new_pth']
    return df


def del_cols(df, cols):
    """delete a pandas column if it is in
    the column index otherwise ignore it. """
    if type(cols) == str:
        try:
            del df[cols]
        except:
            print(cols + ' is not in column index')
    else:
        for col in cols:
            try:
                del df[col]
            except:
                print(col + ' is not in column index')
    return df


def del_matching(df, string):
    """
    deletes columns if col name matches string
    """
    matching = [s for s in list(df) if string in s]
    df = del_cols(df, matching)
    return df


def remove_str_from_colnames(df, old_str, new_str=''):
    """
    pass a df and rename all of the col names that
    contain "old_str" with "new_str".

    Args:
        df (pd.DataFrame)
        old_str (str)
        new_str (str)

    Returns:
        df (pd.DataFrame): with renamed cols

	Requires:
		from mf_modules.pandas_operations import list_to_df
    """
    nms = list_to_df(list(df), 'old')
    nms['new'] = nms.old.str.replace(old_str, new_str)
    nms = nms.set_index('old').to_dict()['new']
    df = df.rename(columns=nms)
    return df


def cols_present(df, DEFAULTCOLS):
    """
   Returns columns that are present from the DEFAULTCOLS in a dataframe.
    """
    return [x for x in DEFAULTCOLS if x in df.columns]


def filter_pd_cols(df, string):
    """
    filters cols in df based on string matching

    Code:
        matching=[s for s in list(df) if string in s]
        return df[matching]
    """
    matching = [s for s in list(df) if string in s]
    return df[matching]


def process_mf_pdt(fpth):
    """
    Requires:
        diff(cols1, cols)
        filter_index(out)

    """

    xl = pd.ExcelFile(fpth)
    # xl.sheet_names  # see all sheet names
    pr = pd.read_excel(xl, sheet_name=0)

    # thresh = 5 imples 5th row in (where the user-input product reference begin)
    # any params that do not have user entries in the 1st column are therefore ignored
    # pr=pr.dropna(thresh=5).set_index('ModelReference')
    pr = pr.set_index("ModelReference").T

    # pr = pr[pd.notna(pr["Name"])] #ignore ones that do not have a name defined.
    pr = pr[~pr.index.str.contains('#', na=False)]
    pr = filter_pr_index(pr)

    from mf_modules.file_operations import fnm_from_fpth
    fnm = fnm_from_fpth(fpth, drop_extension=True)
    cat = fnm.split('-')[0]
    nm = fnm.split('-')[1]
    if nm[-1:] == 's':
        nm = nm[:-1]
    pr['Category'] = cat
    pr['Name'] = nm
    # table_toexcel(pr,'test.xlsx')
    return pr


def process_mf_pdt1(fpth):
    """
    Requires:
        diff(cols1, cols)
        filter_index(out)

    """

    xl = pd.ExcelFile(fpth)
    # xl.sheet_names  # see all sheet names
    pr = pd.read_excel(xl, sheet_name='Product information_MfReformat')

    # thresh = 5 imples 5th row in (where the user-input product reference begin)
    # any params that do not have user entries in the 1st column are therefore ignored
    # pr=pr.dropna(thresh=5).set_index('ModelReference')
    pr = pr.set_index("ModelReference").T

    # pr = pr[pd.notna(pr["Name"])] #ignore ones that do not have a name defined.
    pr = pr[~pr.index.str.contains('#', na=False)]
    pr = filter_pr_index(pr)

    return pr


def filter_pr_index(pr_df, filter_mf=True):
    """
    searches Pr index for and extracts only the user-added product references
    by comparing the list of references with the standard NBS references.

    Args:
        pr_df (pd.DataFrame): dataframe of product data. required cols:
            'index' : product reference

    Returns
        filtered_pr_df (pd.DataFrame): only the user-added entries from pr_df
    """

    li1 = pr_df.index.tolist()
    if filter_mf:
        mf = []
        x = "Mf"
        [mf.append(l) for l in li1 if x in l]
        li1 = (list(set(li1) - set(mf)))

    x = 'Enter'
    ent = []
    [ent.append(l) for l in li1 if x in l]
    li1 = (list(set(li1) - set(ent)))

    li2 = [
        '0',
        'index',
        'LOI',
        'Reference',
        'A reference for the system or product',
        'Enter product 001',
        'Enter product 002',
        'Enter product 003',
        'Enter further items'
    ]

    diff_2 = (list(set(li1) - set(li2)))

    return pr_df.loc[diff_2]


def copy_from_dfOld_to_dfNew(dfOld, dfNew):
    """
    copies data from an old dataframe to a new one.
    requires that dfOld and dfNew have the same index
    and column headings.

    Args:
        dfOld(pd.DataFrame):old df
        dfNew(pd.DataFrame):new df
    Returns:
        dfNew(pd.DataFrame): populated with data from dfOld
    """
    cols = list(dfNew)
    for col in cols:
        try:
            dfNew[col] = dfOld[col]
        except:
            print(col + ' not in dfOld dataframe')
    return dfNew


def read_excel_find_header(fpth, sheet_name='Sheet1'):
    """
    finds header row in 0th column and makes it the header row
    uses multiindex:
        index_col = (0,1)
    """
    header_row = pd.read_excel(fpth, sheet_name=sheet_name).reset_index().iloc[:, 0].tolist().index('header_row') + 1
    df = pd.read_excel(fpth, header=header_row)  # ,index_col=(1,2)

    return df


def map_dict_to_pdDf(map_dict, map_col):
    """
    creates a new np.array ("new_col") from "map_dict" values
    by mapping the values of "map_col" to the keys of "map_dict"

    Reference:
        http://cmdlinetips.com/2018/01/how-to-add-a-new-column-to-using-a-dictionary-in-pandas-data-frame/
    """
    #
    new_col = map_col.map(map_dict)
    return new_col


def split_col(df, col_nm, di='', pat='_'):
    """
    splits a column into multiple using string split and merges back to the main df

    Ref:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.split.html
    Args:
        df(pd.DataFrame):
        col_nm(str): column name to str split
        di(dict): dict to define how to rename split columns
        **pat(str)='_': pattern to split on
    Returns:
        df with additional columns
    Example:
        #example name in column
        #A_00_XX_A01_Storage
        di={0:'BlockCode',1:'Level',2:'TM46Category',3:'SpaceId',4:'SpaceType'}
        col_nm='Name'
        split_col(df,col_nm,di,pat='_')
    """

    try:
        nm = df.index.name
        if str(type(nm)) != "<class 'NoneType'>":
            df = df.reset_index(drop=False)
    except:
        pass
    tmp = df[col_nm].str.split(pat, expand=True)
    if di != '':
        tmp = tmp.rename(columns=di)
    df[list(tmp)] = tmp
    try:
        df = df.set_index(nm)
    except:
        pass
    return df


def df_from_list_of_dicts(list_of_dicts,
                          li_of_keys=["@id", "@zoneIdRef", "@conditionType", "@buildingStoreyIdRef", "Name", "Area",
                                      "Volume", "CADObjectId", "TypeCode"]):
    """
    extract listed di items from a list of dicts.
    build list of extracted dicts into dataframe.

    Example:
        list_of_dicts=gbjson["gbXML"]["Campus"]["Building"]["Space"]
        li_of_keys=["@id","@zoneIdRef","@conditionType","@buildingStoreyIdRef","Name","Area","Volume","CADObjectId","TypeCode"]
        df=df_from_list_of_dicts(list_of_dicts,li_of_keys=li_of_keys)
    """
    df = pd.DataFrame(columns=li_of_keys)
    for li_di in list_of_dicts:
        di = {}
        for l in li_of_keys:
            try:
                di[l] = li_di[l]
            except:
                di[l] = 'na'
        df = df.append(di, ignore_index=True)
    return df


def pdcol_as_percent(df, colnms):
    """
    reformat column as percentage
    """
    for col in colnms:
        df[col] = pd.Series(["{0:.2f}%".format(val * 100) for val in df[col]], index=df.index)
    return df


def split_col(df, col_nm, col_rename_di=None, pat='_'):
    """
    splits a column into multiple using string split and merges back to the main df

    Ref:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.split.html
    Args:
        df(pd.DataFrame):
        col_nm(str): column name to str split
        col_rename_di(dict): dict to define how to rename split columns
        **pat(str)='_': pattern to split on
    Returns:
        df with additional columns
    Example:
        #example name in column
        #A_00_XX_A01_Storage
        di={0:'BlockCode',1:'Level',2:'TM46Category',3:'SpaceId',4:'SpaceType'}
        col_nm='Name'
        split_col(df,col_nm,di,pat='_')
    """

    try:
        nm = df.index.name
        if str(type(nm)) != "<class 'NoneType'>":
            df = df.reset_index(drop=False)
    except:
        pass
    tmp = df[col_nm].str.split(pat, expand=True)
    if col_rename_di != None:
        tmp = tmp.rename(columns=col_rename_di)
    df[list(tmp)] = tmp
    try:
        df = df.set_index(nm)
    except:
        pass
    return df


def decipher_pd_cols(df, delimiter=':', rename_di={0: 'floor', 1: 'ld_type'}):
    """
    creates a new dataframe with data extracted from the column headings
    Args:
        df (pd.DataFrame):
        delimiter: split column string on this character
        rename_di: give the split column indexes names

    Returns:
        df_cols (pd.DataFrame):

    """
    cols = list(df)
    df_cols = list_to_df(cols, col_nm='col_nm')
    df_cols = df_cols.merge(df_cols['col_nm'].str.split(delimiter, expand=True).rename(columns=rename_di),
                            right_index=True, left_index=True)
    return df_cols


def pd_replace_vals_in_col(df, val_grouping_di):
    """
    groups values from a given column
    Args:
        df (pd.DataFrame):
        val_grouping_di: defines how to group vals together from a
            given column. e.g.
            val_grouping_di={
                        'colnm':{
                            'new_val':[
                                'old_val0',
                                'old_val1',
                                'old_val2'
                            ]
                        }
                    }

    Returns:
        df (pd.DataFrame): with grouping applied
    """
    for colnm, rename_di in val_grouping_di.items():
        for new_val, old_vals in rename_di.items():
            for old_val in old_vals:
                df[colnm] = df[colnm].str.replace(new_val, old_val)
    return df


def pd_datetime_outputs(ser_dt,
                        request_di=None,
                        drop_datetime=True,
                        weekend_bool=True):
    """

    Args:
        ser_dt (series): of pd.datetime objects
        request_di (dict): defining what output you want
            default = {'weekday': '%A', 'month': '%B', 'hour': '%H'}
            key = column date
            value = format of output (see reference)
        drop_datetime (bool): drop pd.datetime input?
        weekend_bool (bool): creates a bool column to say if its the weekend
            requires 'weekday':'%A' or 'weekday':'%w' to be passed in request_di

    Reference:
        #https://medium.com/@deallen7/managing-date-datetime-and-timestamp-in-python-pandas-cc9d285302ab

    Returns:
        df (pd.DataFrame): columns = list(request_di.keys()) + 'weekend_bool' if selected

    Example:
        ser_dt = pd.date_range(start='2020-03-13', end='2020-03-14', freq='6H')
        pd_datetime_outputs(ser_dt)

    """
    if request_di == None:
        request_di = {'weekday': '%A', 'month': '%B', 'hour': '%H'}
    else:
        pass
    wknd_bl = {
        'dayofweek_wrd': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'dayofweek_no': [0, 1, 2, 3, 4, 5, 6],
        'weekend_bool': [False, False, False, False, False, True, True]
    }
    wknd_bl = pd.DataFrame.from_dict(wknd_bl)
    cols = list(request_di.keys())
    df = pd.DataFrame()
    df['datetime'] = ser_dt
    for k, v in request_di.items():
        df[k] = df['datetime'].dt.strftime(v)
        if weekend_bool == True:
            if v == '%A':
                di = wknd_bl.set_index('dayofweek_wrd')['weekend_bool'].to_dict()
                df['weekend_bool'] = df[k].map(di)
                cols.append('weekend_bool')
            elif v == '%w':
                di = wknd_bl.set_index('dayofweek_no')['weekend_bool'].to_dict()
                df['weekend_bool'] = df[k].map(di)
                cols.append('weekend_bool')
            else:
                pass
    if drop_datetime == True:
        df = df[cols]
    return df


def pd_drop_zeros(df):
    """
    drop any column that only contains zeros

    Args:
        df(pd.DataFrame)
    Returns:
        df(pd.DataFrame): without columns with zeros only

    Reference:
        https://stackoverflow.com/questions/21164910/how-do-i-delete-a-column-that-contains-only-zeros-in-pandas
    """
    return df.loc[:, (df != 0).any(axis=0)]


def str_match(li, col_nm='heat_source', match=['heat source 1', 'heat source 2', 'heat source 3', 'heat source 4']):
    """
    pass a list and another list of string to match in the first list and and return a mapped dataframe of matches.
    intended use is when there is 1 to 1 mapping

    Args:
        li (list):
        col_nm (str): resulting column name in df
        match (list): list of strings to match with li

    Returns:
        df (pd.DataFrame)
    """
    _li = []
    for l in li:
        tmp = [m for m in match if m in l]
        if len(tmp) == 1:
            _li.append(tmp[0])
        elif len(tmp) == 0:
            _li.append('na')
        else:
            _li.append(tmp[0])
            print('multiple matches for {0}'.format(s))
    _di = dict(zip(li, _li))
    di = {col_nm: _di}
    return pd.DataFrame.from_dict(di)

if __name__ == '__main__':
    if __debug__:
        # import os
        fpth = os.path.join(os.environ['mf_root'],
                            r'MF_Toolbox\dev\examples\img_from_xl\eg0-img_left\Pr_70_60_36_73-Radiators.xlsx')
        df = pd.read_excel(fpth)
        df1 = df.iloc[0:4, :]
        di = {}
        di['test1'] = df1
