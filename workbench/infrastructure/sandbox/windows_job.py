"""An owned Windows job, assigned before the trusted SDK child receives work."""

import ctypes
from ctypes import wintypes

from workbench.errors import UnsupportedScope


class BasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", ctypes.c_uint32),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_uint32),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_uint32),
        ("SchedulingClass", ctypes.c_uint32),
    ]


class IOCounters(ctypes.Structure):
    _fields_ = [
        (key, ctypes.c_ulonglong)
        for key in (
            "ReadOperationCount",
            "WriteOperationCount",
            "OtherOperationCount",
            "ReadTransferCount",
            "WriteTransferCount",
            "OtherTransferCount",
        )
    ]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", BasicLimits),
        ("IoInfo", IOCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class WindowsJob:
    def __init__(self, process, *, api=None):
        self.api = api if api is not None else ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            "SetInformationJobObject": (
                [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32],
                ctypes.c_int32,
            ),
            "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], ctypes.c_int32),
            "TerminateJobObject": ([wintypes.HANDLE, ctypes.c_uint32], ctypes.c_int32),
            "CloseHandle": ([wintypes.HANDLE], ctypes.c_int32),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = args, result
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise UnsupportedScope("Windows file worker job creation failed")
        try:
            limits = ExtendedLimits()
            limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not self.api.SetInformationJobObject(
                self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
            ):
                raise UnsupportedScope("Windows file worker job configuration failed")
            if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
                raise UnsupportedScope("Windows file worker job assignment failed")
        except BaseException:
            self.close()
            raise

    def terminate(self):
        if not self.api.TerminateJobObject(self.handle, 1):
            raise UnsupportedScope("Windows file worker subtree termination failed")

    def close(self):
        if self.handle:
            handle, self.handle = self.handle, None
            if not self.api.CloseHandle(handle):
                raise UnsupportedScope("Windows file worker job handle closure failed")
