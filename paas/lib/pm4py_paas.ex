defmodule Pm4pyPaaS.Application do
  use Application

  @impl true
  def start(_type, _args) do
    port = String.to_integer(System.get_env("PORT", "8000"))

    children = [
      {Bandit, plug: Pm4pyPaaS.Router, scheme: :http, port: port}
    ]

    Supervisor.start_link(children, strategy: :one_for_one, name: Pm4pyPaaS.Supervisor)
  end
end

defmodule Pm4pyPaaS.Router do
  use Plug.Router

  plug Plug.RequestId
  plug :match
  plug Plug.Parsers, parsers: [:json], pass: ["application/json", "application/vnd.api+json"], json_decoder: Jason
  plug :dispatch

  get "/health" do
    json(conn, 200, %{
      status: "ok",
      service: "pm4py-paas",
      standing: "PARTIAL_ALIVE",
      authority: "BRCE"
    })
  end

  post "/v1/runs" do
    with :ok <- authorize(conn),
         {:ok, params} <- admit_body(conn.body_params),
         input <- Ash.ActionInput.for_action(Pm4pyPaaS.DataService, :execute, params),
         {:ok, result} <- Ash.run_action(input, domain: Pm4pyPaaS.Domain) do
      json(conn, 200, result)
    else
      {:error, :unauthorized} -> json(conn, 401, refusal("REFUSED_NO_AUTHORITY", "Bearer authority is missing or invalid"))
      {:error, {:bad_request, detail}} -> json(conn, 400, refusal("REFUSED_INVALID_INTENT", detail))
      {:error, %Ash.Error{} = error} -> json(conn, 422, refusal("REFUSED_ASH_ACTION", Exception.message(error)))
      {:error, reason} -> json(conn, 502, refusal("REFUSED_EXECUTION", inspect(reason)))
    end
  end

  match _ do
    json(conn, 404, refusal("REFUSED_ROUTE_NOT_FOUND", "No admitted route matches this request"))
  end

  defp authorize(conn) do
    expected = System.get_env("PM4PY_PAAS_TOKEN")

    supplied =
      conn
      |> get_req_header("authorization")
      |> List.first()

    cond do
      is_nil(expected) or expected == "" -> {:error, :unauthorized}
      supplied == "Bearer " <> expected -> :ok
      true -> {:error, :unauthorized}
    end
  end

  defp admit_body(%{"input_path" => input_path, "operation" => operation} = body)
       when is_binary(input_path) and is_binary(operation) do
    {:ok,
     %{
       input_path: input_path,
       operation: operation,
       run_id: Map.get(body, "run_id", Ash.UUID.generate())
     }}
  end

  defp admit_body(_), do: {:error, {:bad_request, "input_path and operation are required strings"}}

  defp refusal(code, detail), do: %{status: "REFUSED", code: code, detail: detail}

  defp json(conn, status, payload) do
    conn
    |> put_resp_content_type("application/json")
    |> send_resp(status, Jason.encode!(payload))
  end
end
