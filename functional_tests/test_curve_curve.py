# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
import numpy as np
import pytest
import six

import bezier
from bezier import _intersection_helpers
from bezier import _plot_helpers

import runtime_utils


CONFIG = runtime_utils.Config()
# g1 = sympy.Matrix([[s, 2 * s * (1 - s)]])
CURVE1 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.0],
    [0.5, 1.0],
    [1.0, 0.0],
]), _copy=False)
# g2 = sympy.Matrix([[(9 - 8 * s) / 8, (2 * s - 1)**2 / 2]])
CURVE2 = bezier.Curve.from_nodes(np.asfortranarray([
    [1.125, 0.5],
    [0.625, -0.5],
    [0.125, 0.5],
]), _copy=False)
# g3 = 3 * g1
# g3 = sympy.Matrix([[3 * s, 6 * s * (1 - s)]])
CURVE3 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.0],
    [1.5, 3.0],
    [3.0, 0.0],
]), _copy=False)
# g4 = sympy.Matrix([[
#     -3 * (4 * s**2 + s - 4) / 4,
#     (92 * s**2 - 77 * s + 24) / 16,
# ]])
CURVE4 = bezier.Curve.from_nodes(np.asfortranarray([
    [3.0, 1.5],
    [2.625, -0.90625],
    [-0.75, 2.4375],
]), _copy=False)
# g5 = sympy.Matrix([[s, (8 * s**2 - 8 * s + 3) / 4]])
CURVE5 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.75],
    [0.5, -0.25],
    [1.0, 0.75],
]), _copy=False)
# g6 = sympy.Matrix([[s, s**2 + (1 - s)**2]])
CURVE6 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 1.0],
    [0.5, 0.0],
    [1.0, 1.0],
]), _copy=False)
# g7 = sympy.Matrix([[s, (4 * s**2 - 4 * s + 17) / 64]])
CURVE7 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.265625],
    [0.5, 0.234375],
    [1.0, 0.265625],
]), _copy=False)
# g8 = sympy.Matrix([[8 * s, 3]]) / 8
CURVE8 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.375],
    [1.0, 0.375],
]), _copy=False)
# g9 = sympy.Matrix([[2, 3 * s]]) / 4
CURVE9 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.5, 0.0],
    [0.5, 0.75],
]), _copy=False)
# g10 = 9 * g1
# g10 = sympy.Matrix([[9 * s, 18 * s * (1 - s)]])
CURVE10 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.0],
    [4.5, 9.0],
    [9.0, 0.0],
]), _copy=False)
# g11 = sympy.Matrix([[6 * s, 8 * (1 - s)]])
CURVE11 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 8.0],
    [6.0, 0.0],
]), _copy=False)
# NOTE: This curve has a self-crossing.
# g12 = sympy.Matrix([[
#     -3 * s * (3 * s - 2)**2 / 4,
#     -(27 * s**3 - 72 * s**2 + 48 * s - 16) / 8,
# ]])
CURVE12 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 2.0],
    [-1.0, 0.0],
    [1.0, 1.0],
    [-0.75, 1.625],
]), _copy=False)
# g13 = sympy.Matrix([[s, 4 * s * (1 - s) * (7 * s**2 - 7 * s + 2)]])
CURVE13 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.0],
    [0.25, 2.0],
    [0.5, -2.0],
    [0.75, 2.0],
    [1.0, 0.0],
]), _copy=False)
# g14 = sympy.Matrix([[3 * s / 4, 3 * s * (4 - 3 * s) / 8]])
CURVE14 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.0],
    [0.375, 0.75],
    [0.75, 0.375],
]), _copy=False)
# g15 = sympy.Matrix([[(3 * s + 1) / 4, (9 * s**2 - 6 * s + 5) / 8]])
CURVE15 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.25, 0.625],
    [0.625, 0.25],
    [1.0, 1.0],
]), _copy=False)
# g16 = sympy.Matrix([[(3 * s + 1) / 4, 3 * (6 * s**2 - 4 * s + 3) / 16]])
CURVE16 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.25, 0.5625],
    [0.625, 0.1875],
    [1.0, 0.9375],
]), _copy=False)
# g17 = sympy.Matrix([[11 - 8 * s, -4 * (2 * s**2 - s - 2)]])
CURVE17 = bezier.Curve.from_nodes(np.asfortranarray([
    [11.0, 8.0],
    [7.0, 10.0],
    [3.0, 4.0],
]), _copy=False)
# g18 = sympy.Matrix([[s + 1, -2 * s * (1 - s)]])
CURVE18 = bezier.Curve.from_nodes(np.asfortranarray([
    [1.0, 0.0],
    [1.5, -1.0],
    [2.0, 0.0],
]), _copy=False)
# g19 = sympy.Matrix([[s + 1, 2 * s * (1 - s)]])
CURVE19 = bezier.Curve.from_nodes(np.asfortranarray([
    [2.0, 0.0],
    [1.5, 1.0],
    [1.0, 0.0],
]), _copy=False)
# g20 = sympy.Matrix([[(2 * s - 1)**2, s/2]])
CURVE20 = bezier.Curve.from_nodes(np.asfortranarray([
    [1.0, 0.0],
    [-1.0, 0.25],
    [1.0, 0.5],
]), _copy=False)
# g21 = sympy.Matrix([[
#     (10 * s - 1) / 8,
#     (9 - 10 * s) * (10 * s - 1) / 32,
# ]])
CURVE21 = bezier.Curve.from_nodes(np.asfortranarray([
    [-0.125, -0.28125],
    [0.5, 1.28125],
    [1.125, -0.28125],
]), _copy=False)
# g22 = sympy.Matrix([[25 * (2 * s - 1)**2 / 16, (10 * s - 1)  / 16]])
CURVE22 = bezier.Curve.from_nodes(np.asfortranarray([
    [1.5625, -0.0625],
    [-1.5625, 0.25],
    [1.5625, 0.5625],
]), _copy=False)
# g23 = 5 * g8 + sympy.Matrix([[24, 21]]) / 8
# g23 = sympy.Matrix([[10 * s + 6, 9]]) / 2
CURVE23 = bezier.Curve.from_nodes(np.asfortranarray([
    [3.0, 4.5],
    [8.0, 4.5],
]), _copy=False)
# g24 = sympy.Matrix([[(4 * s + 1) / 4, (3 - 4 * s) * (4 * s + 1) / 8]])
CURVE24 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.25, 0.375],
    [0.75, 0.875],
    [1.25, -0.625],
]), _copy=False)
# g25 = sympy.Matrix([[
#     -s * (2 * s**2 - 3 * s - 3) / 4,
#     -(3 * s**3 - 3 * s - 1) / 2,
# ]])
CURVE25 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.5],
    [0.25, 1.0],
    [0.75, 1.5],
    [1.0, 0.5],
]), _copy=False)
# g26 = sympy.Matrix([[
#     3 * (14 * s + 1) / 8,
#     18 * s**3 - 27 * s**2 + 3 * s + 7,
# ]])
CURVE26 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.375, 7.0],
    [2.125, 8.0],
    [3.875, 0.0],
    [5.625, 1.0],
]), _copy=False)
# g27 = sympy.Matrix([[
#     (6 * s + 1) / 8,
#     (35 * s**3 - 60 * s**2 + 24 * s + 4) / 16,
# ]])
CURVE27 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.125, 0.25],
    [0.375, 0.75],
    [0.625, 0.0],
    [0.875, 0.1875],
]), _copy=False)
# Rotate g1 by 45 degrees and scale by sqrt(2).
# g28 = sympy.Matrix([[s * (2 * s - 1), s * (3 - 2 * s)]])
CURVE28 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.0, 0.0],
    [-0.5, 1.5],
    [1.0, 1.0],
]), _copy=False)
# Rotate g6 by 45 degrees and scale by sqrt(2).
# g29 = sympy.Matrix([[(1 - 2 * s) * (1 - s), 2 * s**2 - s + 1]])
CURVE29 = bezier.Curve.from_nodes(np.asfortranarray([
    [-1.0, 1.0],
    [0.5, 0.5],
    [0.0, 2.0],
]), _copy=False)
# Rotate g9 by 45 degrees and scale by sqrt(2).
# g30 = sympy.Matrix([[(2 - 3 * s) / 4, (2 + 3 * s) / 4]])
CURVE30 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.5, 0.5],
    [-0.25, 1.25],
]), _copy=False)
# g31 = 2 * g11 + sympy.Matrix([[1, 3]]) / 4
# g31 = sympy.Matrix([[(48 * s + 1) / 4, (67 - 64 * s) / 4]])
CURVE31 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.25, 16.75],
    [12.25, 0.75],
]), _copy=False)
# g32 = sympy.Matrix([[(7 * s - 2) / 8, -1 / 4]])
# NOTE: This is a degree-elevated line.
CURVE32 = bezier.Curve.from_nodes(np.asfortranarray([
    [-0.25, -0.25],
    [0.1875, -0.25],
    [0.625, -0.25],
]), _copy=False)
# g33 = sympy.Matrix([[(1 - 2 * s) * (s - 1) / 8, -s]])
CURVE33 = bezier.Curve.from_nodes(np.asfortranarray([
    [-0.125, 0.0],
    [0.0625, -0.5],
    [0.0, -1.0],
]), _copy=False)
# g34 = sympy.Matrix([[4, 3 * (2 * s + 5)]]) / 8
CURVE34 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.5, 1.875],
    [0.5, 2.625],
]), _copy=False)
# g35 = sympy.Matrix([[5 * (1 - 2 * s), 21]]) / 8
CURVE35 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.625, 2.625],
    [-0.625, 2.625],
]), _copy=False)
# g36 = sympy.Matrix([[(1 - s) / 2, -3 * (s + 1) / 8]])
CURVE36 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.5, -0.375],
    [0.0, -0.75],
]), _copy=False)
# g37 = sympy.Matrix([[(7 * s - 2) / 4, 7 * (s - 1) / 8]])
CURVE37 = bezier.Curve.from_nodes(np.asfortranarray([
    [-0.5, -0.875],
    [1.25, 0.0],
]), _copy=False)
# g38 = sympy.Matrix([[(3 * s + 1) / 2, (3 * s - 1)**2 / 8]])
CURVE38 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.5, 0.125],
    [1.25, -0.25],
    [2.0, 0.5],
]), _copy=False)
# g39 = sympy.Matrix([[(2 * s + 1) / 2, -(2 * s - 1)**2 / 8]])
CURVE39 = bezier.Curve.from_nodes(np.asfortranarray([
    [0.5, -0.125],
    [1.0, 0.125],
    [1.5, -0.125],
]), _copy=False)


