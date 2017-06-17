# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from contextlib import contextmanager
import os
from unittest import TestCase

from os.path import join
import pytest

from conda.base.context import context, reset_context, Context
from conda.common.io import env_var
from conda.core.linked_data import PrefixData
from conda.core.solve import DepsModifier, Solver
from conda.exceptions import UnsatisfiableError
from conda.history import History
from conda.models.channel import Channel
from conda.models.dag import PrefixDag
from conda.models.dist import Dist
from conda.models.prefix_record import PrefixRecord
from conda.resolve import MatchSpec
from ..helpers import patch, get_index_r_1, get_index_r_2, get_index_r_3
from conda.common.compat import iteritems

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

@contextmanager
def get_solver(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    prefix = '/a/test/c/prefix'
    PrefixData._cache_ = {}
    pd = PrefixData(prefix)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    spec_map = {spec.name: spec for spec in history_specs}
    index, r = get_index_r_1()
    with patch.object(History, 'get_requested_specs_map', return_value=spec_map):
        solver = Solver(prefix, (Channel('defaults'),), context.subdirs,
                        specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        solver._index = index
        solver._r = r
        solver._prepared = True
        yield solver


@contextmanager
def get_solver_2(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    prefix = '/a/test/c/prefix'
    PrefixData._cache_ = {}
    pd = PrefixData(prefix)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    spec_map = {spec.name: spec for spec in history_specs}
    index, r = get_index_r_2()
    with patch.object(History, 'get_requested_specs_map', return_value=spec_map):
        solver = Solver(prefix, (Channel('defaults'),), context.subdirs,
                        specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        solver._index = index
        solver._r = r
        solver._prepared = True
        yield solver


@contextmanager
def get_solver_3(specs_to_add=(), specs_to_remove=(), prefix_records=(), history_specs=()):
    prefix = '/a/test/c/prefix'
    PrefixData._cache_ = {}
    pd = PrefixData(prefix)
    pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec) for rec in prefix_records}
    spec_map = {spec.name: spec for spec in history_specs}
    index, r = get_index_r_3()
    with patch.object(History, 'get_requested_specs_map', return_value=spec_map):
        solver = Solver(prefix, (Channel('defaults'),), context.subdirs,
                        specs_to_add=specs_to_add, specs_to_remove=specs_to_remove)
        solver._index = index
        solver._r = r
        solver._prepared = True
        yield solver


def test_solve_1():
    specs = MatchSpec("numpy"),

    with get_solver(specs) as solver:
        final_state = solver.solve_final_state()
        print([Dist(rec).full_name for rec in final_state])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-3.3.2-0',
            'defaults::numpy-1.7.1-py33_0',
        )
        assert tuple(final_state) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("python=2"),
    with get_solver(specs_to_add=specs_to_add,
                    prefix_records=final_state, history_specs=specs) as solver:
        final_state = solver.solve_final_state()
        print([Dist(rec).full_name for rec in final_state])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::numpy-1.7.1-py27_0',
        )
        assert tuple(final_state) == tuple(solver._index[Dist(d)] for d in order)


def test_prune_1():
    specs = MatchSpec("numpy=1.6"), MatchSpec("python=2.7.3"), MatchSpec("accelerate"),

    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::libnvvm-1.0-p0',
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::mkl-rt-11.0-p0',
            'defaults::python-2.7.3-7',
            'defaults::bitarray-0.8.1-py27_0',
            'defaults::llvmpy-0.11.2-py27_0',
            'defaults::meta-0.4.2.dev-py27_0',
            'defaults::mkl-service-1.0.0-py27_p0',
            'defaults::numpy-1.6.2-py27_p4',
            'defaults::numba-0.8.1-np16py27_0',
            'defaults::numexpr-2.1-np16py27_p0',
            'defaults::scipy-0.12.0-np16py27_p0',
            'defaults::numbapro-0.11.0-np16py27_p0',
            'defaults::scikit-learn-0.13.1-np16py27_p0',
            'defaults::mkl-11.0-np16py27_p0',
            'defaults::accelerate-1.1.0-np16py27_p0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_remove = MatchSpec("numbapro"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(prune=False)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::libnvvm-1.0-p0',
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::mkl-rt-11.0-p0',
            'defaults::python-2.7.3-7',
            'defaults::bitarray-0.8.1-py27_0',
            'defaults::llvmpy-0.11.2-py27_0',
            'defaults::meta-0.4.2.dev-py27_0',
            'defaults::mkl-service-1.0.0-py27_p0',
            'defaults::numpy-1.6.2-py27_p4',
            'defaults::numba-0.8.1-np16py27_0',
            'defaults::numexpr-2.1-np16py27_p0',
            'defaults::scipy-0.12.0-np16py27_p0',
            'defaults::scikit-learn-0.13.1-np16py27_p0',
            'defaults::mkl-11.0-np16py27_p0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(prune=True)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.3-7',
            'defaults::numpy-1.6.2-py27_4',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)


