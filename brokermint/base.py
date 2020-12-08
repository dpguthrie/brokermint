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
        "sso": {"retrieve": "/v1/users/{user_id}/sso_token"},
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
        required_fields: List[str] = None,
    ):
        """Entrypoint to getting data from Brokermint API

        Parameters
        ----------
        key: str, required
            Dictionary key in self.ENDPOINTS dictionary
        method: str, required
            Type of request to perform
        within: str, optional
            Grouped endpoints can have sub-groups that further define how URL is
            structured.  This is a key that will match that sub-group.
        uri_params: dict, optional
            Parameters injected into the URL
        data: dict, optional
            Dictionary used to create / update data
        files: dict, optional
            Dictionary used to upload files
        required_fields: list, optional
            Fields required when creating or updating data
        """
        url = self._construct_url(key, method, within, uri_params)
        params = self._construct_params(params)
        response = self._make_request(url, method, params, data, files, required_fields)
        try:
            return response.json()
        except ValueError:
            return {"error": response.text}

    def _construct_url(self, key: str, method: str, within: str, uri_params: dict):
        """Construct the URL used in the request

        Parameters
        ----------
        key: str, required
            Dictionary key in self.ENDPOINTS dictionary
        method: str, required
            Type of request to perform
        within: str, optional
            Grouped endpoints can have sub-groups that further define how URL is
            structured.  This is a key that will match that sub-group.
        uri_params: dict, optional
            Parameters injected into the URL
        """
        endpoint = (
            self.ENDPOINTS[key][within][method]
            if within
            else self.ENDPOINTS[key][method]
        )
        if uri_params:
            endpoint = endpoint.format(**uri_params)
        return f"{self.BASE_URL}{endpoint}"

    def _construct_params(self, params: dict):
        """Construct the query parameters used in the request

        Parameters
        ----------
        params: dict, required
            Dictionary containing query parameters used to filter data
        """
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
        required_fields: List[str],
    ):
        """Request data from the API

        Parameters
        ----------
        url: str, required
            Fully constructed URL
        method: str, required
            Type of request to perform
        params: dict, required
            Dictionary containing query parameters used to filter data
        data: dict, optional
            Dictionary used to create / update data
        files: dict, optional
            Dictionary used to upload files
        required_fields: list, optional
            Fields required when creating or updating data
        """
        if required_fields is not None and data is not None:
            if not all(k in data for k in required_fields):
                raise ValueError(
                    f"The data argument is missing one of the required fields:  {', '.join(required_fields)}"
                )
        response = requests.request(
            self.METHOD_MAPPING[method],
            url,
            params=params,
            json=data,
            files=files,
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
        """List of available users in account

        Parameters
        ----------
        count: int, default 1000, optional
            Specifies the number of items to retrieve
        starting_from_id: int, optional
            Specifies the ID of entity to retrieve records starting from
        active: int, optional
            Filter active/inactive users.  By default all users are returned.  Use
            1 to query active users only or 0 to query inactive.
        created_since: str or int, optional
            Filter users created since specified date.  Date format:  YYYY-MM-DD or
            13-digit unix timestamp
        updated_since: str or int, optional
            Filter users updated since specified date.  Date format:  YYYY-MM-DD or
            13-digit unix timestamp
        external_ids: str, optional
            Filter users by the comma separated list of external IDs
        emails: str, optional
            Filter users by the comma separated list of emails
        full_info: int, default 0, optional
            Specifies whether to retrieve short or full user information.
        """
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
        """Create User

        Parameters
        ----------
        data: dict, required
            Data used to create the user.  Fields available are:
                email: str, required
                first_name: str, required
                last_name: str, required
                company: str, optional
                role: str, optional
                team: str, optional
                external_id: str, optional
                    External identifier passed during user creation, this value is
                    available through users API only, users can be filtered by this
                    field to see whether such user already exists
                birthday: int, optional
                    13-digit unix timestamp
                anniversary_date: str
                phone: str
        send_instructions: int, default 0, optional
            Specifies whether to send welcome email and login instructions
        """
        return self._get_data(
            "users",
            "create",
            data=data,
            params={"send_instructions": send_instructions},
            required_fields=["email", "first_name", "last_name"],
        )

    def get_user(self, user_id: int):
        """Get User

        Parameters
        ----------
        user_id: int, required
            ID of User
        """
        return self._get_data("users", "retrieve", uri_params={"user_id": user_id})

    def update_user(self, user_id: int, data: dict):
        """Update User

        Parameters
        ----------
        user_id: int, required
            ID of User
        data: dict, required
            Data used to create the user.  Fields available are:
                email: str, required
                first_name: str, required
                last_name: str, required
                company: str, optional
                role: str, optional
                team: str, optional
                external_id: str, optional
                    External identifier passed during user creation, this value is
                    available through users API only, users can be filtered by this
                    field to see whether such user already exists
                birthday: int, optional
                    13-digit unix timestamp
                anniversary_date: str
                phone: str
        """
        return self._get_data(
            "users",
            "update",
            uri_params={"user_id": user_id},
            data=data,
            required_fields=["email", "first_name", "last_name"],
        )

    def list_user_commission_plans(self, user_id: int):
        """List commision plans assigned to user

        Parameters
        ----------
        user_id: int, required
            ID of User
        """
        return self._get_data(
            "user_commission_plans", "list", uri_params={"user_id": user_id}
        )

    def assign_user_commission_plan(self, user_id: int, plan_id: int):
        """Assign commision plan to user

        Parameters
        ----------
        user_id: int, required
            ID of User
        plan_id: int, required
            ID of commission plan
        """
        return self._get_data(
            "user_commission_plans",
            "create",
            uri_params={"user_id": user_id, "plan_id": plan_id},
        )

    def unassign_user_commission_plan(self, user_id: int, plan_id: int):
        """Unassign commision plan from user

        Parameters
        ----------
        user_id: int, required
            ID of User
        plan_id: int, required
            ID of commission plan
        """
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
        """List of available contacts in account

        Parameters
        ----------
        count: int, default 1000, optional
            Specifies the number of items to retrieve
        starting_from_id: int, optional
            Specifies the ID of entity to retrieve records starting from
        created_since: str or int, optional
            Filter contacts created since specified date.  Date format:  YYYY-MM-DD or
            13-digit unix timestamp
        updated_since: str or int, optional
            Filter contacts updated since specified date.  Date format:  YYYY-MM-DD or
            13-digit unix timestamp
        external_ids: str, optional
            Filter contacts by the comma separated list of external IDs
        emails: str, optional
            Filter contacts by the comma separated list of emails
        full_info: int, default 0, optional
            Specifies whether to retrieve short or full contact information.
        """
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
        """Create Contact

        Parameters
        ----------
        data: dict, required
            Data used to create the contact.  Fields available are:
                email: str, required
                first_name: str, optional
                last_name: str, optional
                contact_type: str
                    Contact's role, like Escrow Officer, Selling Agent, etc.
                external_id: str, optional
                    External identifier passed during contact creation, this value is
                    available through contacts API only, contacts can be filtered by this
                    field to see whether such contact already exists
                company: str, optional
                address: str, optional
                city: str, optional
                state: str, optional
                zip: str, optional
                phone: str, optional
                mobile_phone: str, optional
                fax: str, optional
                private: bool, optional
                lead_source: str, optional
                custom_attributes: List[dict], optional
                    name: str
                    label: str
                    type: str, [text, date, dropdown, money]
                    options: str
                    value: str
        """
        return self._get_data(
            "contacts", "create", data=data, required_fields=["email"]
        )

    def get_contact(self, contact_id: int):
        """Get Contact

        Parameters
        ----------
        contact_id: int, required
            ID of contact
        """
        return self._get_data(
            "contacts", "retrieve", uri_params={"contact_id": contact_id}
        )

    def update_contact(self, contact_id: int, data: dict):
        """Update Contact

        Parameters
        ----------
        contact_id: int, required
            ID of contact
        data: dict, required
            Data used to update the contact.  Fields available are:
                email: str, required
                first_name: str, optional
                last_name: str, optional
                contact_type: str
                    Contact's role, like Escrow Officer, Selling Agent, etc.
                external_id: str, optional
                    External identifier passed during contact creation, this value is
                    available through contacts API only, contacts can be filtered by this
                    field to see whether such contact already exists
                company: str, optional
                address: str, optional
                city: str, optional
                state: str, optional
                zip: str, optional
                phone: str, optional
                mobile_phone: str, optional
                fax: str, optional
                private: bool, optional
                lead_source: str, optional
                custom_attributes: List[dict], optional
                    name: str
                    label: str
                    type: str, [text, date, dropdown, money]
                    options: str
                    value: str
        """
        return self._get_data(
            "contacts",
            "update",
            uri_params={"contact_id": contact_id},
            data=data,
            required_fields=["email"],
        )

    def delete_contact(self, contact_id: int):
        """Delete Contact

        Parameters
        ----------
        contact_id: int, required
            ID of contact
        """
        return self._get_data(
            "contacts", "destroy", uri_params={"contact_id": contact_id}
        )

    def list_commission_plans(self):
        """List of available Commission Plans"""
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
        """List of available transactions

        Parameters
        ----------
        count: int, default 1000, optional
            Specifies the number of items to retrieve
        starting_from_id: int, optional
            Specifies the ID of entity to retrieve records starting from
        statuses: str, optional
            Filter transactions by specified statuses.  Allowed values: listing, pending,
            closed, and cancelled.  Multiple statuses can be used as a comma-separated
            string
        created_since: str or int, optional
            Filter transactions created since specified date.  Date format:  YYYY-MM-DD or
            13-digit unix timestamp
        updated_since: str or int, optional
            Filter transactions updated since specified date.  Date format:  YYYY-MM-DD or
            13-digit unix timestamp
        closed_since: str or int, optional
            Filter transactions closed since specified date.  Date format:  YYYY-MM-DD or
            13-digit unix timestamp
        owned_by: str, optional
            Filter transactions by owner - owner format TYPE-ID, i.g. "User-230" or
            "Contact-1245"
        external_ids: str, optional
            Filter transactions by the comma separated list of external IDs
        """
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
        """Create Transaction

        Parameters
        ----------
        data: dict, required
            Data used to create the transaction.  Fields available are:
                external_id: str, optional
                address: str, required
                city: str, required
                state: str, required
                zip: str, required
                status: str, required
                    One of listing, pending, closed, or cancelled
                transaction_type: str, optional
                price: number, required
                acceptance_date: int, optional
                    13-digit unix timestamp
                expiration_date: int, optional
                    13-digit unix timestamp
                closing_date: int, optional
                    13-digit unix timestamp
                listing_date: int, optional
                    13-digit unix timestamp
                timezone: int, optional
                    Transaction timezone in hours from UTC
                listing_side_representer: object, required
                    id: int
                    type: str (Account, Contact)
                buying_side_representer: object, required
                    id: int
                    type: str (Account, Contact)
                custom_attributes: List[dict], optional
                    name: str
                    label: str
                    type: str, [text, date, dropdown, money]
                    value: str
                    required: bool
                    requried_if_status: str, [listing, pending, closed, cancelled]
                    options: str
        """
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
        """Get Transaction

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        """
        return self._get_data(
            "transactions", "retrieve", uri_params={"transaction_id": transaction_id}
        )

    def update_transaction(self, transaction_id: int, data: dict):
        """Update Transaction

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        """
        return self._get_data(
            "transactions",
            "update",
            uri_params={"transaction_id": transaction_id},
            data=data,
        )

    def delete_transaction(self, transaction_id: int):
        """Delete Transaction

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        """
        return self._get_data(
            "transactions", "destroy", uri_params={"transaction_id": transaction_id}
        )

    def list_transaction_participants(
        self, transaction_id: int, *, full_info: int = None
    ):
        """List of transaction participants

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        full_info: int, default 0, optional
            Specifies whether to retrieve short or full user / contact information.
        """
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
        """List of user transaction participants

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        full_info: int, default 0, optional
            Specifies whether to retrieve short or full user information.
        """
        return self._get_data(
            "transaction_participants",
            "list",
            within="users",
            uri_params={"transaction_id": transaction_id},
            params={"full_info": full_info},
        )

    def create_user_transaction_participants(self, transaction_id: int, data: dict):
        """Add or update user participation

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        data: dict, required
            Data used to create a user participant.  Fields available are:
                id: int, required
                    User ID
                preserve_existing_role: bool, optional
                    Flag to not modify existing role
                role: str, required
                    Person role in transaction
                owner: bool
                    Indicates whether the person owns this transaction.  There can
                    be only one owner, so setting this flag will reset it for current
                    owner
        """
        return self._get_data(
            "transaction_participants",
            "create",
            within="users",
            uri_params={"transaction_id": transaction_id},
            data=data,
            required_fields=["role", "id"],
        )

    def get_user_transaction_participant(
        self, transaction_id: int, user_id: int, *, full_info: int = None
    ):
        """Get user transaction participant

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        user_id: int, required
            ID of user
        full_info: int, default 0, optional
            Specifies whether to retrieve short or full user information.
        """
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
        """Update user transaction participant

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        user_id: int, required
            ID of user
        data: dict, required
            Data used to update a user participant.  Fields available are:
                id: int, required
                    User ID
                preserve_existing_role: bool, optional
                    Flag to not modify existing role
                role: str, optional
                    Person role in transaction
                owner: bool
                    Indicates whether the person owns this transaction.  There can
                    be only one owner, so setting this flag will reset it for current
                    owner
        """
        return self._get_data(
            "transaction_participants",
            "update",
            within="users",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
            data=data,
            required_fields=["id"],
        )

    def delete_user_transaction_participant(self, transaction_id: int, user_id: int):
        """Remove user transaction participant

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        user_id: int, required
            ID of user
        """
        return self._get_data(
            "transaction_participants",
            "destroy",
            within="users",
            uri_params={"transaction_id": transaction_id, "user_id": user_id},
        )

    def list_contact_transaction_participants(
        self, transaction_id: int, *, full_info: int = None
    ):
        """List of contact transaction participants

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        full_info: int, default 0, optional
            Specifies whether to retrieve short or full contact information.
        """
        return self._get_data(
            "transaction_participants",
            "list",
            within="contacts",
            uri_params={"transaction_id": transaction_id},
            params={"full_info": full_info},
        )

    def create_contact_transaction_participants(self, transaction_id: int, data: dict):
        """Add or update contact participation

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        data: dict, required
            Data used to create a contact participant.  Fields available are:
                id: int, required
                    Contact ID
                preserve_existing_role: bool, optional
                    Flag to not modify existing role
                role: str, required
                    Person role in transaction
                owner: bool
                    Indicates whether the person owns this transaction.  There can
                    be only one owner, so setting this flag will reset it for current
                    owner
        """
        return self._get_data(
            "transaction_participants",
            "create",
            within="contactts",
            uri_params={"transaction_id": transaction_id},
            data=data,
            required_fields=["id", "role"],
        )

    def get_contact_transaction_participant(
        self, transaction_id: int, contact_id: int, *, full_info: int = None
    ):
        """Get contact transaction participant

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        contact_id: int, required
            ID of contact
        full_info: int, default 0, optional
            Specifies whether to retrieve short or full contact information.
        """
        return self._get_data(
            "transaction_participants",
            "retrieve",
            within="contacts",
            uri_params={"transaction_id": transaction_id, "contact_id": contact_id},
            params={"full_info": full_info},
        )

    def update_contact_transaction_participant(
        self, transaction_id: int, contact_id: int, data: dict
    ):
        """Update contact transaction participant

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        contact_id: int, required
            ID of contact
        data: dict, required
            Data used to update a contact participant.  Fields available are:
                id: int, required
                    Contact ID
                preserve_existing_role: bool, required
                    Flag to not modify existing role
                role: str
                    Person role in transaction
                owner: bool
                    Indicates whether the person owns this transaction.  There can
                    be only one owner, so setting this flag will reset it for current
                    owner
        """
        return self._get_data(
            "transaction_participants",
            "update",
            within="contacts",
            uri_params={"transaction_id": transaction_id, "contact_id": contact_id},
            data=data,
            required_fields=["id"],
        )

    def delete_contact_transaction_participant(
        self, transaction_id: int, contact_id: int
    ):
        """Remove contact transaction participant

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        contact_id: int, required
            ID of contact
        """
        return self._get_data(
            "transaction_participants",
            "destroy",
            within="contacts",
            uri_params={"transaction_id": transaction_id, "contact_id": contact_id},
        )

    def list_transaction_commissions(self, transaction_id: int):
        """List of transaction commission items

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        """
        return self._get_data(
            "transaction_commissions",
            "list",
            uri_params={"transaction_id": transaction_id},
        )

    def list_transaction_checklists(self, transaction_id: int):
        """List of available transaction's checklists

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        """
        return self._get_data(
            "transaction_checklists",
            "list",
            uri_params={"transaction_id": transaction_id},
        )

    def get_transaction_checklists(self, transaction_id: int, checklist_id: int):
        """Get transaction checklists by ID

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        checklist_id: int, required
            ID of checklist
        """
        return self._get_data(
            "transaction_checklists",
            "retrieve",
            uri_params={"transaction_id": transaction_id, "checklist_id": checklist_id},
        )

    def list_transaction_tasks(self, transaction_id: int, checklist_id: int):
        """List of tasks in specified transaction checklists

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        checklist_id: int, required
            ID of checklist
        """
        return self._get_data(
            "transaction_tasks",
            "list",
            within="tasks",
            uri_params={"transaction_id": transaction_id, "checklist_id": checklist_id},
        )

    def create_transaction_task(
        self, transaction_id: int, checklist_id: int, data: dict
    ):
        """Create a new task in specified transaction checklists

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        checklist_id: int, required
            ID of checklist
        data: dict, required
            Data used to create a task.  Fields available are:
                name: str, required
                description: str, optional
                document_required: bool, optional
                done: bool, optional
                deadline: int, optional
                    13-digit unix timestamp
        """
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
        """Get transaction task by ID

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        checklist_id: int, required
            ID of checklist
        task_id: int, required
            ID of task
        """
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
        """Get transaction task by ID

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        checklist_id: int, required
            ID of checklist
        task_id: int, required
            ID of task
        data: dict, required
            Data used to create a task.  Fields available are:
                name: str, required
                description: str, optional
                document_required: bool, optional
                done: bool, optional
                deadline: int, optional
                    13-digit unix timestamp
        """
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
        """Submit task's document for review

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        checklist_id: int, required
            ID of checklist
        task_id: int, required
            ID of task
        files: dict, required
            File to submit
        """
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
        """Create task comment

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        checklist_id: int, required
            ID of checklist
        task_id: int, required
            ID of task
        data: dict, required
            Data used to create a comment.  Fields available are:
                text: str, required
        """
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
        """Create transaction document

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        data: dict, required
            Data used to create a comment.  Fields available are:
                task_id: int, optional
                    ID of task to add document to
                name: str
                    Document's file name
                content_type: str
                    Default "text/plain"
                path: str <URL>
                    Public URL to document file
        """
        return self._get_data(
            "transaction_documents",
            "create",
            uri_params={
                "transaction_id": transaction_id,
            },
            data=data,
        )

    def get_transaction_document(self, transaction_id: int, document_id: int):
        """Get transaction's document

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        document_id: int, required
            ID of document
        """
        return self._get_data(
            "transaction_documents",
            "retrieve",
            uri_params={
                "transaction_id": transaction_id,
                "document_id": document_id,
            },
        )

    def create_transaction_note(self, transaction_id: int, data: dict):
        """Add comment to transaction

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        data: dict, required
            Data used to create a comment.  Fields available are:
                text: str
        """
        return self._get_data(
            "transaction_notes",
            "create",
            uri_params={
                "transaction_id": transaction_id,
            },
            data=data,
            required_fields=["text"],
        )

    def list_transaction_backups(
        self,
        transaction_id: int,
        *,
        count: int = None,
        starting_from_id: int = None,
        completed_since: Union[str, int] = None,
        exclude_backup_ids: str = None,
    ):
        """List of transaction's backups

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        count: int, default 1000, optional
            Specifies the number of items to retrieve
        starting_from_id: int, optional
            Specifies the ID of entity to retrieve records starting from
        completed_since: str or int, optional
            Filter backups completed since specified date.  Date format YYYY-MM-DD or
            13-digit unix timestamp
        exclude_backup_ids: str, optional
            Array of strings - filter out backups with IDs in specified comma separated list
        """
        return self._get_data(
            "transaction_backups",
            "list",
            within="all",
            uri_params={"transaction_id": transaction_id},
            params={
                "count": count,
                "starting_from_id": starting_from_id,
                "completed_since": completed_since,
                "exclude_backup_ids": exclude_backup_ids,
            },
        )

    def get_latest_transaction_backup(self, transaction_id: int):
        """Get latest transaction backup

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        """
        return self._get_data(
            "transaction_backups",
            "retrieve",
            within="latest",
            uri_params={"transaction_id": transaction_id},
        )

    def list_transaction_offers(self, transaction_id: int):
        """List available offers in transaction

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        """
        return self._get_data(
            "transaction_offers",
            "list",
            within="all",
            uri_params={"transaction_id": transaction_id},
        )

    def get_transaction_offer(self, transaction_id: int, offer_id: int):
        """Get offer by ID

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        offer_id: int, required
            ID of the offer
        """
        return self._get_data(
            "transaction_offers",
            "retrieve",
            within="all",
            uri_params={"transaction_id": transaction_id, "offer_id": offer_id},
        )

    def get_transaction_offer_attachment(
        self, transaction_id: int, offer_id: int, attachment_id: int
    ):
        """Get offer attachment by ID

        Parameters
        ----------
        transaction_id: int, required
            ID of transaction
        offer_id: int, required
            ID of the offer
        attachment_id: int, required
            ID of the attachment
        """
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
        """Create or update incoming transactions

        Note
        ----
        If existing transaction was already accepted or declined, its updates will be ignored

        Parameters
        ----------
        data: dict, required
            Data used to create an incoming transaction.  Fields available are:
                source_id: str
                    Incoming transaction source - this can be the name of CRM or other
                    system that sourced these transactions.  This allows you to distinguish
                    incoming transactions with the same external IDs from different
                    sources
                transactions: List[dict]
                    See create_transaction
        """
        return self._get_data(
            "incoming_transactions",
            "create",
            data=data,
            required_fields=["source_id", "transactions"],
        )

    def list_reports(self):
        """List available reports in account"""
        return self._get_data(
            "reports",
            "list",
            within="all",
        )

    def list_report_filters(self, report_id: int):
        """List of filters and available filter options for specified report

        Parameters
        ----------
        report_id: int, required
            ID of report
        """
        return self._get_data(
            "reports", "list", within="filters", uri_params={"report_id": report_id}
        )

    def get_report_data(self, report_id: int):
        """Retrieve report data

        Note
        ----
        All query parameters except timezone are filters - field=filter_value

        Parameters
        ----------
        report_id: int, required
            ID of report
        """
        return self._get_data(
            "reports",
            "retrieve",
            within="data",
            uri_params={
                "report_id": report_id,
            },
        )

    def get_sso_token(self, user_id: int):
        """Get SSO token for user

        Note
        ----
        SSO API allows a user to remotely login to Brokermint.  To login a user into
        Brokermint using the sso token, redirect the user to the URL:
        https://my.brokermint.com/users/sign_in_by_token?token=<token>

        Parameters
        ----------
        report_id: int, required
            ID of report
        """
        return self._get_data("sso", "retrieve", uri_params={"user_id": user_id})