def make_plots(curve1, curve2, points, ignore_save=False, failed=True):
    if not CONFIG.running:
        return

    ax = curve1.plot(64)
    curve2.plot(64, ax=ax)
    ax.plot(points[:, 0], points[:, 1],
            marker='o', linestyle='None', color='black')
    ax.axis('scaled')
    _plot_helpers.add_plot_boundary(ax)

    if CONFIG.save_plot:
        if not ignore_save:
            CONFIG.save_fig()
    else:
        if failed:
            plt.title(CONFIG.current_test + ': failed')
        else:
            plt.title(CONFIG.current_test)
        plt.show()

    plt.close(ax.figure)


def curve_curve_check(curve1, curve2, s_vals, t_vals, points,
                      ignore_save=False):
    assert len(s_vals) == len(t_vals)
    assert len(s_vals) == len(points)

    intersections = _intersection_helpers.all_intersections(
        [(curve1, curve2)])
    assert len(intersections) == len(s_vals)

    info = six.moves.zip(intersections, s_vals, t_vals, points)
    for intersection, s_val, t_val, point in info:
        assert intersection.first is curve1
        assert intersection.second is curve2

        CONFIG.assert_close(intersection.s, s_val)
        CONFIG.assert_close(intersection.t, t_val)

        computed_point = intersection.get_point()
        CONFIG.assert_close(computed_point[0, 0], point[0])
        CONFIG.assert_close(computed_point[0, 1], point[1])

        point_on1 = curve1.evaluate(s_val)
        CONFIG.assert_close(point_on1[0, 0], point[0])
        CONFIG.assert_close(point_on1[0, 1], point[1])

        point_on2 = curve2.evaluate(t_val)
        CONFIG.assert_close(point_on2[0, 0], point[0])
        CONFIG.assert_close(point_on2[0, 1], point[1])

    make_plots(curve1, curve2, points, ignore_save=ignore_save, failed=False)


