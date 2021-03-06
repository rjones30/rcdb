from datetime import datetime
import unittest
import rcdb
import rcdb.model
from rcdb.model import ConditionType, Condition, Run

import logging

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class TestConditions(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)
        rcdb.provider.destroy_all_create_schema(self.db)
        # create run
        self.db.create_run(1)

    def tearDown(self):
        self.db.disconnect()

    def test_creating_condition_type(self):
        """Test of create_condition_type function"""

        # Create condition type
        ct = self.db.create_condition_type("test", ConditionType.FLOAT_FIELD, "This is a test")

        # Check values
        self.assertIsInstance(ct, ConditionType)
        self.assertEqual(ct.name, "test")
        self.assertEqual(ct.value_type, ConditionType.FLOAT_FIELD)
        self.assertEqual(ct.description, "This is a test")

        # Creating ConditionType with the same name but different type or flag should raise
        self.assertRaises(rcdb.OverrideConditionTypeError, self.db.create_condition_type, "test", ConditionType.INT_FIELD, "This is a test")
        self.assertRaises(rcdb.OverrideConditionTypeError, self.db.create_condition_type, "test", ConditionType.FLOAT_FIELD, "He")

        # Creating the same existing ConditionType should not raise
        try:
            self.db.create_condition_type("test", ConditionType.FLOAT_FIELD, "This is a test")
        except rcdb.OverrideConditionTypeError:
            self.fail()

    def test_get_condition_type(self):
        """Test of get_condition_type function"""
        # Create condition type
        ct = self.db.create_condition_type("test", ConditionType.FLOAT_FIELD, "Description")

        # now get it from DB using API
        ct = self.db.get_condition_type("test")
        self.assertEqual(ct.name, "test")
        self.assertEqual(ct.description, "Description")
        self.assertEqual(ct.value_type, ConditionType.FLOAT_FIELD)

        # now check that there is no way selecting non existent
        self.assertRaises(rcdb.NoConditionTypeFound, self.db.get_condition_type, "abra kadabra")

    def test_basic_work_with_condition_value(self):
        """ Tests add_condition_value funciton
        :return:None
        """
        ct = self.db.create_condition_type("events_num", ConditionType.FLOAT_FIELD, "Number of events")
        self.db.add_condition(1, "events_num", 1000)
        result = self.db.get_condition(1, "events_num")
        self.assertEqual(result.value, 1000)

    # TEST
    def test_one_per_run_condition_values(self):
        ct = self.db.create_condition_type("single", ConditionType.INT_FIELD, "Description")

        # First addition to DB
        val = self.db.add_condition(1, ct, 1000)

        # The func should return ConditionValue it created or found in BD
        self.assertIsNotNone(val)

        # Ok. no exception and do nothing is the very same value already exists
        val = self.db.add_condition(1, "single", 1000)
        self.assertIsNotNone(val)

        # Error. exception ConditionValueExistsError
        self.assertRaises(rcdb.OverrideConditionValueError, self.db.add_condition, 1, "single", 2222)

        # Ok. Replacing existing value
        val = self.db.add_condition(1, "single", 2222, replace=True)
        self.assertIsNotNone(val)

        # Check, that get method works as expected
        val = self.db.get_condition(1, "single")
        self.assertEqual(val.value, 2222)
        self.assertEqual(val.int_value, 2222)
        self.assertIsNone(val.time_value)

        # Add time information to the
        val = self.db.add_condition(1, "single", 2222, replace=True)
        self.assertIsNotNone(val)

        # Create condition for non existent run is impossible
        self.assertRaises(rcdb.NoRunFoundError, self.db.add_condition, 1763654, "single", 2222)

    def test_check_float_condition_value(self):
        """ Tests add_condition_value funciton
        :return:None
        """
        ct = self.db.create_condition_type("float_cnd", ConditionType.FLOAT_FIELD, "")
        cnd = self.db.add_condition(1, ct, 0.15)

        # evict all database-loaded data from the session
        self.db.session.expire_all()

        result = self.db.get_condition(1, "float_cnd")
        self.assertEqual(result.value, 0.15)

    def test_run_link_to_conditions(self):
        """ Tests add_condition_value funciton
        :return:None
        """
        ct = self.db.create_condition_type("one", ConditionType.INT_FIELD, "")
        self.db.add_condition(1, "one", 1000)
        ct = self.db.create_condition_type("two", ConditionType.INT_FIELD, "")
        self.db.add_condition(1, "two", 2000)

        run = self.db.get_run(1)

        self.assertGreaterEqual(len(run.conditions),  2)
        names = [condition.name for condition in run.conditions]
        self.assertIn("one", names)
        self.assertIn("two", names)

    def test_query(self):
        """ Tests add_condition_value function
        :return:None
        """
        ct = self.db.create_condition_type("one", ConditionType.INT_FIELD, "")
        ct = self.db.create_condition_type("two", ConditionType.INT_FIELD, "")

        for i in range(101, 110):
            self.db.create_run(i)
            self.db.add_condition(i, "one", (i-100)*10)
            self.db.add_condition(i, "two", (i-100)*100)

    def test_usage_of_string_values(self):
        self.db.create_condition_type("string_val", ConditionType.STRING_FIELD, "")
        self.db.add_condition(1, "string_val", "test test")
        val = self.db.get_condition(1, "string_val")
        self.assertEqual(val.value, "test test")

    def test_time_only_condition(self):
        """Test how to work with time information too"""

        self.db.create_condition_type("lunch_bell_rang", ConditionType.TIME_FIELD, "")

        # add value to run 1
        time = datetime(2015, 9, 1, 14, 21, 1)
        self.db.add_condition(1, "lunch_bell_rang", time)

        # get from DB
        val = self.db.get_condition(1, "lunch_bell_rang")
        self.assertEqual(val.value, time)
        self.assertEqual(val.time_value, time)


    def test_use_run_instead_of_run_number(self):

        run = self.db.create_run(2)
        ct = self.db.create_condition_type("lalala", ConditionType.INT_FIELD, "")
        val = self.db.add_condition(run, ct, 10)      # event_count in range 950 - 1049

        self.assertEqual(val.run_number, 2)

    def test_get_condition(self):
        self.db.create_condition_type("one", ConditionType.INT_FIELD, "")
        self.db.create_condition_type("two", ConditionType.INT_FIELD, "")
        self.db.add_condition(1, "one", 10)

        self.assertEqual(self.db.get_run(1).get_condition("one").value, 10)
        self.assertIsNone(self.db.get_run(1).get_condition("two"))

    def test_double_penetration(self):
        self.db.create_condition_type("one", ConditionType.INT_FIELD, "")
        self.db.create_run(5665)
        self.db.add_condition(5665, "one", 10)
        self.db.add_condition(5665, "one", 10)
        run = self.db.get_run(5665)

        self.assertEqual(len(run.conditions), 1)

    def test_add_conditions_list_lists(self):
        self.db.create_condition_type("one", ConditionType.INT_FIELD, "")
        self.db.create_condition_type("two", ConditionType.INT_FIELD, "")
        run = self.db.create_run(5665)
        result = self.db.add_conditions(5665, [["one", 10], ["two", 20]])
        self.assertEqual(len(run.conditions), 2)
        self.assertEqual(len(result), 2)
        self.assertSequenceEqual(result, run.conditions)

    def test_add_conditions_dict(self):
        self.db.create_condition_type("one", ConditionType.INT_FIELD, "")
        self.db.create_condition_type("two", ConditionType.INT_FIELD, "")
        run = self.db.create_run(5665)
        result = self.db.add_conditions(5665, {"one": 10, "two": 20})
        self.assertEqual(len(run.conditions), 2)
        self.assertEqual(len(result), 2)
        self.assertSequenceEqual(result, run.conditions)

    def test_add_conditions_failure(self):
        self.db.create_condition_type("one", ConditionType.INT_FIELD, "")
        self.assertRaises(KeyError, self.db.add_conditions, 1, [["one", 10], ["one", 20]])




