def test_prune_2():
    specs_to_remove = MatchSpec("python=2"),
    history_specs = MatchSpec("sqlite=3"),
    with get_solver(specs_to_remove=specs_to_remove, history_specs=history_specs) as solver:
        final_state = solver.solve_final_state(prune=True)
        print(final_state)
        assert len(final_state) == 1


def test_force_remove_1():
    specs = MatchSpec("numpy[build=*py27*]"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::numpy-1.7.1-py27_0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_remove = MatchSpec("python"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_remove = MatchSpec("python"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(force_remove=True)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::numpy-1.7.1-py27_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    with get_solver(prefix_records=final_state_2) as solver:
        final_state_3 = solver.solve_final_state(prune=True)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_3])
        order = ()
        assert tuple(final_state_3) == tuple(solver._index[Dist(d)] for d in order)


def test_no_deps_1():
    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        # print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("numba"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::python-2.7.5-0',
            'defaults::llvmpy-0.11.2-py27_0',
            'defaults::meta-0.4.2.dev-py27_0',
            'defaults::numpy-1.7.1-py27_0',
            'defaults::numba-0.8.1-np17py27_0'
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("numba"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(deps_modifier='NO_DEPS')
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::numba-0.8.1-np17py27_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)


def test_only_deps_1():
    specs = MatchSpec("numba[build=*py27*]"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state(deps_modifier=DepsModifier.ONLY_DEPS)
        # PrefixDag(final_state_1, specs).open_url()
        # print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::python-2.7.5-0',
            'defaults::llvmpy-0.11.2-py27_0',
            'defaults::meta-0.4.2.dev-py27_0',
            'defaults::numpy-1.7.1-py27_0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)


def test_only_deps_2():
    specs = MatchSpec("numpy=1.5"), MatchSpec("python=2.7.3"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.3-7',
            'defaults::numpy-1.5.1-py27_4',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("numba=0.5"),
    with get_solver(specs_to_add) as solver:
        final_state_2 = solver.solve_final_state(deps_modifier=DepsModifier.ONLY_DEPS)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::python-2.7.5-0',
            'defaults::llvmpy-0.10.0-py27_0',
            'defaults::meta-0.4.2.dev-py27_0',
            'defaults::nose-1.3.0-py27_0',
            'defaults::numpy-1.7.1-py27_0',
            # 'defaults::numba-0.5.0-np17py27_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("numba=0.5"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(deps_modifier=DepsModifier.ONLY_DEPS)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::python-2.7.3-7',
            'defaults::llvmpy-0.10.0-py27_0',
            'defaults::meta-0.4.2.dev-py27_0',
            'defaults::nose-1.3.0-py27_0',
            'defaults::numpy-1.7.1-py27_0',
            # 'defaults::numba-0.5.0-np17py27_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)


def test_update_all_1():
    specs = MatchSpec("numpy=1.5"), MatchSpec("python=2.6"), MatchSpec("system[build_number=0]")
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-0',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.6.8-6',
            'defaults::numpy-1.5.1-py26_4',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("numba=0.6"), MatchSpec("numpy")
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-0',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::python-2.6.8-6',
            'defaults::llvmpy-0.10.2-py26_0',
            'defaults::nose-1.3.0-py26_0',
            'defaults::numpy-1.7.1-py26_0',
            'defaults::numba-0.6.0-np17py26_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("numba=0.6"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state(deps_modifier=DepsModifier.UPDATE_ALL)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::python-2.7.5-0',
            'defaults::llvmpy-0.10.2-py27_0',
            'defaults::meta-0.4.2.dev-py27_0',
            'defaults::nose-1.3.0-py27_0',
            'defaults::numpy-1.7.1-py27_0',
            'defaults::numba-0.6.0-np17py27_0'
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)


def test_broken_install():
    specs = MatchSpec("pandas"), MatchSpec("python=2.7"), MatchSpec("numpy 1.6.*")
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order_original = [
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::numpy-1.6.2-py27_4',
            'defaults::pytz-2013b-py27_0',
            'defaults::six-1.3.0-py27_0',
            'defaults::dateutil-2.1-py27_1',
            'defaults::scipy-0.12.0-np16py27_0',
            'defaults::pandas-0.11.0-np16py27_1',
        ]
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order_original)
        assert solver._r.environment_is_consistent(order_original)

    # Add an incompatible numpy; installation should be untouched
    order_1 = list(order_original)
    order_1[7] = "defaults::numpy-1.7.1-py33_p0"
    order_1_records = [solver._index[Dist(d)] for d in order_1]
    assert not solver._r.environment_is_consistent(order_1)

    specs_to_add = MatchSpec("flask"),
    with get_solver(specs_to_add, prefix_records=order_1_records, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = [
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::jinja2-2.6-py27_0',
            "defaults::numpy-1.7.1-py33_p0",
            'defaults::pytz-2013b-py27_0',
            'defaults::six-1.3.0-py27_0',
            'defaults::werkzeug-0.8.3-py27_0',
            'defaults::dateutil-2.1-py27_1',
            'defaults::flask-0.9-py27_0',
            'defaults::scipy-0.12.0-np16py27_0',
            'defaults::pandas-0.11.0-np16py27_1'
        ]
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
        assert not solver._r.environment_is_consistent(order)

    # adding numpy spec again snaps the packages back to a consistent state
    specs_to_add = MatchSpec("flask"), MatchSpec("numpy 1.6.*"),
    with get_solver(specs_to_add, prefix_records=order_1_records, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = [
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::jinja2-2.6-py27_0',
            'defaults::numpy-1.6.2-py27_4',
            'defaults::pytz-2013b-py27_0',
            'defaults::six-1.3.0-py27_0',
            'defaults::werkzeug-0.8.3-py27_0',
            'defaults::dateutil-2.1-py27_1',
            'defaults::flask-0.9-py27_0',
            'defaults::scipy-0.12.0-np16py27_0',
            'defaults::pandas-0.11.0-np16py27_1',
        ]
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
        assert solver._r.environment_is_consistent(order)

    # Add an incompatible pandas; installation should be untouched, then fixed
    order_2 = list(order_original)
    order_2[12] = 'defaults::pandas-0.11.0-np17py27_1'
    order_2_records = [solver._index[Dist(d)] for d in order_2]
    assert not solver._r.environment_is_consistent(order_2)

    specs_to_add = MatchSpec("flask"),
    with get_solver(specs_to_add, prefix_records=order_2_records, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = [
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::jinja2-2.6-py27_0',
            'defaults::numpy-1.6.2-py27_4',
            'defaults::pytz-2013b-py27_0',
            'defaults::six-1.3.0-py27_0',
            'defaults::werkzeug-0.8.3-py27_0',
            'defaults::dateutil-2.1-py27_1',
            'defaults::flask-0.9-py27_0',
            'defaults::scipy-0.12.0-np16py27_0',
            'defaults::pandas-0.11.0-np17py27_1',
        ]
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
        assert not solver._r.environment_is_consistent(order)

    # adding pandas spec again snaps the packages back to a consistent state
    specs_to_add = MatchSpec("flask"), MatchSpec("pandas"),
    with get_solver(specs_to_add, prefix_records=order_2_records, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = [
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::jinja2-2.6-py27_0',
            'defaults::numpy-1.6.2-py27_4',
            'defaults::pytz-2013b-py27_0',
            'defaults::six-1.3.0-py27_0',
            'defaults::werkzeug-0.8.3-py27_0',
            'defaults::dateutil-2.1-py27_1',
            'defaults::flask-0.9-py27_0',
            'defaults::scipy-0.12.0-np16py27_0',
            'defaults::pandas-0.11.0-np16py27_1',
        ]
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
        assert solver._r.environment_is_consistent(order)

    # Actually I think this part might be wrong behavior:
    #    # Removing pandas should fix numpy, since pandas depends on it
    # I think removing pandas should probably leave the broken numpy. That seems more consistent.

    # order_3 = list(order_original)
    # order_1[7] = 'defaults::numpy-1.7.1-py33_p0'
    # order_3[12] = 'defaults::pandas-0.11.0-np17py27_1'
    # order_3_records = [index[Dist(d)] for d in order_3]
    # assert not r.environment_is_consistent(order_3)
    #
    # PrefixData._cache_ = {}
    # pd = PrefixData(prefix)
    # pd._PrefixData__prefix_records = {rec.name: PrefixRecord.from_objects(rec)
    #                                   for rec in order_3_records}
    # spec_map = {
    #     "pandas": MatchSpec("pandas"),
    #     "python": MatchSpec("python=2.7"),
    #     "numpy": MatchSpec("numpy 1.6.*"),
    # }
    # with patch.object(History, 'get_requested_specs_map', return_value=spec_map):
    #     solver = Solver(prefix, (Channel('defaults'),), context.subdirs,
    #                     specs_to_remove=(MatchSpec("pandas"),))
    #     solver.index = index
    #     solver.r = r
    #     solver._prepared = True
    #
    #     final_state_2 = solver.solve_final_state()
    #
    #     # PrefixDag(final_state_2, specs).open_url()
    #     print([Dist(rec).full_name for rec in final_state_2])
    #
    #     order = [
    #         'defaults::openssl-1.0.1c-0',
    #         'defaults::readline-6.2-0',
    #         'defaults::sqlite-3.7.13-0',
    #         'defaults::system-5.8-1',
    #         'defaults::tk-8.5.13-0',
    #         'defaults::zlib-1.2.7-0',
    #         'defaults::python-2.7.5-0',
    #         'defaults::jinja2-2.6-py27_0',
    #         'defaults::numpy-1.6.2-py27_4',
    #         'defaults::pytz-2013b-py27_0',
    #         'defaults::six-1.3.0-py27_0',
    #         'defaults::werkzeug-0.8.3-py27_0',
    #         'defaults::dateutil-2.1-py27_1',
    #         'defaults::flask-0.9-py27_0',
    #         'defaults::scipy-0.12.0-np16py27_0',
    #     ]
    #     assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
    #     assert r.environment_is_consistent(order)


def test_install_uninstall_features():
    specs = MatchSpec("pandas"), MatchSpec("python=2.7"), MatchSpec("numpy 1.6.*")
    with env_var("CONDA_TRACK_FEATURES", 'mkl', reset_context):
        with get_solver(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            print([Dist(rec).full_name for rec in final_state_1])
            order = (
                'defaults::openssl-1.0.1c-0',
                'defaults::readline-6.2-0',
                'defaults::sqlite-3.7.13-0',
                'defaults::system-5.8-1',
                'defaults::tk-8.5.13-0',
                'defaults::zlib-1.2.7-0',
                'defaults::mkl-rt-11.0-p0',
                'defaults::python-2.7.5-0',
                'defaults::numpy-1.6.2-py27_p4',
                'defaults::pytz-2013b-py27_0',
                'defaults::six-1.3.0-py27_0',
                'defaults::dateutil-2.1-py27_1',
                'defaults::scipy-0.12.0-np16py27_p0',
                'defaults::pandas-0.11.0-np16py27_1',
            )
            assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    # no more track_features in configuration
    # just remove the pandas package, but the mkl feature "stays in the environment"
    # that is, the current mkl packages aren't switched out
    specs_to_remove = MatchSpec("pandas"),
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_1,
                    history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::mkl-rt-11.0-p0',
            'defaults::python-2.7.5-0',
            'defaults::numpy-1.6.2-py27_p4',
            'defaults::pytz-2013b-py27_0',
            'defaults::six-1.3.0-py27_0',
            'defaults::dateutil-2.1-py27_1',
            'defaults::scipy-0.12.0-np16py27_p0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    # now remove the mkl feature
    specs_to_remove = MatchSpec(track_features="mkl"),
    history_specs = MatchSpec("python=2.7"), MatchSpec("numpy 1.6.*")
    with get_solver(specs_to_remove=specs_to_remove, prefix_records=final_state_2,
                    history_specs=history_specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::numpy-1.6.2-py27_4',
            'defaults::pytz-2013b-py27_0',
            'defaults::six-1.3.0-py27_0',
            'defaults::dateutil-2.1-py27_1',
            # 'defaults::scipy-0.12.0-np16py27_p0', scipy is out here because it wasn't a requested spec
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)


def test_update_deps_1():
    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        # print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("numpy=1.7.0"), MatchSpec("python=2.7.3")
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.3-7',
            'defaults::nose-1.3.0-py27_0',
            'defaults::numpy-1.7.0-py27_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("iopro"),
    with get_solver(specs_to_add, prefix_records=final_state_2, history_specs=specs) as solver:
        final_state_3 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_3])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::unixodbc-2.3.1-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.3-7',
            'defaults::nose-1.3.0-py27_0',
            'defaults::numpy-1.7.0-py27_0',
            'defaults::iopro-1.5.0-np17py27_p0',
        )
        assert tuple(final_state_3) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("iopro"),
    with get_solver(specs_to_add, prefix_records=final_state_2, history_specs=specs) as solver:
        final_state_3 = solver.solve_final_state(deps_modifier=DepsModifier.UPDATE_DEPS)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_3])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::unixodbc-2.3.1-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',   # with update_deps, numpy should switch from 1.7.0 to 1.7.1
            'defaults::nose-1.3.0-py27_0',
            'defaults::numpy-1.7.1-py27_0',  # with update_deps, numpy should switch from 1.7.0 to 1.7.1
            'defaults::iopro-1.5.0-np17py27_p0',
        )
        assert tuple(final_state_3) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("iopro"),
    with get_solver(specs_to_add, prefix_records=final_state_2, history_specs=specs) as solver:
        final_state_3 = solver.solve_final_state(deps_modifier=DepsModifier.UPDATE_DEPS_ONLY_DEPS)
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_3])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::unixodbc-2.3.1-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',   # with update_deps, numpy should switch from 1.7.0 to 1.7.1
            'defaults::nose-1.3.0-py27_0',
            'defaults::numpy-1.7.1-py27_0',  # with update_deps, numpy should switch from 1.7.0 to 1.7.1
            # 'defaults::iopro-1.5.0-np17py27_p0',
        )
        assert tuple(final_state_3) == tuple(solver._index[Dist(d)] for d in order)


