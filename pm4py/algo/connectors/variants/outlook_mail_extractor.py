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



from typing import Optional, Dict
from pm4py.algo.connectors.util import mail as mail_utils
from pm4py.util import pandas_utils
import pandas as pd
from datetime import datetime
from pm4py.util.dt_parsing.variants import strpfromiso
from typing import List, Any
import importlib.util
import traceback


correspondence = {
    # mail & posts
    "43": "Mail",
    "45": "Post",
    "46": "Delivery Report",
    "47": "Remote",

    # meetings
    "53": "Meeting Request",
    "54": "Meeting Cancellation",
    "55": "Meeting Declination",
    "56": "Meeting Acceptance",
    "57": "Meeting Tentatively Accepted",
    "181": "Meeting Forward Notification",

    # tasks
    "48": "Task",
    "49": "Task Request",
    "50": "Task Request Update",
    "51": "Task Request Acceptance",
    "52": "Task Request Declination",

    # appointments & miscellany
    "26": "Appointment",
    "40": "Contact",
    "41": "Document",
    "42": "Journal",
    "44": "Note",
    "69": "Distribution List",
    "104": "Sharing",
    "113": "Storage",
}


def get_events(box, prefix, progress) -> List[Dict[str, Any]]:
    """
    Utility method extracting the items of a given mailbox.

    Parameters
    --------------
    box
        Mailbox
    prefix
        Prefix for the activities (Sent / Received )

    Returns
    --------------
    list_events
        List of events (dictionaries)
    """
    events = []
    for it in box.Items:
        cla = " "
        try:
            cla = str(it.Class)
            if cla in correspondence:
                cla = prefix + correspondence[cla]
                subject = str(it.Subject)
                timestamp = strpfromiso.fix_naivety(
                    datetime.fromtimestamp(it.CreationTime.timestamp())
                )
                sender = "EMPTY"
                try:
                    sender = str(it.Sender.Name)
                except BaseException:
                    pass
                recipients = "EMPTY"
                try:
                    recipients = " AND ".join(
                        [str(x.Name) for x in it.Recipients]
                    )
                except BaseException:
                    pass
                conversationid = str(it.ConversationID)
                conversationtopic = str(it.ConversationTopic)
                events.append(
                    {
                        "case:concept:name": conversationid,
                        "concept:name": cla,
                        "time:timestamp": timestamp,
                        "org:resource": sender,
                        "recipients": recipients,
                        "topic": conversationtopic,
                        "subject": subject,
                    }
                )
        except BaseException:
            traceback.print_exc()
            pass
        if progress is not None:
            progress.update()
    return events


def apply(parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Extracts the history of the conversations from the local instance of Microsoft Outlook
    running on the current computer.

    CASE ID (case:concept:name) => identifier of the conversation
    ACTIVITY (concept:name) => activity that is performed in the current item (send e-mail, receive e-mail, refuse meeting ...)
    TIMESTAMP (time:timestamp) => timestamp of creation of the item in Outlook
    RESOURCE (org:resource) => sender of the current item

    Returns
    ---------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    inbox = mail_utils.connect(None, 6)
    outbox = mail_utils.connect(None, 5)

    progress = None
    if importlib.util.find_spec("tqdm"):
        from tqdm.auto import tqdm

        progress = tqdm(
            total=len(outbox.Items) + len(inbox.Items),
            desc="extracting mailbox items, progress :: ",
        )

    events = get_events(outbox, "Sent ", progress)
    events = events + get_events(inbox, "Received ", progress)

    if progress is not None:
        progress.close()

    dataframe = pandas_utils.instantiate_dataframe(events)
    dataframe = pandas_utils.insert_index(
        dataframe, "@@index", copy_dataframe=False, reset_index=False
    )
    dataframe = dataframe.sort_values(["time:timestamp", "@@index"])
    dataframe["@@case_index"] = dataframe.groupby(
        "case:concept:name", sort=False
    ).ngroup()
    dataframe = dataframe.sort_values(
        ["@@case_index", "time:timestamp", "@@index"]
    )

    return dataframe
