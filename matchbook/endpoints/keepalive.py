import json

from matchbook.endpoints.baseendpoint import BaseEndpoint
from matchbook.exceptions import AuthError


class KeepAlive(BaseEndpoint):
    def __call__(self, session=None):
        session = session or self.client.session
        response = self.request(
            "GET",
            self.client.urn_main,
            "security/session",
            data=self.data,
            session=session,
        )
        if response.status_code == 200:
            pass
        elif response.status_code == 401:
            response = self.request(
                "POST",
                self.client.urn_main,
                "security/session",
                data=self.data,
                session=session,
            )
            if response.status_code != 200:
                raise AuthError(response)

            response_json = response.json()
            self.client.set_session_token(
                response_json.get("session-token"), response_json.get("user-id")
            )
        else:
            raise AuthError(response)

    def request(
        self,
        request_method,
        urn,
        method,
        params=None,
        data=None,
        target=None,
        session=None,
    ):
        """
        :param request_method: type of request to be sent.
        :param urn: matchbook urn to append to url specified.
        :param method: Matchbook method to be used.
        :param params: Params to be used in request
        :param url: define different URL to use.
        :param data: data to be sent in request body.
        :param target: target key to get from data, if None returns full response.
        :param session: Requests session to be used, reduces latency.
        """
        session = session or self.client.session
        data["session-token"] = self.client.session_token
        data["user-id"] = self.client.user_id
        request_url = f"{self.client.url}{urn}{method}"
        return session.request(
            request_method,
            request_url,
            params=params,
            data=json.dumps(data),
            headers=self.client.headers,
        )

    @property
    def data(self):
        return {"username": self.client.username, "password": self.client.password}