def test_curves1_and_2():
    sq31 = np.sqrt(31.0)
    s_val0 = 0.0625 * (9.0 - sq31)
    s_val1 = 0.0625 * (9.0 + sq31)

    s_vals = np.asfortranarray([s_val0, s_val1])
    t_vals = np.asfortranarray([s_val1, s_val0])
    points = np.asfortranarray([
        [s_val0, (16.0 + sq31) / 64.0],
        [s_val1, (16.0 - sq31) / 64.0],
    ])
    curve_curve_check(CURVE1, CURVE2, s_vals, t_vals, points)


def test_curves3_and_4():
    s_vals = np.asfortranarray([0.25, 0.875])
    t_vals = np.asfortranarray([0.75, 0.25])
    points = np.asfortranarray([
        [0.75, 1.125],
        [2.625, 0.65625],
    ])
    curve_curve_check(CURVE3, CURVE4, s_vals, t_vals, points)


def test_curves1_and_5():
    s_vals = np.asfortranarray([0.25, 0.75])
    t_vals = s_vals
    points = np.asfortranarray([
        [0.25, 0.375],
        [0.75, 0.375],
    ])
    curve_curve_check(CURVE1, CURVE5, s_vals, t_vals, points)


def test_curves1_and_6():
    s_vals = np.asfortranarray([0.5])
    t_vals = s_vals
    points = np.asfortranarray([
        [0.5, 0.5],
    ])
    curve_curve_check(CURVE1, CURVE6, s_vals, t_vals, points)


