
import datetime

from dateutil.tz import tzutc

from pm4py.objects.log import obj

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"


def generate_pm4py_log(trace_frequencies):
    log = obj.EventLog()
    trace_count = 0
    for variant in trace_frequencies.items():
        frequency = variant[1]
        activities = variant[0].split(EVENT_DELIMETER)
        for i in range(0, frequency):
            trace = obj.Trace()
            trace.attributes["concept:name"] = trace_count
            trace_count = trace_count + 1
            for activity in activities:
                if TRACE_END not in activity:
                    event = obj.Event()
                    event["concept:name"] = str(activity)
                    event["time:timestamp"] = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=tzutc())
                    trace.append(event)
            log.append(trace)
    return log
