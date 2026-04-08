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



from typing import Optional


def connect(email_user: Optional[str], mailbox_id: int):
    """
    Returns a mailbox object from the local Outlook instance.

    Parameters
    -------------
    email_user
        E-mail address to use
    mailbox_id
        ID of the mailbox to use:
        * 5 = outbox
        * 6 = inbox
        * 9 = calendar

    Returns
    -------------
    mailbox_obj
        Mailbox object
    """
    import pythoncom

    pythoncom.CoInitialize()

    import win32com.client

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace(
        "MAPI"
    )
    mailbox_id = int(mailbox_id)

    if email_user is not None:
        recipient = outlook.CreateRecipient(email_user)
        recipient.Resolve()
        return outlook.GetSharedDefaultFolder(recipient, mailbox_id)

    return outlook.GetDefaultFolder(mailbox_id)
