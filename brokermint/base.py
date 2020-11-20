from typing import Union, List
import os
import requests


class Client:

    BASE_URL = "https://my.brokermint.com/api"

    METHOD_MAPPING = {
        "list": "GET",
        "retrieve": "GET",
        "create": "POST",
        "update": "PUT",
        "destroy": "DELETE",
    }

    ENDPOINTS = {
        "users": {
            "list": "/v1/users",
            "retrieve": "/v1/users/{user_id}",
            "update": "/v1/users/{user_id}",
            "create": "/v1/users",
        },
        "user_commission_plans": {
            "list": "/v1/users/{user_id}/commision_plans",
            "create": "/v1/users/{user_id}/commission_plans",
            "delete": "/v1/users/{user_id}/commission_plans/{plan_id}",
        },
        "contacts": {
            "list": "/v1/contacts",
            "create": "/v1/contacts",
            "retrieve": "/v1/contacts/{contact_id}",
            "update": "/v1/contacts/{contact_id}",
            "destroy": "/v1/contacts/{contact_id}",
        },
        "commission_plans": {
            "list": "/v1/commission_plans",
        },
        "transactions": {
            "list": "/v2/transactions",
            "create": "/v2/transactions",
            "retrieve": "/v2/transactions/{transaction_id}",
            "update": "/v2/transactions/{transaction_id}",
            "destroy": "/v2/transactions/{transaction_id}",
        },
        "transaction_participants": {
            "all": {
                "list": "/v1/transactions/{transaction_id}/participants",
            },
            "users": {
                "list": "/v1/transactions/{transaction_id}/participants/users",
                "create": "/v1/transactions/{transaction_id}/participants/users",
                "retrieve": "/v1/transactions/{transaction_id}/participants/users/{user_id}",
                "update": "/v1/transactions/{transaction_id}/participants/users/{user_id}",
                "destroy": "/v1/transactions/{transaction_id}/participants/users/{user_id}",
            },
            "contacts": {
                "list": "/v1/transactions/{transaction_id}/participants/contacts",
                "create": "/v1/transactions/{transaction_id}/participants/contacts",
                "retrieve": "/v1/transactions/{transaction_id}/participants/contacts/{contact_id}",
                "update": "/v1/transactions/{transaction_id}/participants/contacts/{contact_id}",
                "destroy": "/v1/transactions/{transaction_id}/participants/contacts/{contact_id}",
            },
        },
        "transaction_commissions": {
            "list": "/v1/transactions/{transaction_id}/commissions",
        },
        "transaction_checklists": {
            "list": "/v1/transactions/{transaction_id}/checklists",
            "retrieve": "/v1/transactions/{transaction_id}/checklists/{checklist_id}",
        },
        "transaction_tasks": {
            "tasks": {
                "list": "/v1/transactions/{transaction_id}/checklists/{checklist_id}/tasks",
                "create": "/v1/transactions/{transaction_id}/checklists/{checklist_id}/tasks",
                "retrieve": "/v1/transactions/{transaction_id}/checklists/{checklist_id}/tasks/{task_id}",
                "update": "/v1/transactions/{transaction_id}/checklists/{checklist_id}/tasks/{task_id}",
            },
            "document": {
                "create": "/v1/transactions/{transaction_id}/checklists/{checklist_id}/tasks/{task_id}/submit_document",
            },
            "comment": {
                "create": "/v1/transactions/{transaction_id}/checklists/{checklist_id}/tasks/{task_id}/add_comment",
            },
        },
        "transaction_documents": {
            "create": "/v1/transactions/{transaction_id}/documents",
            "retrieve": "/v1/transactions/{transaction_id}/documents/{document_id}",
        },
        "transaction_notes": {
            "create": "/v1/transactions/{transaction_id}/notes",
        },
        "transaction_backups": {
            "all": {
                "list": "/v1/transactions/{transaction_id}/backups",
            },
            "latest": {
                "retrieve": "/v1/transactions/{transaction_id}/backup",
            },
        },
        "transaction_offers": {
            "all": {
                "list": "/v1/transactions/{transaction_id}/offers",
                "retrieve": "/v1/transactions/{transaction_id}/offers/{offer_id}",
            },
            "attachment": {
                "retrieve": "/v1/transactions/{transaction_id}/offers/{offer_id}/attachments/{attachment_id}",
            },
        },
        "incoming_transactions": {
            "create": "/v1/incoming_transactions",
        },
        "reports": {
            "all": {
                "list": "/v2/reports",
            },
            "filters": {
                "list": "/v2/reports/{report_id}/filters",
            },
            "data": {
                "retrieve": "/v2/reports/{report_id}",
            },
        },
    }

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("BM_API_KEY")

    def _get_data(
        self,
        key: str,
        method: str,
        *,
        within: str = None,
        uri_params: dict = None,
        params: dict = None,
        data: dict = None,
        files: dict = None,
    ):
        url = self._construct_url(key, method, within, uri_params)
        params = self._construct_params(params)
        response = self._make_request(url, method, params, data, files)
        try:
            return response.json()
        except ValueError:
            return {"error": response.text}

    def _construct_url(self, key: str, method: str, within: str, uri_params: dict):
        endpoint = (
            self.ENDPOINTS[key][within][method]
            if within
            else self.ENDPOINTS[key][method]
        )
        if uri_params:
            endpoint = endpoint.format(**uri_params)
        return f"{self.BASE_URL}{endpoint}"

    def _construct_params(self, params: dict):
        try:
            new_params = {k: v for k, v in params.items() if v is not None}
        except AttributeError:

            # No parameters given
            new_params = {}
        new_params["api_key"] = self.api_key
        return new_params

    def _make_request(
        self,
        url: str,
        method: str,
        params: dict,
        data: dict,
        files: dict,
    ):
        response = requests.request(
            self.METHOD_MAPPING[method], url, params=params, json=data, files=files
        )
        return response

    def list_users(
        self,
        *,
        count: int = None,
        starting_from_id: int = None,
        active: int = None,
        created_since: Union[str, int] = None,
        updated_since: Union[str, int] = None,
        external_ids: str = None,
        emails: str = None,
        full_info: int = None,
    ):
        params = {
            "count": count,
            "starting_from_id": starting_from_id,
            "active": active,
            "created_since": created_since,
            "updated_since": updated_since,
            "external_ids": external_ids,
            "emails": emails,
            "full_info": full_info,
        }
        return self._get_data("users", "list", params=params)

    def create_user(self, data: dict, *, send_instructions: int = None):
        return self._get_data(
            "users",
            "create",
            data=data,
            params={"send_instructions": send_instructions},
            required_fields=["email", "first_name", "last_name"],
        )

    def get_user(self, user_id: int):
        return self._get_data("users", "retrieve", uri_params={"user_id": user_id})

    def update_user(self, user_id: int, data: dict):
        # if not all(k in data for k in required_fields):
        #     raise ValueError(
        #         "The data argument is missing one of the required fields:  {', '.join(required_fields)"
        #     )
        return self._get_data(
            "users",
            "update",
            uri_params={"user_id": user_id},
            data=data,
            required_fields=["email", "first_name", "last_name"],
        )

    def list_user_commission_plans(self, user_id: int):
        return self._get_data(
            "user_commission_plans", "list", uri_params={"user_id": user_id}
        )

    def assign_user_commission_plan(self, user_id: int, plan_id: int):
        return self._get_data(
            "user_commission_plans",
            "create",
            uri_params={"user_id": user_id, "plan_id": plan_id},
        )

    def unassign_user_commission_plan(self, user_id: int, plan_id: int):
        return self._get_data(
            "user_commission_plans",
            "destroy",
            uri_params={"user_id": user_id, "plan_id": plan_id},
        )

    def list_contacts(
        self,
        *,
        count: int = None,
        starting_from_id: int = None,
        active: int = None,
        created_since: Union[str, int] = None,
        updated_since: Union[str, int] = None,
        external_ids: str = None,
        emails: str = None,
        full_info: int = None,
    ):
        params = {
            "count": count,
            "starting_from_id": starting_from_id,
            "active": active,
            "created_since": created_since,
            "updated_since": updated_since,
            "external_ids": external_ids,
            "emails": emails,
            "full_info": full_info,
        }
        return self._get_data("contacts", "list", params=params)

    def create_contact(self, data: dict):
        return self._get_data("contacts", "create", data=data)

    def get_contact(self, contact_id: int):
        return self._get_data(
            "contacts", "retrieve", uri_params={"contact_id": contact_id}
        )

    def update_contact(self, contact_id: int, data: dict):
        return self._get_data(
            "contacts",
            "update",
            uri_params={"contact_id": contact_id},
            data=data,
            required_fields=["email"],
        )

    def delete_contact(self, contact_id: int):
        return self._get_data(
            "contacts", "destroy", uri_params={"contact_id": contact_id}
        )

    def list_commission_plans(self):
        return self._get_data("commission_plans", "list")

    def list_transactions(
        self,
        *,
        count: int = None,
        starting_from_id: int = None,
        statuses: Union[str, List[str]] = None,
        created_since: Union[str, int] = None,
        updated_since: Union[str, int] = None,
        closed_since: Union[str, int] = None,
        owned_by: str = None,
        external_ids: str = None,
    ):
        params = {
            "count": count,
            "starting_from_id": starting_from_id,
            "statuses": statuses,
            "created_since": created_since,
            "updated_since": updated_since,
            "closed_since": closed_since,
            "owned_by": owned_by,
            "external_ids": external_ids,
        }
        return self._get_data("transactions", "list", params=params)

    def create_transactions(self, data: dict):
        return self._get_data(
            "transactions",
            "create",
            data=data,
            required_fields=[
                "address",
                "city",
                "state",
                "zip",
                "status",
                "price",
                "listing_side_representer",
                "buying_side_representer",
            ],
        )

    def get_transaction(self, transaction_id: int):
        return self._get_data(
            "transactions", "retrieve", uri_params={"transaction_id": transaction_id}
        )

    def update_transaction(self, transaction_id: int, data: dict):
        return self._get_data(
            "transactions",
            "update",
            uri_params={"transaction_id": transaction_id},
            data=data,
        )

    def delete_transaction(self, transaction_id: int):
        return self._get_data(
            "transactions", "destroy", uri_params={"transaction_id": transaction_id}
        )

    def list_transaction_participants(
        self, transaction_id: int, *, full_info: int = None
    ):
        return self._get_data(
            "transaction_participants",
            "list",
            within="all",
            uri_params={"transaction_id": transaction_id},
            params={"full_info": full_info},
        )

    def list_user_transaction_participants(
        self, transaction_id: int, *, full_info: int = None
    ):
        return self._get_data(
            "transaction_participants",
            "list",
            within="users",
            uri_params={"transaction_id": transaction_id},
            params={"full_info": full_info},
        )

    def create_user_transaction_participants(self, transaction_id: int, data: dict):
        return self._get_data(
            "transaction_participants",
            "create",
            within="users",
            uri_params={"transaction_id": transaction_id},
            data=data,
        )

    def get_user_transaction_participant(
        self, transaction_id: int, user_id: int, *, full_info: int = None
    ):
        return self._get_data(
            "transaction_participants",
            "retrieve",
            within="users",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
            params={"full_info": full_info},
        )

    def update_user_transaction_participant(
        self, transaction_id: int, user_id: int, data: dict
    ):
        return self._get_data(
            "transaction_participants",
            "update",
            within="users",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
            data=data,
        )

    def delete_user_transaction_participant(self, transaction_id: int, user_id: int):
        return self._get_data(
            "transaction_participants",
            "destroy",
            within="users",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
        )

    def list_contact_transaction_participants(
        self, transaction_id: int, *, full_info: int = None
    ):
        return self._get_data(
            "transaction_participants",
            "list",
            within="contacts",
            uri_params={"transaction_id": transaction_id},
            params={"full_info": full_info},
        )

    def create_contact_transaction_participants(self, transaction_id: int, data: dict):
        return self._get_data(
            "transaction_participants",
            "create",
            within="contactts",
            uri_params={"transaction_id": transaction_id},
            data=data,
        )

    def get_contact_transaction_participant(
        self, transaction_id: int, user_id: int, *, full_info: int = None
    ):
        return self._get_data(
            "transaction_participants",
            "retrieve",
            within="contacts",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
            params={"full_info": full_info},
        )

    def update_contact_transaction_participant(
        self, transaction_id: int, user_id: int, data: dict
    ):
        return self._get_data(
            "transaction_participants",
            "update",
            within="contacts",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
            data=data,
        )

    def delete_contact_transaction_participant(self, transaction_id: int, user_id: int):
        return self._get_data(
            "transaction_participants",
            "destroy",
            within="contacts",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
        )

    def list_transaction_commissions(self, transaction_id: int):
        return self._get_data(
            "transaction_commissions",
            "list",
            uri_params={"transaction_id": transaction_id},
        )

    def list_transaction_checklists(self, transaction_id: int):
        return self._get_data(
            "transaction_checklists",
            "list",
            uri_params={"transaction_id": transaction_id},
        )

    def get_transaction_checklists(self, transaction_id: int, checklist_id: int):
        return self._get_data(
            "transaction_checklists",
            "retrieve",
            uri_params={"transaction_id": transaction_id, "checklist_id": checklist_id},
        )

    def list_transaction_tasks(self, transaction_id: int, checklist_id: int):
        return self._get_data(
            "transaction_tasks",
            "list",
            within="tasks",
            uri_params={"transaction_id": transaction_id, "checklist_id": checklist_id},
        )

    def create_transaction_task(
        self, transaction_id: int, checklist_id: int, data: dict
    ):
        return self._get_data(
            "transaction_tasks",
            "create",
            within="tasks",
            uri_params={"transaction_id": transaction_id, "checklist_id": checklist_id},
            data=data,
            required_fields=["name"],
        )

    def get_transaction_task(
        self, transaction_id: int, checklist_id: int, task_id: int
    ):
        return self._get_data(
            "transaction_tasks",
            "retrieve",
            within="tasks",
            uri_params={
                "transaction_id": transaction_id,
                "checklist_id": checklist_id,
                "task_id": task_id,
            },
        )

    def update_transaction_task(
        self, transaction_id: int, checklist_id: int, task_id: int, data: dict
    ):
        return self._get_data(
            "transaction_tasks",
            "update",
            within="tasks",
            uri_params={
                "transaction_id": transaction_id,
                "checklist_id": checklist_id,
                "task_id": task_id,
            },
            data=data,
            required_fields=["name"],
        )

    def submit_transaction_task_document(
        self, transaction_id: int, checklist_id: int, task_id: int, files: dict
    ):
        return self._get_data(
            "transaction_tasks",
            "create",
            within="document",
            uri_params={
                "transaction_id": transaction_id,
                "checklist_id": checklist_id,
                "task_id": task_id,
            },
            files=files,
        )

    def create_transaction_task_comment(
        self, transaction_id: int, checklist_id: int, task_id: int, data: dict
    ):
        return self._get_data(
            "transaction_tasks",
            "create",
            within="comment",
            uri_params={
                "transaction_id": transaction_id,
                "checklist_id": checklist_id,
                "task_id": task_id,
            },
            data=data,
        )

    def create_transaction_document(self, transaction_id: int, data: dict):
        return self._get_data(
            "transaction_documents",
            "create",
            uri_params={
                "transaction_id": transaction_id,
            },
            data=data,
        )

    def get_transaction_document(
        self, transaction_id: int, document_id: int, task_id: int
    ):
        return self._get_data(
            "transaction_documents",
            "retrieve",
            uri_params={
                "transaction_id": transaction_id,
                "document_id": document_id,
            },
        )

    def create_transaction_note(self, transaction_id: int, data: dict):
        return self._get_data(
            "transaction_notes",
            "create",
            uri_params={
                "transaction_id": transaction_id,
            },
            data=data,
            required_fields=["text"],
        )

    def list_transaction_backups(self, transaction_id: int):
        return self._get_data(
            "transaction_backups",
            "list",
            within="all",
            uri_params={"transaction_id": transaction_id},
        )

    def get_latest_transaction_backup(self, transaction_id: int):
        return self._get_data(
            "transaction_backups",
            "retrieve",
            within="latest",
            uri_params={"transaction_id": transaction_id},
        )

    def list_transaction_offers(self, transaction_id: int):
        return self._get_data(
            "transaction_offers",
            "list",
            within="all",
            uri_params={"transaction_id": transaction_id},
        )

    def get_transaction_offer(self, transaction_id: int, offer_id: int):
        return self._get_data(
            "transaction_offers",
            "retrieve",
            within="all",
            uri_params={"transaction_id": transaction_id, "offer_id": offer_id},
        )

    def get_transaction_offer_attachment(
        self, transaction_id: int, offer_id: int, attachment_id: int
    ):
        return self._get_data(
            "transaction_offers",
            "retrieve",
            within="attachment",
            uri_params={
                "transaction_id": transaction_id,
                "offer_id": offer_id,
                "attachment_id": attachment_id,
            },
        )

    def create_incoming_transaction(self, data: dict):
        return self._get_data(
            "incoming_transactions",
            "create",
            data=data,
            required_fields=["source_id", "transactions"],
        )

    def list_reports(self):
        return self._get_data(
            "reports",
            "list",
            within="all",
        )

    def list_report_filters(self):
        return self._get_data(
            "reports",
            "list",
            within="filters",
        )

    def get_report_data(self, report_id: int):
        return self._get_data(
            "reports",
            "retrieve",
            within="data",
            uri_params={
                "report_id": report_id,
            },
        )
