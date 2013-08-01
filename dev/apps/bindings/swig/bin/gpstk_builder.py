"""GPSTk module __init__.py generator and build finisher.

Usage:
    python module_builder.py
    This runs the program and builds to the gpstk folder to the system
    default path for python. The path is defined by:
        from distutils.sysconfig import get_python_lib
        print(get_python_lib())
    This may require extra permissions.


If on a Unix-like platform:
    sudo python module_builder.py /usr/local/lib/python2.7/dist-packages
    This runs the program and builds to /usr/local/lib/python2.7/dist-packages

    python module_builder.py ~/.local/lib/python2.7/site-packages
    This runs the program and builds to ~/.local/lib/python2.7/site-packages/

If on Windows:
    python module_builder.py C:\Python27\Lib\site-packages
    This runs the program and builds to C:\Python27\Lib\site-packages\
"""


import argparse
import distutils.dir_util
import distutils.sysconfig
import inspect
import os
import shutil
import sys


# Any object that is exactly a string in this list will be ignored
ignore_exact = [
'asString',
'cvar',
'DisplayExtendedRinexObsTypes',
'DisplayStandardRinexObsTypes',
'FFData',
'Rinex3NavBase',
'Rinex3ObsBase',
'RinexClockBase',
'RinexMetBase',
'RinexNavBase',
'RinexObsBase',
'SEMBase',
'SP3Base',
'SwigPyIterator',
'YumaBase',
]


# Any object that contains a string in this list will be ignored
ignore_patterns = [
'EngNav_',
'FileStore',
'ObsID_',
'ObsIDInitializer',
'OrbElem_',
'Position_',
'PRSolution2_',
'RinexMetHeader_',
'RinexObsHeader_',
'Stream',
'swigregister',
'TabularSatStore_',
'TimeTag_',
'TropModel_',
'VectorBase',
]


# submodule_name -> (list of exact names, list of pattern names)
submodules = {
    'cpp' : (
        ['seqToVector', 'vectorToSeq', 'cmap', 'mapToDict', 'dictToMap'],
        ['vector_', 'map_', 'set_']),
}


def should_be_added(name):
    for pattern in ignore_patterns:
        if pattern in name:
            return False
    if name in ignore_exact:
        return False
    if name[:1] == '_':
        return False
    else:
        return True


def main():
    if len(sys.argv) >= 2:
        out_dir = os.path.join(sys.argv[1], 'gpstk')
    else:
        out_dir = distutils.sysconfig.get_python_lib()

    try:
        # remove any init files already there
        os.remove(out_dir + '/__init__.py')
        os.remove(out_dir + '/cpp/__init__.py')
        os.remove(out_dir + '/constants/__init__.py')
        os.remove(out_dir + '/exceptions/__init__.py')
    except:
        pass

    # add seperator at the end if one is missing
    if out_dir[-1] != '/' and out_dir[-1] != '\\':
        out_dir = out_dir + '/'

    print 'Placing gpstk build files in', out_dir

    # saves all files to move, some are added later
    files_to_move = ['gpstk_pylib.py', '__init__.py']

    # Create gpstk __init__.py file
    import gpstk_pylib
    namespace = dir(gpstk_pylib)
    out_file = open('__init__.py', 'w')
    out_file.write('"""The GPS Toolkit - an open source library to the satellite navigation community.\n"""\n')
    out_file.write('### This file is AUTO-GENERATED by module_builder.py. ###\n\n')

    def add_to_submodule(object_name, submodule_name):
        if not os.path.exists(out_dir + '/' + submodule_name + '/'):
            os.makedirs(out_dir + '/' + submodule_name + '/')
        f = open(out_dir + '/' + submodule_name + '/__init__.py', 'a')
        f.write('from ..gpstk_pylib import ' + x + '\n')
        f.close()

    for x in namespace:
        if should_be_added(x):
            use_global_namespace = True

            # check if in the custom-defined submodule dict
            for key, val in submodules.iteritems():
                exact_match = x in val[0]
                pattern_match = False
                for pattern in val[1]:
                    if pattern in x:
                        pattern_match = True

                if exact_match or pattern_match:
                    use_global_namespace = False
                    if not os.path.exists(out_dir + key):
                        os.makedirs(out_dir + key)
                    f = open(out_dir + key + '/__init__.py', 'a')
                    f.write('from ..gpstk_pylib import ' + x + '\n')
                    f.close()

                    name = key + '/__init__.py'
                    if name not in files_to_move:
                        files_to_move.append(name)

            # if it isn't a type (i.e. class) or function add to constants submodule
            t = eval('gpstk_pylib.' + x)
            if (type(t) is not type) and (not hasattr(t, '__call__')):
                use_global_namespace = False
                add_to_submodule(x, 'constants')
            # if it subclasses gpstk.Exception add to exceptions submodule
            if inspect.isclass(t) and issubclass(t, gpstk_pylib.Exception) or 'Exception' in x:
                use_global_namespace = False
                add_to_submodule(x, 'exceptions')

            # otherwise add to global gpstk
            if use_global_namespace:
                out_file.write('from gpstk_pylib import ')
                out_file.write(x)
                out_file.write('\n')

    for key, val in submodules.iteritems():
        out_file.write('import ' + key + '\n')
    out_file.write('import constants\n')
    out_file.write('import exceptions\n')

    # Create gpstk folder, move things into it
    # we don't know extension of library file, so search the directory:
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if '_gpstk_pylib' in f:
            files_to_move.append(f)

    # build to local gpstk folder
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for f in files_to_move:
        if os.path.exists(f):
            os.rename(f, out_dir + f)
        # adds pyc file if it exists:
        if os.path.exists(f + 'c'):
            os.rename(f + 'c', out_dir + f + 'c')


if __name__ == '__main__':
    main()