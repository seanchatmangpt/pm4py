defmodule Pm4pyPaaS.Domain do
  use Ash.Domain, validate_config_inclusion?: false

  resources do
    resource Pm4pyPaaS.DataService
    resource Pm4pyPaaS.MiningRun
    resource Pm4pyPaaS.Receipt
  end
end

defmodule Pm4pyPaaS.DataService do
  use Ash.Resource,
    domain: Pm4pyPaaS.Domain,
    data_layer: Ash.DataLayer.Ets,
    extensions: [AshR2RML.Resource]

  r2rml do
    table_name("pm4py_data_services")
    class("http://www.w3.org/ns/dcat#DataService")

    subject do
      template("urn:pm4py-paas:service:{id}")
    end

    property(:title, "http://purl.org/dc/terms/title")
    property(:endpoint, "http://www.w3.org/ns/dcat#endpointURL")
  end

  actions do
    defaults [:read]

    action :execute, :map do
      argument :run_id, :string, allow_nil?: false
      argument :input_path, :string, allow_nil?: false
      argument :operation, :string, allow_nil?: false

      run fn input, _context ->
        Reactor.run(Pm4pyPaaS.RunMining, input.arguments, %{}, async?: false)
      end
    end
  end

  attributes do
    uuid_primary_key :id
    attribute :title, :string, public?: true
    attribute :endpoint, :string, public?: true
  end
end

defmodule Pm4pyPaaS.MiningRun do
  use Ash.Resource,
    domain: Pm4pyPaaS.Domain,
    data_layer: Ash.DataLayer.Ets,
    extensions: [AshR2RML.Resource]

  r2rml do
    table_name("pm4py_mining_runs")
    class("http://www.w3.org/ns/prov#Activity")

    subject do
      template("urn:pm4py-paas:run:{id}")
    end

    property(:id, "http://purl.org/dc/terms/identifier")
    property(:operation, "http://purl.org/dc/terms/type")
    property(:input_sha256, "http://www.w3.org/ns/prov#value")
    property(:standing, "http://purl.org/dc/terms/type")
  end

  actions do
    defaults [:read, create: :*]
  end

  attributes do
    attribute :id, :string, primary_key?: true, allow_nil?: false, public?: true
    attribute :operation, :string, allow_nil?: false, public?: true
    attribute :input_sha256, :string, allow_nil?: false, public?: true
    attribute :standing, :string, allow_nil?: false, public?: true
  end
end

defmodule Pm4pyPaaS.Receipt do
  use Ash.Resource,
    domain: Pm4pyPaaS.Domain,
    data_layer: Ash.DataLayer.Ets,
    extensions: [AshR2RML.Resource]

  r2rml do
    table_name("pm4py_receipts")
    class("http://www.w3.org/ns/prov#Bundle")

    subject do
      template("urn:pm4py-paas:receipt:{id}")
    end

    property(:id, "http://purl.org/dc/terms/identifier")
    property(:result_sha256, "http://www.w3.org/ns/prov#value")
    property(:source_sha, "http://purl.org/dc/terms/source")
  end

  actions do
    defaults [:read, create: :*]
  end

  attributes do
    attribute :id, :string, primary_key?: true, allow_nil?: false, public?: true
    attribute :result_sha256, :string, allow_nil?: false, public?: true
    attribute :source_sha, :string, public?: true
  end
end
