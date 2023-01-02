import numpy as np
from scipy.interpolate import interp1d


def interpolateVectors(vectors, numInterpolations, interpolationType):
    """
    Interpolates between a given set of vectors with a given amount of interpolation steps
    Args:
        vectors: Array of vectors
        numInterpolations: Amount of interpolation steps between all vectors
        interpolationType: cubic, quadratic, linear or nearest

    Returns: Array of interpolated vectors between first and last vector of given set

    """
    # Amount of initial noise vectors
    numInitNoise = len(vectors)

    # Repeats the initial vector for every frame, if there is no interpolation possible
    # This happens if only one vector is provided
    if numInitNoise < 2:
        # Reshape initial vector
        vectors[0] = np.array(vectors[0])
        vectors[0] = vectors[0].reshape(512, 1)
        vectors[0] = np.transpose(vectors[0])

        # Create array to store all frame vectors into
        interpolations = np.array([None]*0).reshape(0, 512)

        # Repeat initial vector for every frame
        for i in range(numInterpolations):
            interpolations = np.append(interpolations, vectors[0], axis=0)

        return interpolations

    # Interpolations between given noise vectors
    interpolations = np.array([0.0] * 0).reshape(numInterpolations, 0)

    # Indices for all initial noise vectors
    noiseIterator = list(range(numInitNoise))

    # Interpolate each dimension separately
    for dim in range(len(vectors[0])):
        dimensionValues = [None] * len(vectors)

        # Retrieve current dimension value for all frames
        for v in range(len(vectors)):
            dimensionValues[v] = vectors[v][dim]

        # Create interpolation curve between all dimension values with given interpolation type
        if numInitNoise < 3 and interpolationType == "quadratic":
            dimension_curve = interp1d(noiseIterator, dimensionValues, kind='linear')
        elif numInitNoise < 4 and interpolationType == "cubic":
            if numInitNoise < 3:
                dimension_curve = interp1d(noiseIterator, dimensionValues, kind='linear')
            else:
                dimension_curve = interp1d(noiseIterator, dimensionValues, kind='quadratic')
        else:
            dimension_curve = interp1d(noiseIterator, dimensionValues, kind=interpolationType)

        # Interpolate between first and last initial vector with interpolation curve
        framesIterator = np.linspace(0, len(vectors) - 1, num=numInterpolations, endpoint=True)
        dimensionInerpolationPoints = dimension_curve(framesIterator)

        # Turn values into column vector
        dimensionInterpolation = dimensionInerpolationPoints.reshape(numInterpolations, 1)

        # Add interpolation for current dimension to interpolations matrix
        interpolations = np.append(interpolations, dimensionInterpolation, axis=1)

    return interpolations
