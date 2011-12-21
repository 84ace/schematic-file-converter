# encoding: utf-8
from parser.kicad import KiCAD
from parser.openjson import JSON
import unittest

from os.path import dirname, join

TEST_DIR = join(dirname(__file__), '..', '..', 'test', 'kicad')

TEST_INPUT_FILE = join(TEST_DIR, 'test.sch')
GOOD_OUTPUT_FILE = join(TEST_DIR, 'test.upv')


class KiCADTests(unittest.TestCase):

    def setUp(self):
        """ Set load the test files """
        self.good = JSON().parse(GOOD_OUTPUT_FILE)
        self.actual = KiCAD().parse(TEST_INPUT_FILE)


    def test_design_attributes(self):
        """ All the design attributes are correct """

        self.assert_annotations_equal(
            self.actual.design_attributes.annotations,
            self.good.design_attributes.annotations)


    def test_points(self):
        """
        Test that all the points are present and have the right
        positions and connected points and components.
        """

        good_points = {}

        for net in self.good.nets:
            for pid, p in net.points.items():
                good_points[pid] = p

        self.assertEqual(len(good_points), 24)

        for net in self.actual.nets:
            for pid, p in net.points.items():
                goodp = good_points.pop(pid)
                self.assertEqual(p.point_id, goodp.point_id)
                self.assertEqual(p.x, goodp.x)
                self.assertEqual(p.y, goodp.y)
                self.assertEqual(set(p.connected_points),
                                 set(goodp.connected_points))
                self.assertEqual(
                    set((cc.instance_id, cc.pin_number)
                        for cc in p.connected_components),
                    set((cc.instance_id, cc.pin_number)
                        for cc in goodp.connected_components))

        self.assertEqual(good_points, {})


    def test_nets(self):
        """
        Test that all the right nets are present with
        the right points.
        """

        good_nets = self.good.nets[:]

        self.assertEqual(len(good_nets), 5)

        for net in self.actual.nets:
            for goodnet in good_nets:
                if set(net.points) == set(goodnet.points):
                    good_nets.remove(goodnet)
                    break
            else:
                raise Exception('bad net', net)

        self.assertEqual(good_nets, [])


    def test_components(self):
        """
        Test that all the right components are present
        with the correct values.
        """

        good_cpts = self.good.components.components.copy()

        for cid, cpt in self.actual.components.components.items():
            goodcpt = good_cpts.pop(cid)

            self.assertEqual(cpt.name, goodcpt.name)
            self.assertEqual(cpt.attributes, goodcpt.attributes)
            self.assertEqual(len(cpt.symbols), len(goodcpt.symbols))

            for sym, goodsym in zip(cpt.symbols, goodcpt.symbols):
                self.assertEqual(len(sym.bodies), len(goodsym.bodies))

                for body, goodbody in zip(sym.bodies, goodsym.bodies):
                    self.assertEqual(len(body.shapes), len(goodbody.shapes))
                    for shape, goodshape in zip(body.shapes, goodbody.shapes):
                        self.assertEqual(shape.__class__, goodshape.__class__)
                        self.assertEqual(shape.json(), goodshape.json())

                    self.assertEqual(len(body.pins), len(goodbody.pins))
                    for pin, goodpin in zip(body.pins, goodbody.pins):
                        self.assertEqual(pin.__class__, goodpin.__class__)
                        self.assertEqual(pin.json(), goodpin.json())

        self.assertEqual(good_cpts, {})


    def test_component_instances(self):
        """
        Test that the component instances were loaded correctly.
        """

        good_insts = self.good.component_instances[:]
        test_insts = self.actual.component_instances[:]

        while good_insts:
            good_inst = good_insts.pop(0)
            for test_inst in test_insts:
                if good_inst.instance_id == test_inst.instance_id:
                    test_insts.remove(test_inst)
                    break
            else:
                raise Exception('missing instance', good_inst.instance_id)

            self.assertEqual(test_inst.library_id, good_inst.library_id)
            self.assertEqual(test_inst.attributes, good_inst.attributes)
            self.assertEqual(test_inst.symbol_index, good_inst.symbol_index)

            self.assertEqual(len(test_inst.symbol_attributes),
                             len(good_inst.symbol_attributes))

            for test_sa, good_sa in zip(test_inst.symbol_attributes,
                                        good_inst.symbol_attributes):
                self.assertEqual(test_sa.x, good_sa.x)
                self.assertEqual(test_sa.y, good_sa.y)
                self.assertEqual(test_sa.rotation, good_sa.rotation)
                self.assert_annotations_equal(test_sa.annotations,
                                              good_sa.annotations)

        self.assertEqual(test_insts, [])

    def assert_annotations_equal(self, test_anns, good_anns):
        self.assertEqual(len(test_anns), len(good_anns))
        for test_ann, good_ann in zip(test_anns, good_anns):
            self.assertEqual(test_ann.value, good_ann.value)
            self.assertEqual(test_ann.x, good_ann.x)
            self.assertEqual(test_ann.y, good_ann.y)
            self.assertEqual(test_ann.rotation, good_ann.rotation)
            self.assertEqual(test_ann.visible, good_ann.visible)
