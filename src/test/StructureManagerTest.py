import random
import shutil
import string
import unittest

from storage.StructureManager import *

TEST_PATH = '/tmp/TestNotebook/'
TEST_PICKLE = 'nb.tnb'
RAND_INPUT_UPPER_BOUND = 10000
RAND_INPUT_LOWER_BOUND = 0
STRING_CHOICES = string.ascii_letters + string.digits + string.punctuation + string.whitespace


def rand_input() -> str:
    return ''.join(random.choices(STRING_CHOICES, k=random.randint(RAND_INPUT_LOWER_BOUND, RAND_INPUT_UPPER_BOUND)))


class StructureManagerTest(unittest.TestCase):
    """ Unit tests for StructureManager
    """

    def setUp(self):
        self.structure_manager = StructureManager(TEST_PATH)

    def tearDown(self):
        if os.path.exists(TEST_PATH):
            shutil.rmtree(TEST_PATH)
        if os.path.exists(TEST_PICKLE):
            os.remove(TEST_PICKLE)

    def test_new_tab(self):
        tab = self.structure_manager.new_tab('Test Tab')
        self.assertEqual(1, len(self.structure_manager.components), "Incorrect number of tabs inserted")
        self.assertEqual(self.structure_manager.get_component(tab).name, 'Test Tab',
                         "Created tab does not have correct name")
        tab = self.structure_manager.new_tab()
        self.assertEqual(2, len(self.structure_manager.components), "Incorrect number of tabs or pages inserted")
        self.assertEqual("Tab " + str(self.structure_manager._total_tabs),
                         self.structure_manager.get_component(tab).name, "Default tab name incorrect")

    def test_new_page_error(self):
        with self.assertRaises(ValueError, msg="ValueError not raised with invalid page creation"):
            tab1 = self.structure_manager.new_tab()
            tab2 = self.structure_manager.new_tab()
            self.structure_manager.remove_component(tab1)
            self.structure_manager.new_page(tab1)
            self.structure_manager.remove_component(tab2)
            self.structure_manager.new_page(tab1)

    def test_new_page(self):
        tab = self.structure_manager.new_tab('Test')
        page = self.structure_manager.new_page(tab)
        self.assertEqual([page, tab], self.structure_manager.unroll_path(page), "Initial new page incorrect")
        self.assertEqual(DEFAULT_PAGE_NAME, self.structure_manager.get_component(page).name,
                         "Default page name incorrect")
        self.assertTrue(self.structure_manager.get_as_page(page).is_leaf(), "First page is not leaf")
        sub_page = self.structure_manager.new_page(page)
        self.assertEqual([sub_page, page, tab], self.structure_manager.unroll_path(sub_page),
                         "Document structure of sub-page not formed correctly")

    def test_remove_component(self):
        tab1 = self.structure_manager.new_tab()
        tab2 = self.structure_manager.new_tab()
        page1 = self.structure_manager.new_page(tab1)
        page2 = self.structure_manager.new_page(tab2)
        self.structure_manager.remove_component(page1)
        self.assertTrue(page1 not in self.structure_manager, "Remove of single page unsuccessful")
        self.assertTrue(page1 not in self.structure_manager.get_as_tab(tab1).pages,
                        "Remove of page from tab unsuccessful")
        self.structure_manager.remove_component(tab2)
        self.assertTrue(page2 not in self.structure_manager,
                        "Nested remove of page does not affect StructureManager")
        self.assertTrue(tab2 not in self.structure_manager, "Remove of tab does not affect StructureManager")

    def test_eq(self):
        _copy = copy.deepcopy(self.structure_manager)
        self.assertTrue(_copy == self.structure_manager, "Copied empty StructureManager is not equal")
        tab = self.structure_manager.new_tab()
        page = self.structure_manager.new_page(tab)
        _copy = copy.deepcopy(self.structure_manager)
        self.assertTrue(_copy == self.structure_manager, "Copied StructureManager is not equal")
        sm1 = StructureManager(TEST_PATH)
        self.assertTrue(sm1 != self.structure_manager, "Empty StructureManager is equal to non-empty StructureManager")
        self.assertTrue(StructureManager(TEST_PATH) != StructureManager(TEST_PATH + 'a'),
                        "StructureManagers with different paths considered equal")
        _copy.new_page(page)
        self.assertTrue(self.structure_manager != _copy, "Different populated StructureManagers considered equal")

    def test_persist(self):
        nb = os.path.join(TEST_PATH, TEST_PICKLE)
        StructureManager.persist(self.structure_manager, TEST_PICKLE)
        self.assertEqual(StructureManager.load_from_disk(nb), self.structure_manager,
                         "Empty StructureManager pickle not equal")
        tab = self.structure_manager.new_tab()
        page = self.structure_manager.new_page(tab)
        self.structure_manager.new_page(page)
        StructureManager.persist(self.structure_manager, TEST_PICKLE)
        self.assertEqual(StructureManager.load_from_disk(nb), self.structure_manager,
                         "Filled StructureManager pickle not equal")
        with open(nb, "wb") as f:
            pickle.dump({'hello': 0}, f)
        with self.assertRaises(TypeError, msg="Loading invalid pickle does not raise TypeError"):
            StructureManager.load_from_disk(nb)
        os.remove(nb)
