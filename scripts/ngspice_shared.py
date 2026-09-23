import ctypes as c
import os
import ctypes.util
from pathlib import Path
import numpy as np

class Complex(c.Structure):
    _fields_ = [('real', c.c_double), ('imag', c.c_double)]

class Vector(c.Structure):
    _fields_ = [('name', c.c_char_p), ('type', c.c_int), ('flags', c.c_short),
                ('real', c.POINTER(c.c_double)), ('complex', c.POINTER(Complex)),
                ('length', c.c_int)]

class Engine:
    def __init__(self, library=None):
        library = library or os.environ.get('NGSPICE_LIBRARY')
        if not library:
            windows_default = Path('C:/Program Files/KiCad/9.0/bin/ngspice.dll')
            library = str(windows_default) if windows_default.is_file() else ctypes.util.find_library('ngspice')
        if not library:
            raise RuntimeError('Set NGSPICE_LIBRARY to your ngspice shared library path.')
        self.messages = []
        self.dir = os.add_dll_directory(str(Path(library).parent)) if os.name == 'nt' else None
        self.dll = c.CDLL(library)
        send = c.CFUNCTYPE(c.c_int, c.c_char_p, c.c_int, c.c_void_p)
        exit_type = c.CFUNCTYPE(c.c_int, c.c_int, c.c_bool, c.c_bool, c.c_int, c.c_void_p)
        def output(text, _id, _user):
            self.messages.append(text.decode(errors='replace'))
            return 0
        def exited(status, immediate, quitexit, _id, _user):
            self.messages.append(f'CONTROLLED_EXIT status={status} quit={quitexit}')
            return 0
        self.output = send(output)
        self.exited = exit_type(exited)
        self.dll.ngSpice_Init.argtypes = [send, c.c_void_p, exit_type, c.c_void_p, c.c_void_p, c.c_void_p, c.c_void_p]
        self.dll.ngSpice_Init(self.output, None, self.exited, None, None, None, None)
        self.dll.ngSpice_Command.argtypes = [c.c_char_p]
        self.dll.ngGet_Vec_Info.argtypes = [c.c_char_p]
        self.dll.ngGet_Vec_Info.restype = c.POINTER(Vector)
        self.command('set ngbehavior=ps')
        self.command('version')
        self.command('set noaskquit')

    def command(self, command):
        self.messages.append('COMMAND: ' + command)
        status = self.dll.ngSpice_Command(command.encode())
        if status:
            raise RuntimeError(f'Command failed ({status}): {command}')

    def load(self, path):
        self.command('destroy all')
        self.command('source ' + Path(path).resolve().as_posix())

    def vector(self, name):
        pointer = self.dll.ngGet_Vec_Info(name.encode())
        if not pointer:
            raise RuntimeError('Missing vector: ' + name)
        v = pointer.contents
        if v.real:
            return np.ctypeslib.as_array(v.real, shape=(v.length,)).copy()
        return np.array([complex(v.complex[i].real, v.complex[i].imag) for i in range(v.length)])
