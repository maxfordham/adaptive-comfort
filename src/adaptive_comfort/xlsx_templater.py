import pandas as pd
import os
import xlsxwriter as xw
from adaptive_comfort.utils import jobno_fromdir
import getpass
import datetime
import copy


def get_user():
    return getpass.getuser()


def date():
    return datetime.datetime.now().strftime('%Y%m%d')


# class ToExcel()
#    def __init__(self,data_object,fpth,open=True,print_fpth=False,FileLink_fpth=True):
#       self.lidi = generate_sheet_json(data_object,fpth)
#       self.meta = format_meta(self.lidi)

colours = {
    'ifcAqua': '#2da4a8',
    'ifcPurple': '#b72893',
    'ifcRed': '#e70051',
    'ifcBlue': '#005ca3',
    'mfSalmon': '#F7B799',
    'mfYellow': '#FFFF99',
    'nbsPurple': '#403151'
}


def headertable_fromdict(header):
    header = pd.DataFrame.from_dict(header, orient='index').rename(columns={0: 'Description'})
    di = {
        'sheet_name': '0_Header',
        'xlsx_exporter': 'sheet_table',
        'xlsx_params': None,
        'df': header,
        'description': 'header information that relates to all sheets',
    }
    return di


def load_formats():
    colours = {
        'ifcAqua': '#2da4a8',
        'ifcPurple': '#b72893',
        'ifcRed': '#e70051',
        'ifcBlue': '#005ca3',
        'mfSalmon': '#F7B799',
        'mfYellow': '#FFFF99',
        'nbsPurple': '#403151'
    }
    formats = {
        'ifcBlue': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'white',  # r64 g49 b81 #Color 21
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': colours['ifcBlue'],
            'border': 1},
        'ifcRed': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'white',  # r64 g49 b81 #Color 21
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': colours['ifcRed'],
            'border': 1},
        'ifcPurple': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'black',  # r64 g49 b81 #Color 21
            'bold': False,
            'italic': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': colours['ifcPurple'],  # #F2F2F2 = salmon,
            'border': 1},
        'ifcAqua': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'black',  # r64 g49 b81 #Color 21
            'bold': False,
            'italic': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': colours['ifcAqua'],  # yellow #F8EB2A
            'border': 1},
        'mfSalmon': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'black',  # r64 g49 b81 #Color 21
            'bold': True,
            'italic': False,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': colours['mfSalmon'],  # yellow #F8EB2A
            'border': 1},
        'border': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'black',  # r64 g49 b81 #Color 21
            'bold': False,
            'italic': False,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': 'white',
            'border': 1},
        'readme': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'black',  # r64 g49 b81 #Color 21
            'bold': False,
            'italic': False,
            'text_wrap': True,
            'valign': 'top',
            'align': 'left',
            'fg_color': 'white',
            'border': 0},
        'readme1': {
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': 'black',  # r64 g49 b81 #Color 21
            'bold': False,
            'italic': False,
            'text_wrap': True,
            'valign': 'top',
            'align': 'left',
            'fg_color': 'white',
            'border': 0}
    }
    return formats


def params_ifctemplate():
    '''
    formatting data for bsdd ifc product data template (generated by the IfcDataTemplater app)
    '''
    table_style = 'Table Style Light 2'
    freeze = (1, 3)
    tbox = [
        {
            'row': 1,
            'col': 18,
            'text': '''
                    This is an IFC Building Data Dictionary Product Data Sheet. \n
                    Max Fordham have transposed the columns to rows to make it easier to read. \n
                    Any column with the prefix "Mf" will be ignored. \n
                    Use to Mf examples as a guide, it indicates what information should be filled in for a given product. \n
                    Over time, Mf examples will be completed for all of the products that we take responsibility for specifying. \n
                    \n
                    An "Image" row has also been added. \n
                    Copy and paste an image into this row for your product. \n
                    This Image will then be mapped to a family in your Revit model. \n
                    The "ModelReference" must equal the "TypeMark" in the Revit model.
                    ''',
            'options': {
                'fill': {'color': 'yellow'},
                'width': 800,  # 20
                'height': 160,  # 15
                'font': {'bold': True},
            }
        }
    ]
    formats = load_formats()
    col_formatting = [
        {
            'start_col': 1,
            'end_col': 1,
            'col_width': 40,
            'format': formats['ifcBlue'],
            'options': None,
        },
        {
            'start_col': 2,
            'end_col': 2,
            'col_width': 60,
            'format': formats['ifcBlue'],
            'options': None,
        },
        {
            'start_col': 3,
            'end_col': 3,
            'col_width': 8,
            'format': formats['ifcRed'],
            'options': None,
        },
        {
            'start_col': 4,
            'end_col': 8,
            'col_width': 30,
            'format': formats['ifcRed'],
            'options': {'level': 1, 'hidden': True},
        },
        {
            'start_col': 9,
            'end_col': 9,
            'col_width': 8,
            'format': formats['ifcPurple'],
            'options': None,
        },
        {
            'start_col': 10,
            'end_col': 12,
            'col_width': 30,
            'format': formats['ifcPurple'],
            'options': {'level': 1, 'hidden': True},
        },
        {
            'start_col': 13,
            'end_col': 13,
            'col_width': 8,
            'format': formats['ifcAqua'],
            'options': None,
        },
        {
            'start_col': 14,
            'end_col': 16,
            'col_width': 30,
            'format': formats['ifcAqua'],
            'options': {'level': 1, 'hidden': True},
        },
    ]
    xlsx_params = {
        'freeze': freeze,
        'col_formatting': col_formatting,
        'textbox': tbox,
        'table_style': table_style,
        'hide_grid': True,
    }

    # worksheet = sheet_table(df,
    #                writer,
    #                sheet_name,
    #                **xlsx_params)

    return xlsx_params


