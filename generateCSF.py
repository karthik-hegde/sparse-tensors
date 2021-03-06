# Author -  Kartik hegde
#           kartikhegde.net

"""
    This file has functions to generate CSF data for a given tensor input.

    See the following papers:
        Kjolstad, Fredrik, et al. "The tensor algebra compiler." Proceedings of the ACM on Programming Languages
        1.OOPSLA (2017): 77.

        Shaden Smith and George Karypis. 2015. Tensor-matrix products with a compressed sparse tensor. In Proceedings of
        the 5th
        Workshop on Irregular Applications: Architectures and Algorithms. ACM, 5
"""

import numpy as np
import sys
import os

def compressDim(data, dim, dataShape, sparseDims, compressedData):
    """
        This is a recursive function call to generate compressed data.
    """

    if(dim > 0):

        idx_base = 0
        nnz_count = 0

        if(sparseDims[dim]):
            # Go through every data
            for x in range(dataShape[dim]):
                if(np.any(data[x])):
                    compressedData[dim][1].append(idx_base)
                    nnz_count += 1

                    # spawn another call
                    compressedData = compressDim(data[x], dim-1, dataShape,  sparseDims, compressedData)

                idx_base += 1

            compressedData[dim][0].append(compressedData[dim][0][-1] + nnz_count)

        else:
            # Simply add every dimension
            for x in range(dataShape[dim]):
                # spawn another call
                compressedData = compressDim(data[x], dim-1, dataShape, sparseDims, compressedData)

        return compressedData

    else:

        idx_base = 0
        nnz_count = 0

        # Inner most dimension ( doesn't spawn  new calls)
        if(sparseDims[dim]):
            # Go through every data
            for x in range(dataShape[dim]):
                if(np.any(data[x])):
                    compressedData[dim][1].append(idx_base)
                    nnz_count += 1
                    compressedData[-1].append(data[x])

                idx_base += 1

            compressedData[dim][0].append(compressedData[dim][0][-1] + nnz_count)

        else:
            # Append the entire data
            for x in range(dataShape[dim]):
                compressedData[-1].append(data[x])

        return compressedData

def generateCSF(data, sparseDims, datatype=np.float32):

    """
        This function generates CSF data for a given uncompressed input.

        Input:
            data - Standard Numpy array
            sparseDims - A list of length number of dimensions with a bool to represent sparse dimensions.

        Output:
            Dictionary that contains two keys:
                data: A numpy array of data
                metadata: A list of numpy arrays, where each array has two sub-arrays for pos and idx.
    """

    # Create useful parameters.
    numDims = len(sparseDims)
    dataShape = data.shape[::-1]
    sparseDims = sparseDims[::-1]

    # Placeholder for output
    compressedData = []

    for dim in range(numDims):
        if(sparseDims[dim]):
            compressedData.append([[0],[]])
        else:
            compressedData.append([[dataShape[dim]],[]])

    # Placeholder for the data
    compressedData.append([])

    # Now call the recursive function
    compressedData = compressDim(data, numDims-1, dataShape, sparseDims, compressedData)

    # Convert  list  to Numpy arrays
    finalCompressedData = {'data':None, 'metadata':[]}

    for idx,data in enumerate(reversed(compressedData)):
        if(idx==0):
            finalCompressedData['data'] = np.asarray(data, dtype=datatype)
        else:
            finalCompressedData['metadata'].append([np.asarray(data[0], dtype=np.int32),
                                                    np.asarray(data[1], dtype=np.int32)])

    return finalCompressedData


if __name__ == '__main__':

    # Reproduce TACO paper example

    data = np.array([[6,0,9,8],[0,0,0,0],[5,0,0,7]], dtype=np.float32)

    # Sparse Sparse case
    print("\n\n \t Sparse, Sparse")
    print(generateCSF(data, [True, True]))

    # Dense Dense case
    print("\n\n \t Dense, Dense")
    print(generateCSF(data, [False, False]))

    # Sparse Dense case
    print("\n\n \t Sparse, Dense")
    print(generateCSF(data, [True, False]))

    # Dense Sparse case
    print("\n\n \t Dense, Sparse")
    print(generateCSF(data, [False, True]))

