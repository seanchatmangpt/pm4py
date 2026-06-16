import os
import unittest

import pandas as pd

import pm4py


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TESTS_DIR)
OUTPUT_DIR = os.path.join(TESTS_DIR, "test_output_data")
EXAMPLE_CSV = os.path.join(REPO_DIR, "Order Management OCEL.csv")
EXAMPLE_XML = os.path.join(REPO_DIR, "Order Management OCEL.xml.gz")


class Ocel2CsvTest(unittest.TestCase):
    def test_ocel2_csv_import_export_roundtrip(self):
        source = os.path.join(OUTPUT_DIR, "ocel2_compact_source.csv")
        exported = os.path.join(OUTPUT_DIR, "ocel2_compact_exported.csv")

        dataframe = pd.DataFrame(
            [
                {
                    "id": "create_o1",
                    "activity": "create order",
                    "timestamp": "2024-01-01T10:00:00+0000",
                    "cost": "5",
                    "ot:employees": "Alice#employee",
                    "ot:items": 'i1#item{"price":3}',
                    "ot:orders": 'o1#order{"amount":10}',
                },
                {
                    "id": "pay_o1",
                    "activity": "pay order",
                    "timestamp": "2024-01-02T10:00:00+0000",
                    "cost": "",
                    "ot:employees": "",
                    "ot:items": "i1#item",
                    "ot:orders": "o1#order",
                },
                {
                    "id": "o1",
                    "activity": "o2o",
                    "timestamp": "",
                    "cost": "",
                    "ot:employees": "",
                    "ot:items": "i1#contains",
                    "ot:orders": "",
                },
                {
                    "id": "",
                    "activity": "",
                    "timestamp": "2024-01-03T10:00:00+0000",
                    "cost": "",
                    "ot:employees": 'Alice{"role":"manager"}',
                    "ot:items": "",
                    "ot:orders": "",
                },
                {
                    "id": "",
                    "activity": "",
                    "timestamp": "2024-01-04T10:00:00+0000",
                    "cost": "",
                    "ot:employees": 'Alice{"role":"lead"}',
                    "ot:items": "",
                    "ot:orders": "",
                },
            ]
        )

        try:
            dataframe.to_csv(source, index=False)

            ocel = pm4py.read_ocel2(source)
            self.assertEqual(len(ocel.events), 2)
            self.assertEqual(len(ocel.objects), 3)
            self.assertEqual(len(ocel.relations), 5)
            self.assertEqual(len(ocel.o2o), 1)
            self.assertEqual(len(ocel.object_changes), 1)
            self.assertEqual(
                set(ocel.objects[ocel.object_type_column].unique()),
                {"employees", "items", "orders"},
            )

            pm4py.write_ocel2(ocel, exported)
            imported = pm4py.read_ocel2(exported)

            self.assertEqual(len(imported.events), len(ocel.events))
            self.assertEqual(len(imported.objects), len(ocel.objects))
            self.assertEqual(len(imported.relations), len(ocel.relations))
            self.assertEqual(len(imported.o2o), len(ocel.o2o))
            self.assertEqual(len(imported.object_changes), len(ocel.object_changes))
        finally:
            for path in (source, exported):
                if os.path.exists(path):
                    os.remove(path)

    @unittest.skipUnless(
        os.path.exists(EXAMPLE_CSV) and os.path.exists(EXAMPLE_XML),
        "OCEL2 CSV/XML example files are not available",
    )
    def test_order_management_csv_matches_xml_counts(self):
        csv_ocel = pm4py.read_ocel2_csv(EXAMPLE_CSV)
        xml_ocel = pm4py.read_ocel2_xml(EXAMPLE_XML)

        self.assertEqual(len(csv_ocel.events), len(xml_ocel.events))
        self.assertEqual(len(csv_ocel.objects), len(xml_ocel.objects))
        self.assertEqual(len(csv_ocel.relations), len(xml_ocel.relations))
        self.assertEqual(len(csv_ocel.o2o), len(xml_ocel.o2o))
        self.assertEqual(len(csv_ocel.object_changes), len(xml_ocel.object_changes))

    @unittest.skipUnless(
        os.path.exists(EXAMPLE_XML),
        "OCEL2 XML example file is not available",
    )
    def test_order_management_xml_export_csv_roundtrip_counts(self):
        output_path = os.path.join(OUTPUT_DIR, "order_management_ocel2_export.csv")

        try:
            ocel = pm4py.read_ocel2_xml(EXAMPLE_XML)
            pm4py.write_ocel2_csv(ocel, output_path)
            imported = pm4py.read_ocel2_csv(output_path)

            self.assertEqual(len(imported.events), len(ocel.events))
            self.assertEqual(len(imported.objects), len(ocel.objects))
            self.assertEqual(len(imported.relations), len(ocel.relations))
            self.assertEqual(len(imported.o2o), len(ocel.o2o))
            self.assertEqual(len(imported.object_changes), len(ocel.object_changes))
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


if __name__ == "__main__":
    unittest.main()