def test_pinned_1():
    specs = MatchSpec("numpy"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-3.3.2-0',
            'defaults::numpy-1.7.1-py33_0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    with env_var("CONDA_PINNED_PACKAGES", "python=2.6&iopro<=1.4.2", reset_context):
        specs = MatchSpec("system=5.8=0"),
        with get_solver(specs) as solver:
            final_state_1 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            print([Dist(rec).full_name for rec in final_state_1])
            order = (
                'defaults::system-5.8-0',
            )
            assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

        specs_to_add = MatchSpec("python"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_1,
                        history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state(ignore_pinned=True)
            # PrefixDag(final_state_1, specs).open_url()
            print([Dist(rec).full_name for rec in final_state_2])
            order = (
                'defaults::openssl-1.0.1c-0',
                'defaults::readline-6.2-0',
                'defaults::sqlite-3.7.13-0',
                'defaults::system-5.8-0',
                'defaults::tk-8.5.13-0',
                'defaults::zlib-1.2.7-0',
                'defaults::python-3.3.2-0',
            )
            assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

        specs_to_add = MatchSpec("python"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_1,
                        history_specs=specs) as solver:
            final_state_2 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            print([Dist(rec).full_name for rec in final_state_2])
            order = (
                'defaults::openssl-1.0.1c-0',
                'defaults::readline-6.2-0',
                'defaults::sqlite-3.7.13-0',
                'defaults::system-5.8-0',
                'defaults::tk-8.5.13-0',
                'defaults::zlib-1.2.7-0',
                'defaults::python-2.6.8-6',
            )
            assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

        specs_to_add = MatchSpec("numba"),
        history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_2,
                        history_specs=history_specs) as solver:
            final_state_3 = solver.solve_final_state()
            # PrefixDag(final_state_1, specs).open_url()
            print([Dist(rec).full_name for rec in final_state_3])
            order = (
                'defaults::openssl-1.0.1c-0',
                'defaults::readline-6.2-0',
                'defaults::sqlite-3.7.13-0',
                'defaults::system-5.8-0',
                'defaults::tk-8.5.13-0',
                'defaults::zlib-1.2.7-0',
                'defaults::llvm-3.2-0',
                'defaults::python-2.6.8-6',
                'defaults::argparse-1.2.1-py26_0',
                'defaults::llvmpy-0.11.2-py26_0',
                'defaults::numpy-1.7.1-py26_0',
                'defaults::numba-0.8.1-np17py26_0',
            )
            assert tuple(final_state_3) == tuple(solver._index[Dist(d)] for d in order)

        specs_to_add = MatchSpec("python"),
        history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"), MatchSpec("numba"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_3,
                        history_specs=history_specs) as solver:
            final_state_4 = solver.solve_final_state(deps_modifier=DepsModifier.UPDATE_DEPS)
            # PrefixDag(final_state_1, specs).open_url()
            print([Dist(rec).full_name for rec in final_state_4])
            order = (
                'defaults::openssl-1.0.1c-0',
                'defaults::readline-6.2-0',
                'defaults::sqlite-3.7.13-0',
                'defaults::system-5.8-1',
                'defaults::tk-8.5.13-0',
                'defaults::zlib-1.2.7-0',
                'defaults::llvm-3.2-0',
                'defaults::python-2.6.8-6',
                'defaults::argparse-1.2.1-py26_0',
                'defaults::llvmpy-0.11.2-py26_0',
                'defaults::numpy-1.7.1-py26_0',
                'defaults::numba-0.8.1-np17py26_0',
            )
            assert tuple(final_state_4) == tuple(solver._index[Dist(d)] for d in order)

        specs_to_add = MatchSpec("python"),
        history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"), MatchSpec("numba"),
        with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_4,
                        history_specs=history_specs) as solver:
            final_state_5 = solver.solve_final_state(deps_modifier=DepsModifier.UPDATE_ALL)
            # PrefixDag(final_state_1, specs).open_url()
            print([Dist(rec).full_name for rec in final_state_5])
            order = (
                'defaults::openssl-1.0.1c-0',
                'defaults::readline-6.2-0',
                'defaults::sqlite-3.7.13-0',
                'defaults::system-5.8-1',
                'defaults::tk-8.5.13-0',
                'defaults::zlib-1.2.7-0',
                'defaults::llvm-3.2-0',
                'defaults::python-2.6.8-6',
                'defaults::argparse-1.2.1-py26_0',
                'defaults::llvmpy-0.11.2-py26_0',
                'defaults::numpy-1.7.1-py26_0',
                'defaults::numba-0.8.1-np17py26_0',
            )
            assert tuple(final_state_5) == tuple(solver._index[Dist(d)] for d in order)

    # now update without pinning
    specs_to_add = MatchSpec("python"),
    history_specs = MatchSpec("python"), MatchSpec("system=5.8=0"), MatchSpec("numba"),
    with get_solver(specs_to_add=specs_to_add, prefix_records=final_state_4,
                    history_specs=history_specs) as solver:
        final_state_5 = solver.solve_final_state(deps_modifier=DepsModifier.UPDATE_ALL)
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_5])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::llvm-3.2-0',
            'defaults::python-3.3.2-0',
            'defaults::llvmpy-0.11.2-py33_0',
            'defaults::numpy-1.7.1-py33_0',
            'defaults::numba-0.8.1-np17py33_0',
        )
        assert tuple(final_state_5) == tuple(solver._index[Dist(d)] for d in order)