def params_readme(df):
    freeze = (1, 1)
    table_style = 'Table Style Light 8'
    formats = load_formats()
    end = len(list(df))
    col_formatting = [
        {
            'start_col': 0,
            'end_col': 0,
            'col_width': 20,
            'format': formats['readme'],
            'options': {'text_wrap': True, 'align': 'left'}
        },
        {
            'start_col': 1,
            'end_col': end,
            'col_width': 30,
            'format': formats['readme1'],
            'options': {'text_wrap': True, 'align': 'left'}
        }
    ]

    tbox = [
        {
            'row': len(df) + 2,
            'col': 1,
            'text': '''
                    This readme tab contains the meta data for the datatables in the other worksheets. \n
                    Each column corresponds to 1no sheet in this excel workbook. 
                    ''',
            'options': {
                'fill': {'color': colours['mfYellow']},
                'width': 800,  # 20
                'height': 160,  # 15
                'font': {'bold': True},
            }
        }
    ]

    xlsx_params = {
        'freeze': freeze,
        'col_formatting': col_formatting,
        'textbox': tbox,
        'table_style': table_style,
        'hide_grid': True,
    }
    return xlsx_params


def create_readme(lidi):
    info = copy.deepcopy(lidi)

    def drop(li,drop):
        try:
            li.pop(drop)
        except:
            pass
        return li

    for l in info:
        l = drop(l, 'df')
        l = drop(l, 'xlsx_exporter')
        l = drop(l, 'xlsx_params')

    n = 0
    df = pd.DataFrame()
    for i in info:
        tmp = pd.DataFrame.from_dict(i, orient='index').rename(columns={0: str(n)})
        df[str(n)] = tmp[str(n)]
        n += 1
    df = df.T
    di = {
        'sheet_name': 'readme',
        'xlsx_exporter': 'sheet_table',
        'xlsx_params': params_readme(df),
        'df': df,
    }
    return di


def create_meta(fpth):
    di = {}
    di['JobNo'] = jobno_fromdir(fpth)
    di['Date'] = date()
    di['Author'] = get_user()
    return di


def generate_sheet_json(data_object, fpth):
    '''
    pass a dataobject and return a list of dicts
    '''

    def default(df, counter):
        di = {
            'sheet_name': 'Sheet{0}'.format(counter),
            'xlsx_exporter': 'sheet_table',
            'xlsx_params': None,
            'df': df,
        }
        counter += 1
        return di, counter
    def add_defaults(di):
        req = {
            'xlsx_exporter': 'sheet_table',
            'xlsx_params': None
        }
        li = list(req.keys())
        for l in li:
            if l not in di.keys():
                di[l]=req[l]
        return di

    counter = 1
    lidi = []
    if type(data_object) == pd.DataFrame:
        # then export the DataFrame with the default exporter (i.e. as a table to sheet_name = Sheet1)
        di, counter = default(data_object, counter)
        di.update(create_meta(fpth))
        lidi.append(di)
    if type(data_object) == list:
        # then iterate through the list. 1no sheet / item in list
        for l in data_object:
            if type(l) == pd.DataFrame:
                # then export the DataFrame with the default exporter (i.e. as a table to sheet_name = Sheet#)
                di, counter = default(l, counter)
                di.update(create_meta(fpth))
                lidi.append(di)
            elif type(l) == dict:
                # then export the DataFrame with the exporter defined by the dict
                l.update(create_meta(fpth))
                l = add_defaults(l)
                lidi.append(l)
            else:
                print('you need to pass a list of dataframes or dicts for this function to work')
    if type(data_object) == dict:
        data_object.update(create_meta(fpth))
        data_object = add_defaults(data_object)
        lidi.append(data_object)
    return lidi


def json_object_to_excel(lidi, fpth):
    # initiate xlsxwriter
    writer = pd.ExcelWriter(fpth, engine='xlsxwriter')

    # get sheet meta data
    info = create_readme(lidi)

    # create metadata to make the readme worksheet
    lidi.insert(0, info)

    # create the worksheets
    for d in lidi:
        if type(d['xlsx_params']) == dict:
            sheet_table(d['df'], writer, d['sheet_name'], **d['xlsx_params'])
        else:
            sheet_table(d['df'], writer, d['sheet_name'])

    # save and close the workbook
    writer.save()
    return fpth