def test_curves1_and_7():
    delta = 2.0 / np.sqrt(33.0)
    s_val0 = 0.5 - delta
    s_val1 = 0.5 + delta

    s_vals = np.asfortranarray([s_val0, s_val1])
    t_vals = s_vals
    y_val = 17.0 / 66.0
    points = np.asfortranarray([
        [s_val0, y_val],
        [s_val1, y_val],
    ])
    curve_curve_check(CURVE1, CURVE7, s_vals, t_vals, points)


def test_curves1_and_8():
    s_vals = np.asfortranarray([0.25, 0.75])
    t_vals = s_vals
    points = np.asfortranarray([
        [0.25, 0.375],
        [0.75, 0.375],
    ])
    curve_curve_check(CURVE1, CURVE8, s_vals, t_vals, points)


def test_curves1_and_9():
    s_vals = np.asfortranarray([0.5])
    t_vals = np.asfortranarray([2.0 / 3.0])
    points = np.asfortranarray([
        [0.5, 0.5],
    ])
    curve_curve_check(CURVE1, CURVE9, s_vals, t_vals, points)


def test_curves10_and_11():
    s_vals = np.asfortranarray([1.0 / 3.0])
    t_vals = np.asfortranarray([0.5])
    points = np.asfortranarray([
        [3.0, 4.0],
    ])
    curve_curve_check(CURVE10, CURVE11, s_vals, t_vals, points)


