defmodule Pm4pyPaaS.RunMining do
  use Reactor

  input :run_id
  input :input_path
  input :operation

  step :admit do
    argument :run_id, input(:run_id)
    argument :input_path, input(:input_path)
    argument :operation, input(:operation)

    run fn args, _context -> Pm4pyPaaS.Worker.admit(args) end
  end

  step :execute do
    argument :request, result(:admit)
    run fn %{request: request}, _context -> Pm4pyPaaS.Worker.execute(request) end
  end

  step :record_run do
    argument :result, result(:execute)
    run fn %{result: result}, _context -> Pm4pyPaaS.Projections.record_run(result) end
  end

  step :record_receipt do
    argument :result, result(:record_run)
    run fn %{result: result}, _context -> Pm4pyPaaS.Projections.record_receipt(result) end
  end

  return :record_receipt
end

defmodule Pm4pyPaaS.Projections do
  @domain Pm4pyPaaS.Domain

  def record_run(result) do
    receipt = result["receipt"]

    attrs = %{
      id: receipt["run_id"],
      operation: receipt["operation"],
      input_sha256: receipt["input_sha256"],
      standing: receipt["standing"]
    }

    project(Pm4pyPaaS.MiningRun, attrs, [:operation, :input_sha256, :standing], result)
  end

  def record_receipt(result) do
    receipt = result["receipt"]

    attrs = %{
      id: receipt["run_id"],
      result_sha256: receipt["result_sha256"],
      source_sha: receipt["source_sha"]
    }

    project(Pm4pyPaaS.Receipt, attrs, [:result_sha256, :source_sha], result)
  end

  defp project(resource, %{id: id} = attrs, verified_fields, result) do
    case Ash.get(resource, id, domain: @domain) do
      {:ok, nil} -> create_projection(resource, attrs, result)
      {:ok, existing} -> verify_projection(existing, attrs, verified_fields, result)
      {:error, error} -> {:error, {:projection_lookup_failed, resource, error}}
    end
  end

  defp create_projection(resource, attrs, result) do
    resource
    |> Ash.Changeset.for_create(:create, attrs)
    |> Ash.create(domain: @domain)
    |> case do
      {:ok, _record} -> {:ok, result}
      {:error, error} -> {:error, {:projection_create_failed, resource, error}}
    end
  end

  defp verify_projection(existing, attrs, verified_fields, result) do
    mismatches =
      verified_fields
      |> Enum.filter(fn field -> Map.get(existing, field) != Map.fetch!(attrs, field) end)
      |> Map.new(fn field ->
        {field, %{expected: Map.fetch!(attrs, field), actual: Map.get(existing, field)}}
      end)

    if map_size(mismatches) == 0 do
      {:ok, result}
    else
      {:error, {:refused, "REFUSED_PROJECTION_REPLAY_MISMATCH", mismatches}}
    end
  end
end

defmodule Pm4pyPaaS.Worker do
  @operations ~w(read_xes_summary discover_dfg)
  @run_id ~r/\A[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}\z/

  def admit(%{run_id: run_id, input_path: input_path, operation: operation}) do
    cond do
      operation not in @operations -> {:error, {:refused, "REFUSED_UNSUPPORTED_OPERATION", operation}}
      not is_binary(input_path) or input_path == "" -> {:error, {:refused, "REFUSED_INVALID_INPUT_PATH", input_path}}
      not is_binary(run_id) or not Regex.match?(@run_id, run_id) -> {:error, {:refused, "REFUSED_INVALID_RUN_ID", run_id}}
      true -> {:ok, %{run_id: run_id, input_path: input_path, operation: operation}}
    end
  end

  def execute(request) do
    payload = request |> Jason.encode!() |> Base.url_encode64(padding: false)
    python = System.get_env("PM4PY_PYTHON", "python3")
    worker = :pm4py_paas |> :code.priv_dir() |> to_string() |> Path.join("pm4py_worker.py")
    timeout = String.to_integer(System.get_env("PM4PY_WORKER_TIMEOUT_MS", "120000"))

    task =
      Task.async(fn ->
        System.cmd(python, [worker, "--request-base64", payload],
          env: [
            {"PM4PY_DATA_ROOT", System.get_env("PM4PY_DATA_ROOT", "/app/data")},
            {"PM4PY_SOURCE_SHA", System.get_env("PM4PY_SOURCE_SHA", "UNKNOWN")}
          ],
          stderr_to_stdout: true
        )
      end)

    case Task.yield(task, timeout) || Task.shutdown(task, :brutal_kill) do
      {:ok, {output, 0}} -> Jason.decode(output)
      {:ok, {output, status}} -> decode_worker_error(output, status)
      nil -> {:error, {:refused, "REFUSED_WORKER_TIMEOUT", timeout}}
    end
  end

  defp decode_worker_error(output, status) do
    case Jason.decode(output) do
      {:ok, %{"code" => code} = error} -> {:error, {:refused, code, Map.get(error, "detail"), status}}
      _ -> {:error, {:worker_exit, status, output}}
    end
  end
end