def sheet_table(df,
                writer,
                sheet_name,
                freeze=(1, 1),
                col_formatting=None,
                table_style='None',
                hide_grid=True,
                textbox=None):
    '''
    an xlsxwriter template for writing a pd.DataFrame to an excel sheet
    as a table with customisable formatting. 
    this is the backbone sheet template that is used by all the other ones. 

    Args:
        df (pd.DataFrame):
        writer (class): xlsxwriter object
        sheet_name (string): 
    ** Kwargs:
        freeze (tuple): gives coordinates of freeze panes (x,y)
        col_formatting (list of dicts): list of dicts which define column formatting 
            each dict defines the formatting for a given col or range of cols
        table_style (string): named Excel table style
        hide_grid (bool): show / hide gridlines
        textbox (list of dicts): list of dicts which define textbox requirements
            each dict specifies requirements for 1no text box
    
    Returns:
        worksheet (class): xlsxwriter object that defines an excel worksheet output. 
            another can then compile many sheets in a single output
    '''

    df.to_excel(writer, sheet_name)
    # get sheets to add the tables
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    if hide_grid == True:
        worksheet.hide_gridlines()

    # the range in which the table is
    # from xlsxwriter.utility import xl_range
    end_row = len(df.index)
    end_column = len(df.columns)
    cell_range = xw.utility.xl_range(0, 0, end_row, end_column)

    # Using the index in the Table
    df = df.reset_index()
    header = [{'header': di} for di in df.columns.tolist()]
    worksheet.add_table(cell_range,
                        {'style': table_style,
                         'header_row': True,
                         'first_column': True,
                         'columns': header})


    # set col formatting
    # https://xlsxwriter.readthedocs.io/worksheet.html
    # set_column(first_col, last_col, width, cell_format, options)
    # col_formatting is a list of dicts. each dict defines the formatting for a given col or range of cols
    if col_formatting != None:
        for col in col_formatting:
            f = workbook.add_format(col['format'])
            worksheet.set_column(col['start_col'], col['end_col'], col['col_width'], f, col['options'])

    # Add a header format.
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        # 'fg_color': '#D7E4BC',
        'border': 1})
    worksheet.set_row(0, 80, header_format)

    # freeze header row and index    
    if freeze != None:
        worksheet.freeze_panes(freeze[0], freeze[1])

        # insert textbox(s)
    if textbox != None:
        for t in textbox:
            worksheet.insert_textbox(t['row'], t['col'], t['text'], t['options'])

    return worksheet


def main(data_object,
         fpth,
         open=True,
         print_fpth=False,
         FileLink_fpth=True):
         
    """
    the name "main" is DEPRECATED! USE "to_excel" INSTEAD
    """
    print('the name "main" is DEPRECATED! USE "to_excel" INSTEAD')
    lidi = generate_sheet_json(data_object, fpth)
    json_object_to_excel(lidi, fpth)
    if open == True:
        open_file(fpth)
    if print_fpth == True:
        print(fpth)
    '''if FileLink_fpth == True:
        from IPython.display import FileLink
        FileLink(fpth)'''
    return fpth
    
def to_excel(data_object,
         fpth,
         open=True,
         print_fpth=False,
         FileLink_fpth=True):
    """
    Example:
        di = {
            'sheet_name': 'IfcProductDataTemplate',
            'xlsx_exporter': 'sheet_table',
            'xlsx_params': params_ifctemplate(),
            'df': df1,
        }
        to_excel(li, fpth, open=True, print_fpth=False, FileLink_fpth=True)
    """
    lidi = generate_sheet_json(data_object, fpth)
    json_object_to_excel(lidi, fpth)
    if open == True:
        open_file(fpth)
    if print_fpth == True:
        print(fpth)
    '''if FileLink_fpth == True:
        from IPython.display import FileLink
        FileLink(fpth)'''
    return fpth
    


if __name__ == '__main__':
    if __debug__ == True:
        wdir = os.path.join(os.environ['mf_root'],r'MF_Toolbox\dev\examples\xlsx_templater')
        fpth = wdir + '\\' + 'bsDataDictionary_Psets.xlsx'
        df = pd.read_excel(fpth)
        #fpth = wdir + '\\' + 'bsDataDictionary_Psets-processed.xlsx'
        df1 = pd.read_excel(fpth,sheet_name='1_PropertySets')
        di = {
            'sheet_name': 'IfcProductDataTemplate',
            'xlsx_exporter': 'sheet_table',
            'xlsx_params': params_ifctemplate(),
            'df': df1,
        }
        li = [df, di]
        fpth = wdir + '\\' + 'bsDataDictionary_Psets-out.xlsx'
        to_excel(li, fpth, open=True, print_fpth=False, FileLink_fpth=True)
        print('fasdf')
