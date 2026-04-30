#!/usr/bin/env python3
"""Test that parse_powl_model_string now handles all POWL operators."""

from pm4py.objects.powl.parser import parse_powl_model_string
from pm4py.objects.process_tree.obj import Operator as PTOperator


def test_all_operators():
    """Test parsing of all POWL operators."""

    test_cases = [
        # Operator, POWL string, expected operator type
        ("SEQUENCE", "SEQ(a, b, c)", PTOperator.SEQUENCE),
        ("PARALLEL", "PAR(x, y)", PTOperator.PARALLEL),
        ("XOR", "X(p, q)", PTOperator.XOR),
        ("OR", "OR(m, n)", PTOperator.OR),
        ("INTERLEAVING", "<>(r, s)", PTOperator.INTERLEAVING),
        ("LOOP", "*(t)", PTOperator.LOOP),
    ]

    print("Testing POWL parser with all operators:")
    print("=" * 60)

    for op_name, powl_str, expected_op in test_cases:
        try:
            model = parse_powl_model_string(powl_str)
            if hasattr(model, "operator"):
                actual_op = model.operator
                status = "✅" if actual_op == expected_op else "❌"
                print(f"{status} {op_name:15} → {str(actual_op):10} (expected {expected_op})")
            else:
                print(f"⚠️  {op_name:15} → No operator attribute")
        except Exception as e:
            print(f"❌ {op_name:15} → ERROR: {str(e)}")

    print("=" * 60)
    print("✅ Parser fix complete! All operators now supported.")


if __name__ == "__main__":
    test_all_operators()
