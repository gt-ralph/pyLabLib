import pytest

import numpy as np
import pandas as pd
import os




##### Basic import tests #####

def test_imports():
    """Test general non-failing of imports"""
    import pylablib.core.fileio.datafile
    import pylablib.core.fileio.dict_entry
    import pylablib.core.fileio.loadfile_utils
    import pylablib.core.fileio.loadfile
    import pylablib.core.fileio.location
    import pylablib.core.fileio.parse_csv
    import pylablib.core.fileio.savefile
    import pylablib.core.fileio.table_stream


##### Table saving tests #####

import pylablib as pll
from pylablib.core.fileio import loadfile, savefile

@pytest.fixture(params=["array","pandas"])
def table_builder(request):
    """Function which returns a table of a given kind (numpy array or pandas table) from data and column names"""
    kind=request.param
    def _builder(data, columns):
        if kind=="array":
            return np.array(data)
        else:
            return pd.DataFrame(data,columns=columns)
    _builder.kind=kind
    return _builder

def compare_tables(t1, t2):
    """Compare two tables (type, shape, content, etc.)"""
    assert type(t1)==type(t2)
    assert isinstance(t1,(np.ndarray,pd.DataFrame))
    assert np.shape(t1)==np.shape(t2)
    assert np.all(t1==t2)
    if isinstance(t1,pd.DataFrame):
        assert np.all(t1.columns==t2.columns)
def test_tables_saving(table_builder, tmpdir):
    """Test saving/loading consistency"""
    save_path=os.path.join(tmpdir,"table.dat")
    kind=table_builder.kind

    data=np.column_stack((np.arange(10),np.zeros(10)))
    columns=["X","Y"]
    table=table_builder(data,columns)
    save_path=os.path.join(tmpdir,"table.dat")
    savefile.save_bin(table,save_path)
    new_table=loadfile.load_bin(save_path,columns=columns,out_type=kind)
    compare_tables(table,new_table)
    if kind==pll.par["fileio/loadfile/csv/out_type"]:
        new_table=loadfile.load_bin(save_path,columns=columns)
        compare_tables(table,new_table)
    if kind=="array":
        new_table=loadfile.load_bin(save_path,columns=2,out_type="array")
        compare_tables(table,new_table)
        new_table=loadfile.load_bin(save_path,out_type="array").reshape((-1,2))
        compare_tables(table,new_table)

    data=np.column_stack((np.arange(10),np.zeros(10),np.arange(10)**2+1j))
    columns=["X","Y","Z"]
    table=table_builder(data,columns)
    savefile.save_csv(table,save_path)
    new_table=loadfile.load_csv(save_path,out_type=kind)
    compare_tables(table,new_table)
    if kind==pll.par["fileio/loadfile/csv/out_type"]:
        new_table=loadfile.load_csv(save_path)
        compare_tables(table,new_table)

    if kind=="pandas":
        data=list(zip(np.arange(10),["t{}".format(i) for i in np.arange(10)]))
        columns=["X","tX"]
        table=table_builder(data,columns)
        savefile.save_csv(table,save_path)
        new_table=loadfile.load_csv(save_path,dtype="generic",out_type=table_builder.kind)
        compare_tables(table,new_table)


##### Table loading tests #####

def test_tables_loading(table_builder):
    """Test loading consistency"""
    kind=table_builder.kind

    data=np.column_stack((np.arange(10),np.zeros(10)))
    columns=["X","Y"]
    table=table_builder(data,columns)
    load_path="core/fileio/table_simple.csv"
    new_table=loadfile.load_csv(load_path,out_type=kind)
    compare_tables(table,new_table)
    if kind==pll.par["fileio/loadfile/csv/out_type"]:
        new_table=loadfile.load_csv(load_path)
        compare_tables(table,new_table)
    

    data=np.column_stack((np.arange(10),np.zeros(10),np.arange(10)**2+1j))
    columns=["X","Y","Z"]
    table=table_builder(data,columns)
    load_path="core/fileio/table_complex.csv"
    new_table=loadfile.load_csv(load_path,out_type=kind)
    compare_tables(table,new_table)
    if kind==pll.par["fileio/loadfile/csv/out_type"]:
        new_table=loadfile.load_csv(load_path)
        compare_tables(table,new_table)










##### Test dictionary #####

@pytest.fixture
def test_dict():
    pt=pd.DataFrame({"C1":["a","b","c"],"C2":[1,2,3+4j]})
    return pll.Dictionary({'1 2 3/  /5': "value",
    'c/f/g': 5,
    'c/f/h': pt,
    'c/f/n': 11,
    'c/b': 5,
    'c/d': 3,
    'c/e': 4,
    'c/n': 6,
    'f/a': np.array([1.,2.,3.]),
    'f/c': [(0, 0), (1, 1), (2, 3)],
    'f/d': r"$\nu_0$",
    '1': "a",
    '[1,2,3]': 2,
    'a': 1,
    'b': 2,
    'some table': pt })

def compare_dicts(d1, d2):
    d1=pll.as_dict(d1,"flat").copy()
    d2=pll.as_dict(d2,"flat").copy()
    for k in list(d1):
        if isinstance(d1[k],(pd.DataFrame,np.ndarray)):
            compare_tables(d1[k],d2[k])
            del d1[k]
            del d2[k]
    assert d1==d2

def test_dictionary_loading(test_dict):
    """Test loading consistency"""
    load_dict=loadfile.load_dict("core/fileio/dict_simple.dat")
    compare_dicts(test_dict,load_dict)

def test_dictionary_saving(test_dict, tmpdir):
    path=os.path.join(tmpdir,"test.dat")
    savefile.save_dict(test_dict,path,use_rep_classes=True)
    load_dict=loadfile.load_dict(path)
    compare_dicts(test_dict,load_dict)