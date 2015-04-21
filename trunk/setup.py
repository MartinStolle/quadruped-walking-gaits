from distutils.core import setup
import py2exe
import os

Data_Files = []
Data_Files.append ( ('vis', [r'D:\Python26\Lib\site-packages\vis\turbulence3.tga']))
Data_Files.append ( ('vis', [r'D:\Python26\Lib\site-packages\vis\earth.tga']))
Data_Files.append ( ('vis', [r'D:\Python26\Lib\site-packages\vis\wood.tga']))

setup(
    console = ['main.py', 'midpoint.py'],
    data_files = Data_Files,
    options = {
                'py2exe': {
                    'skip_archive':1
                    }
                }
)