def test_curve12_self_crossing():
    left, right = CURVE12.subdivide()
    # Re-create left and right so they aren't sub-curves. This is just to
    # satisfy a quirk of ``curve_curve_check``, not an issue with the
    # library.
    left = bezier.Curve(left.nodes, left.degree)
    right = bezier.Curve(right.nodes, right.degree)

    delta = np.sqrt(5.0) / 3.0
    s_vals = np.asfortranarray([1.0, 1.0 - delta])
    t_vals = np.asfortranarray([0.0, delta])
    points = np.asfortranarray([
        [-0.09375, 0.828125],
        [-0.25, 1.375],
    ])

    curve_curve_check(left, right, s_vals, t_vals, points)

    # Make sure the left curve doesn't cross itself.
    left1, right1 = left.subdivide()
    expected = right1.evaluate_multi(np.asfortranarray([0.0]))
    curve_curve_check(bezier.Curve(left1.nodes, left1.degree),
                      bezier.Curve(right1.nodes, right1.degree),
                      np.asfortranarray([1.0]),
                      np.asfortranarray([0.0]),
                      expected, ignore_save=True)

    # Make sure the right curve doesn't cross itself.
    left2, right2 = right.subdivide()
    expected = right2.evaluate_multi(np.asfortranarray([0.0]))
    curve_curve_check(bezier.Curve(left2.nodes, left2.degree),
                      bezier.Curve(right2.nodes, right2.degree),
                      np.asfortranarray([1.0]),
                      np.asfortranarray([0.0]),
                      expected, ignore_save=True)


def test_curves8_and_9():
    s_vals = np.asfortranarray([0.5])
    t_vals = np.asfortranarray([0.5])
    points = np.asfortranarray([
        [0.5, 0.375],
    ])
    curve_curve_check(CURVE8, CURVE9, s_vals, t_vals, points)


def test_curves1_and_13():
    delta = 0.5 / np.sqrt(7.0)
    s_vals = np.asfortranarray([0.5 - delta, 0.5 + delta, 0.0, 1.0])
    t_vals = s_vals
    points = np.asfortranarray([
        [0.5 - delta, 3.0 / 7.0],
        [0.5 + delta, 3.0 / 7.0],
        [0.0, 0.0],
        [1.0, 0.0],
    ])
    curve_curve_check(CURVE1, CURVE13, s_vals, t_vals, points)


def test_curves14_and_15():
    s_vals = np.asfortranarray([2.0 / 3.0])
    t_vals = np.asfortranarray([1.0 / 3.0])
    points = np.asfortranarray([
        [0.5, 0.5],
    ])
    with pytest.raises(NotImplementedError):
        curve_curve_check(CURVE14, CURVE15, s_vals, t_vals, points)

    make_plots(CURVE14, CURVE15, points)


def test_curves14_and_16():
    s_vals = np.asfortranarray([3.0, 5.0]) / 6.0
    t_vals = np.asfortranarray([1.0, 3.0]) / 6.0
    points = np.asfortranarray([
        [0.375, 0.46875],
        [0.625, 0.46875],
    ])
    curve_curve_check(CURVE14, CURVE16, s_vals, t_vals, points)


def test_curves10_and_17():
    s_vals = np.asfortranarray([1.0 / 3.0])
    t_vals = np.asfortranarray([1.0])
    points = np.asfortranarray([
        [3.0, 4.0],
    ])
    curve_curve_check(CURVE10, CURVE17, s_vals, t_vals, points)


def test_curves1_and_18():
    s_vals = np.asfortranarray([1.0])
    t_vals = np.asfortranarray([0.0])
    points = np.asfortranarray([
        [1.0, 0.0],
    ])
    curve_curve_check(CURVE1, CURVE18, s_vals, t_vals, points)


def test_curves1_and_19():
    s_vals = np.asfortranarray([1.0])
    t_vals = np.asfortranarray([1.0])
    points = np.asfortranarray([
        [1.0, 0.0],
    ])
    curve_curve_check(CURVE1, CURVE19, s_vals, t_vals, points)


def test_curves1_and_20():
    delta = np.sqrt(5.0) / 8.0
    s_vals = np.asfortranarray([0.25, 0.375 - delta, 1.0, 0.375 + delta])
    t_vals = np.asfortranarray([0.75, 0.625 - delta, 0.0, 0.625 + delta])
    points = np.asfortranarray([
        [0.25, 0.375],
        [0.375 - delta, 0.3125 - 0.5 * delta],
        [1.0, 0.0],
        [0.375 + delta, 0.3125 + 0.5 * delta],
    ])
    curve_curve_check(CURVE1, CURVE20, s_vals, t_vals, points)


