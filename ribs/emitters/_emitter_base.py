"""Provides EmitterBase."""
from abc import ABC, abstractmethod

import numpy as np


class EmitterBase(ABC):
    """Base class for emitters.

    Every emitter has an :meth:`ask` method that generates a batch of solutions,
    and a :meth:`tell` method that inserts solutions into the emitter's archive.
    Child classes are only required to override :meth:`ask`.

    Args:
        archive (ribs.archives.ArchiveBase): An archive to use when creating and
            inserting solutions. For instance, this can be
            :class:`ribs.archives.GridArchive`.
        solution_dim (int): The dimension of solutions produced by this emitter.
        bounds (None or array-like): Bounds of the solution space. Pass None to
            indicate there are no bounds. Alternatively, pass an array-like to
            specify the bounds for each dim. Each element in this array-like can
            be None to indicate no bound, or a tuple of
            ``(lower_bound, upper_bound)``, where ``lower_bound`` or
            ``upper_bound`` may be None to indicate no bound.

            Unbounded upper bounds are set to +inf, and unbounded lower bounds
            are set to -inf.
    """

    def __init__(self, archive, solution_dim, bounds):
        self._archive = archive
        self._solution_dim = solution_dim
        (self._lower_bounds,
         self._upper_bounds) = self._process_bounds(bounds, self._solution_dim,
                                                    archive.dtype)

    @staticmethod
    def _process_bounds(bounds, solution_dim, dtype):
        """Processes the input bounds.

        Returns:
            tuple: Two arrays containing all the lower bounds and all the upper
                bounds.
        Raises:
            ValueError: There is an error in the bounds configuration.
        """
        lower_bounds = np.full(solution_dim, -np.inf, dtype=dtype)
        upper_bounds = np.full(solution_dim, np.inf, dtype=dtype)

        if bounds is None:
            return lower_bounds, upper_bounds

        # Handle array-like bounds.
        if len(bounds) != solution_dim:
            raise ValueError("If it is an array-like, bounds must have the "
                             "same length as x0")
        for idx, bnd in enumerate(bounds):
            if bnd is None:
                continue  # Bounds already default to -inf and inf.
            if len(bnd) != 2:
                raise ValueError("All entries of bounds must be length 2")
            lower_bounds[idx] = -np.inf if bnd[0] is None else bnd[0]
            upper_bounds[idx] = np.inf if bnd[1] is None else bnd[1]
        return lower_bounds, upper_bounds

    @property
    def archive(self):
        """ribs.archives.ArchiveBase: The archive which stores solutions
        generated by this emitter."""
        return self._archive

    @property
    def solution_dim(self):
        """int: The dimension of solutions produced by this emitter."""
        return self._solution_dim

    @property
    def lower_bounds(self):
        """numpy.ndarray: ``(solution_dim,)`` array with lower bounds of
        solution space.

        For instance, ``[-1, -1, -1]`` indicates that every dimension of the
        solution space has a lower bound of -1.
        """
        return self._lower_bounds

    @property
    def upper_bounds(self):
        """numpy.ndarray: ``(solution_dim,)`` array with upper bounds of
        solution space.

        For instance, ``[1, 1, 1]`` indicates that every dimension of the
        solution space has an upper bound of 1.
        """
        return self._upper_bounds

    @abstractmethod
    def ask(self):
        """Generates an ``(n, solution_dim)`` array of solutions."""

    @abstractmethod
    def tell(self,
             solution_batch,
             objective_batch,
             measures_batch,
             status_batch,
             value_batch,
             metadata_batch=None):
        """Gives the emitter results from evaluating solutions.

        This base class implementation (in :class:`~ribs.emitters.EmitterBase`)
        needs to be overriden.

        Args:
            solution_batch (numpy.ndarray): Array of solutions generated by this
                emitter's :meth:`ask()` method.
            objective_batch (numpy.ndarray): 1D array containing the objective
                function value of each solution.
            measures_batch (numpy.ndarray): ``(n, <measure space dimension>)``
                array with the measure space coordinates of each solution.
            status_batch (numpy.ndarray): An array of integer statuses
                returned by a series of calls to archive's :meth:`add_single()`
                method or by a single call to archive's :meth:`add()`.
            value_batch  (numpy.ndarray): 1D array of floats returned by a
                series of calls to archive's :meth:`add_single()` method or by a
                single call to archive's :meth:`add()`. For what these floats
                represent, refer to :meth:`ribs.archives.add()`.
            metadata_batch (numpy.ndarray): 1D object array containing a
                metadata object for each solution.
        """
