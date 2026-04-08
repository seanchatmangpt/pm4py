"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""


# list of properties that can be associated to a Petri net or its entities


# distinguish Petri nets that are synchronous product nets
IS_SYNC_NET = "is_sync_net"
TRACE_NET_TRANS_INDEX = "trace_net_trans_index"
TRACE_NET_PLACE_INDEX = "trace_net_place_index"

ARCTYPE = "arctype"
INHIBITOR_ARC = "inhibitor"
RESET_ARC = "reset"
STOCHASTIC_ARC = "stochastic_arc"

TRANS_GUARD = "guard"
WRITE_VARIABLE = "writeVariable"
READ_VARIABLE = "readVariable"
VARIABLES = "variables"