def test_curves20_and_21():
    sq5 = np.sqrt(5.0)
    s_vals = np.asfortranarray([
        0.625 - 0.125 * sq5, 0.0, 0.75, 0.625 + 0.125 * sq5])
    t_vals = np.asfortranarray([4.0 - sq5, 9.0, 3.0, 4.0 + sq5]) / 10.0
    points = np.asfortranarray([
        [0.375 - 0.125 * sq5, 0.3125 - 0.0625 * sq5],
        [1.0, 0.0],
        [0.25, 0.375],
        [0.375 + 0.125 * sq5, 0.3125 + 0.0625 * sq5],
    ])
    curve_curve_check(CURVE20, CURVE21, s_vals, t_vals, points)


def test_curves21_and_22():
    sq5 = np.sqrt(5.0)
    s_vals = np.asfortranarray([4.0 - sq5, 3.0, 9.0, 4.0 + sq5]) / 10.0
    t_vals = np.asfortranarray([6.0 - sq5, 7.0, 1.0, 6.0 + sq5]) / 10.0
    points = np.asfortranarray([
        [0.375 - 0.125 * sq5, 0.3125 - 0.0625 * sq5],
        [0.25, 0.375],
        [1.0, 0.0],
        [0.375 + 0.125 * sq5, 0.3125 + 0.0625 * sq5],
    ])

    # NOTE: We require a bit more wiggle room for these roots.
    with CONFIG.wiggle(12):
        curve_curve_check(CURVE21, CURVE22, s_vals, t_vals, points)


def test_curves10_and_23():
    s_vals = np.asfortranarray([0.5])
    t_vals = np.asfortranarray([3.0 / 10.0])
    points = np.asfortranarray([
        [4.5, 4.5],
    ])
    curve_curve_check(CURVE10, CURVE23, s_vals, t_vals, points)


def test_curves1_and_24():
    # NOTE: This is two coincident curves, i.e. CURVE1 on
    #       [1/4, 1] is identical to CURVE24 on [0, 3/4].
    left_vals = CURVE1.evaluate_multi(
        np.linspace(0.25, 1.0, 2**8 + 1))
    right_vals = CURVE24.evaluate_multi(
        np.linspace(0.0, 0.75, 2**8 + 1))
    assert np.all(left_vals == right_vals)

    s_vals = np.asfortranarray([0.25, 1.0])
    t_vals = np.asfortranarray([0.0, 0.75])
    points = np.asfortranarray([
        [0.25, 0.375],
        [1.0, 0.0],
    ])
    with pytest.raises(NotImplementedError):
        curve_curve_check(CURVE1, CURVE24, s_vals, t_vals, points)

    make_plots(CURVE1, CURVE24, points)


def test_curves15_and_25():
    # ctx = mpmath.MPContext()
    # ctx.prec = 200
    # ctx.polyroots([486, -3726, 13905, -18405, 6213, 1231])
    s_vals = np.asfortranarray([float.fromhex('0x1.b7b348cf939b9p-1')])
    # ctx.polyroots([4, -16, 13, 25, -28, 4])
    t_vals = np.asfortranarray([float.fromhex('0x1.bf3536665a0cdp-1')])

    # Slightly more accurate than (3 s + 1) / 4.
    x_val = float.fromhex('0x1.c9c6769baeb4ap-1')
    # identical to (9 s^2 - 6 s + 5) / 8 after rounding.
    y_val = float.fromhex('0x1.9f09401c281ddp-1')
    points = np.asfortranarray([
        [x_val, y_val],
    ])
    curve_curve_check(CURVE15, CURVE25, s_vals, t_vals, points)