def test_no_update_deps_1():  # i.e. FREEZE_DEPS
    # NOTE: So far, NOT actually testing the FREEZE_DEPS flag.  I'm unable to contrive a
    # situation where it's actually needed.

    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("zope.interface"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
            'defaults::nose-1.3.0-py27_0',
            'defaults::zope.interface-4.0.5-py27_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = MatchSpec("zope.interface>4.1"),
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-3.3.2-0',
            'defaults::nose-1.3.0-py33_0',
            'defaults::zope.interface-4.1.1.1-py33_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)


def test_force_reinstall_1():
    specs = MatchSpec("python=2"),
    with get_solver(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.1c-0',
            'defaults::readline-6.2-0',
            'defaults::sqlite-3.7.13-0',
            'defaults::system-5.8-1',
            'defaults::tk-8.5.13-0',
            'defaults::zlib-1.2.7-0',
            'defaults::python-2.7.5-0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    specs_to_add = specs
    with get_solver(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        unlink_dists, link_dists = solver.solve_for_diff()
        assert not unlink_dists
        assert not link_dists

        unlink_dists, link_dists = solver.solve_for_diff(force_reinstall=True)
        assert len(unlink_dists) == len(link_dists) == 1
        assert unlink_dists[0] == link_dists[0]

        unlink_dists, link_dists = solver.solve_for_diff()
        assert not unlink_dists
        assert not link_dists


@pytest.mark.integration  # this test is slower, so we'll lump it into integration
def test_freeze_deps_1():
    specs = MatchSpec("six=1.7"),
    with get_solver_2(specs) as solver:
        final_state_1 = solver.solve_final_state()
        # PrefixDag(final_state_1, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_1])
        order = (
            'defaults::openssl-1.0.2l-0',
            'defaults::readline-6.2-2',
            'defaults::sqlite-3.13.0-0',
            'defaults::tk-8.5.18-0',
            'defaults::xz-5.2.2-1',
            'defaults::zlib-1.2.8-3',
            'defaults::python-3.4.5-0',
            'defaults::six-1.7.3-py34_0',
        )
        assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)

    # to keep six=1.7 as a requested spec, we have to downgrade python to 2.7
    specs_to_add = MatchSpec("bokeh"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::mkl-2017.0.1-0',
            'defaults::openssl-1.0.2l-0',
            'defaults::readline-6.2-2',
            'defaults::sqlite-3.13.0-0',
            'defaults::tk-8.5.18-0',
            'defaults::xz-5.2.2-1',
            'defaults::yaml-0.1.6-0',
            'defaults::zlib-1.2.8-3',
            'defaults::python-2.7.13-0',
            'defaults::backports-1.0-py27_0',
            'defaults::backports_abc-0.5-py27_0',
            'defaults::futures-3.1.1-py27_0',
            'defaults::markupsafe-0.23-py27_2',
            'defaults::numpy-1.13.0-py27_0',
            'defaults::pyyaml-3.12-py27_0',
            'defaults::requests-2.14.2-py27_0',
            'defaults::setuptools-27.2.0-py27_0',
            'defaults::six-1.7.3-py27_0',
            'defaults::bkcharts-0.2-py27_0',
            'defaults::jinja2-2.9.6-py27_0',
            'defaults::python-dateutil-2.6.0-py27_0',
            'defaults::singledispatch-3.4.0.3-py27_0',
            'defaults::ssl_match_hostname-3.4.0.2-py27_1',
            'defaults::tornado-4.5.1-py27_0',
            'defaults::bokeh-0.12.6-py27_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    # now we can't install the latest bokeh 0.12.5, but instead we get bokeh 0.12.4
    specs_to_add = MatchSpec("bokeh"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1,
                      history_specs=(MatchSpec("six=1.7"), MatchSpec("python=3.4"))) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::mkl-2017.0.1-0',
            'defaults::openssl-1.0.2l-0',
            'defaults::readline-6.2-2',
            'defaults::sqlite-3.13.0-0',
            'defaults::tk-8.5.18-0',
            'defaults::xz-5.2.2-1',
            'defaults::yaml-0.1.6-0',
            'defaults::zlib-1.2.8-3',
            'defaults::python-3.4.5-0',
            'defaults::backports_abc-0.5-py34_0',
            'defaults::markupsafe-0.23-py34_2',
            'defaults::numpy-1.13.0-py34_0',
            'defaults::pyyaml-3.12-py34_0',
            'defaults::requests-2.14.2-py34_0',
            'defaults::setuptools-27.2.0-py34_0',
            'defaults::six-1.7.3-py34_0',
            'defaults::jinja2-2.9.6-py34_0',
            'defaults::python-dateutil-2.6.0-py34_0',
            'defaults::tornado-4.4.2-py34_0',
            'defaults::bokeh-0.12.4-py34_0',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    # here, the python=3.4 spec can't be satisfied, so it's dropped, and we go back to py27
    specs_to_add = MatchSpec("bokeh=0.12.5"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1,
                      history_specs=(MatchSpec("six=1.7"), MatchSpec("python=3.4"))) as solver:
        final_state_2 = solver.solve_final_state()
        # PrefixDag(final_state_2, specs).open_url()
        print([Dist(rec).full_name for rec in final_state_2])
        order = (
            'defaults::mkl-2017.0.1-0',
            'defaults::openssl-1.0.2l-0',
            'defaults::readline-6.2-2',
            'defaults::sqlite-3.13.0-0',
            'defaults::tk-8.5.18-0',
            'defaults::xz-5.2.2-1',
            'defaults::yaml-0.1.6-0',
            'defaults::zlib-1.2.8-3',
            'defaults::python-2.7.13-0',
            'defaults::backports-1.0-py27_0',
            'defaults::backports_abc-0.5-py27_0',
            'defaults::futures-3.1.1-py27_0',
            'defaults::markupsafe-0.23-py27_2',
            'defaults::numpy-1.13.0-py27_0',
            'defaults::pyyaml-3.12-py27_0',
            'defaults::requests-2.14.2-py27_0',
            'defaults::setuptools-27.2.0-py27_0',
            'defaults::six-1.7.3-py27_0',
            'defaults::jinja2-2.9.6-py27_0',
            'defaults::python-dateutil-2.6.0-py27_0',
            'defaults::singledispatch-3.4.0.3-py27_0',
            'defaults::ssl_match_hostname-3.4.0.2-py27_1',
            'defaults::tornado-4.5.1-py27_0',
            'defaults::bokeh-0.12.5-py27_1',
        )
        assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)

    # here, the python=3.4 spec can't be satisfied, so it's dropped, and we go back to py27
    specs_to_add = MatchSpec("bokeh=0.12.5"),
    with get_solver_2(specs_to_add, prefix_records=final_state_1,
                      history_specs=(MatchSpec("six=1.7"), MatchSpec("python=3.4"))) as solver:
        with pytest.raises(UnsatisfiableError):
            solver.solve_final_state(deps_modifier=DepsModifier.FREEZE_INSTALLED)


class PrivateEnvTests(TestCase):

    def setUp(self):
        self.prefix = '/a/test/c/prefix'

        self.preferred_env = "_spiffy-test-app_"
        self.preferred_env_prefix = join(self.prefix, 'envs', self.preferred_env)

        # self.save_path_conflict = os.environ.get('CONDA_PATH_CONFLICT')
        self.saved_values = {}
        self.saved_values['CONDA_ROOT_PREFIX'] = os.environ.get('CONDA_ROOT_PREFIX')
        self.saved_values['CONDA_ENABLE_PRIVATE_ENVS'] = os.environ.get('CONDA_ENABLE_PRIVATE_ENVS')

        # os.environ['CONDA_PATH_CONFLICT'] = 'prevent'
        os.environ['CONDA_ROOT_PREFIX'] = self.prefix
        os.environ['CONDA_ENABLE_PRIVATE_ENVS'] = 'true'

        reset_context()

    def tearDown(self):
        for key, value in iteritems(self.saved_values):
            if value is not None:
                os.environ[key] = value
            else:
                del os.environ[key]

        reset_context()

    # @patch.object(Context, 'prefix_specified')
    # def test_simple_install_uninstall(self, prefix_specified):
    #     prefix_specified.__get__ = Mock(return_value=False)
    #
    #     specs = MatchSpec("spiffy-test-app"),
    #     with get_solver_3(specs) as solver:
    #         final_state_1 = solver.solve_final_state()
    #         # PrefixDag(final_state_1, specs).open_url()
    #         print([Dist(rec).full_name for rec in final_state_1])
    #         order = (
    #             'defaults::openssl-1.0.2l-0',
    #             'defaults::readline-6.2-2',
    #             'defaults::sqlite-3.13.0-0',
    #             'defaults::tk-8.5.18-0',
    #             'defaults::zlib-1.2.8-3',
    #             'defaults::python-2.7.13-0',
    #             'defaults::spiffy-test-app-2.0-py27hf99fac9_0',
    #         )
    #         assert tuple(final_state_1) == tuple(solver._index[Dist(d)] for d in order)
    #
    #     specs_to_add = MatchSpec("uses-spiffy-test-app"),
    #     with get_solver_3(specs_to_add, prefix_records=final_state_1, history_specs=specs) as solver:
    #         final_state_2 = solver.solve_final_state()
    #         # PrefixDag(final_state_2, specs).open_url()
    #         print([Dist(rec).full_name for rec in final_state_2])
    #         order = (
    #
    #         )
    #         assert tuple(final_state_2) == tuple(solver._index[Dist(d)] for d in order)
    #
    #     specs = specs + specs_to_add
    #     specs_to_remove = MatchSpec("uses-spiffy-test-app"),
    #     with get_solver_3(specs_to_remove=specs_to_remove, prefix_records=final_state_2,
    #                       history_specs=specs) as solver:
    #         final_state_3 = solver.solve_final_state()
    #         # PrefixDag(final_state_2, specs).open_url()
    #         print([Dist(rec).full_name for rec in final_state_3])
    #         order = (
    #
    #         )
    #         assert tuple(final_state_3) == tuple(solver._index[Dist(d)] for d in order)
