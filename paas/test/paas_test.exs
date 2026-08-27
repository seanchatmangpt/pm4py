ExUnit.start()

defmodule Pm4pyPaaSTest do
  use ExUnit.Case, async: true

  test "AshR2RML constructs a ggen bundle without DO authority" do
    assert {:ok, bundle} =
             AshR2RML.Ggen.compile_ash_ttl_bundle([
               Pm4pyPaaS.DataService,
               Pm4pyPaaS.MiningRun,
               Pm4pyPaaS.Receipt
             ])

    assert bundle.status == :PARTIAL_ALIVE
    assert bundle.standing == :construct_only
    assert is_map(bundle.files)
    assert map_size(bundle.files) > 0
  end

  test "unsupported operations are refused before Python execution" do
    assert {:error, {:refused, "REFUSED_UNSUPPORTED_OPERATION", "exec_python"}} =
             Pm4pyPaaS.Worker.admit(%{
               run_id: "test-run",
               input_path: "fixture.xes",
               operation: "exec_python"
             })
  end
end