def test_curves11_and_26():
    sq7 = np.sqrt(7.0)
    s_vals = np.asfortranarray(
        [24.0, 24.0 - 7.0 * sq7, 24.0 + 7.0 * sq7]) / 48.0
    t_vals = np.asfortranarray([3.0, 3.0 - sq7, 3.0 + sq7]) / 6.0
    points = np.asfortranarray([
        [72.0, 96.0],
        [72.0 - 21.0 * sq7, 96.0 + 28.0 * sq7],
        [72.0 + 21.0 * sq7, 96.0 - 28.0 * sq7],
    ]) / 24.0

    # NOTE: We require a bit more wiggle room for these roots.
    with CONFIG.wiggle(25):
        curve_curve_check(CURVE11, CURVE26, s_vals, t_vals, points)


def test_curves8_and_27():
    s_val1, s_val2, _ = runtime_utils.real_roots(
        [17920, -29760, 13512, -1691])
    s_vals = np.asfortranarray([s_val2, s_val1])
    t_val1, t_val2, _ = runtime_utils.real_roots([35, -60, 24, -2])
    t_vals = np.asfortranarray([t_val2, t_val1])
    points = np.asfortranarray([
        [s_val2, 0.375],
        [s_val1, 0.375],
    ])

    # NOTE: We require a bit more wiggle room for these roots.
    with CONFIG.wiggle(42):
        curve_curve_check(CURVE8, CURVE27, s_vals, t_vals, points)


def test_curves28_and_29():
    # NOTE: Though curves 1 and 6 successfully intersect (at a point
    #       of tangency), the rotated equivalents do not.
    s_vals = np.asfortranarray([0.5])
    t_vals = s_vals
    points = np.asfortranarray([
        [0.0, 1.0],
    ])
    with pytest.raises(NotImplementedError):
        curve_curve_check(CURVE28, CURVE29, s_vals, t_vals, points)

    make_plots(CURVE28, CURVE29, points)


def test_curves29_and_30():
    s_vals = np.asfortranarray([0.5])
    t_vals = np.asfortranarray([2.0 / 3.0])
    points = np.asfortranarray([
        [0.0, 1.0],
    ])
    curve_curve_check(CURVE29, CURVE30, s_vals, t_vals, points)


def test_curves8_and_23():
    s_vals = np.zeros((0,))
    t_vals = s_vals
    points = np.zeros((0, 2))
    curve_curve_check(CURVE8, CURVE23, s_vals, t_vals, points)


def test_curves11_and_31():
    s_vals = np.zeros((0,))
    t_vals = s_vals
    points = np.zeros((0, 2))
    curve_curve_check(CURVE11, CURVE31, s_vals, t_vals, points)


def test_curves32_and_33():
    s_vals = np.asfortranarray([13.0 / 56.0])
    t_vals = np.asfortranarray([0.25])
    points = np.asfortranarray([
        [-0.046875, -0.25],
    ])

    # NOTE: We allow less wiggle room for this intersection.
    with CONFIG.wiggle(4):
        curve_curve_check(CURVE32, CURVE33, s_vals, t_vals, points)


def test_curves34_and_35():
    s_vals = np.asfortranarray([1.0])
    t_vals = np.asfortranarray([1.0 / 10.0])
    points = np.asfortranarray([
        [0.5, 2.625],
    ])

    curve_curve_check(CURVE34, CURVE35, s_vals, t_vals, points)


def test_curves36_and_37():
    s_vals = np.asfortranarray([0.0])
    t_vals = np.asfortranarray([4.0 / 7.0])
    points = np.asfortranarray([
        [0.5, -0.375],
    ])

    curve_curve_check(CURVE36, CURVE37, s_vals, t_vals, points)


@pytest.mark.xfail
def test_curves38_and_39():
    s_vals = np.asfortranarray([1.0 / 3.0])
    t_vals = np.asfortranarray([0.5])
    points = np.asfortranarray([
        [1.0, 0.0],
    ])

    curve_curve_check(CURVE38, CURVE39, s_vals, t_vals, points)


if __name__ == '__main__':
    CONFIG.run(globals())
