# distutils: language=c++
cimport cython
cimport numpy as np
import numpy as np
from libcpp.stack cimport stack

@cython.boundscheck(False)
@cython.wraparound(False)
def match(long long[:] times, long[:] types):
    cdef stack[long long] q
    out = np.full((types.size,3), -1, dtype= np.int64)
    cdef long long t
    cdef int i
    cdef int stop = types.size
    cdef int step = 1
    cdef long long[:,:] out_view = out
    for i from 0 <= i < stop by step:
        if(types[i] == 0):
            if(q.empty()): continue
            t = q.top()
            q.pop()
            out_view[t][1] = times[i]
            out_view[t][2] = out_view[t][1] - out_view[t][0]
        else:
            out_view[i][0] = times[i]
            q.push(i)
    return out