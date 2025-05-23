from functools import wraps
from typing import Dict, Optional, Any

from httpx import AsyncClient, AsyncHTTPTransport, DecodingError, Timeout, RequestError, HTTPStatusError
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from .exception import APIConnectionError
from .job_functions import JobFunctions


# Suppress InsecureRequestWarning if certificate verification is disabled
disable_warnings(InsecureRequestWarning)


class SabnzbdSession(AsyncClient):
    """
    A custom asynchronous HTTP client session for SABnzbd API calls.
    It wraps the httpx.AsyncClient to apply default timeout and redirect settings.
    """

    @wraps(AsyncClient.request)
    async def request(self, method: str, url: str, **kwargs: Any) -> Any:
        """
        Overrides the default request method to set common defaults.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST").
            url (str): The URL for the request.
            **kwargs: Additional keyword arguments to pass to the httpx.AsyncClient.request method.

        Returns:
            httpx.Response: The HTTP response object.
        """
        # Set default timeout if not already provided in kwargs
        kwargs.setdefault(
            "timeout",
            Timeout(connect=30, read=60, write=60, pool=None),
        )
        # Always follow redirects by default
        kwargs.setdefault("follow_redirects", True)
        return await super().request(method, url, **kwargs)


class SabnzbdClient(JobFunctions):
    """
    A client for interacting with the SABnzbd API.

    This class provides methods to communicate with a SABnzbd instance,
    handling API key authentication, request retries, and session management.
    It inherits from JobFunctions (assumed to be a base class for job-related operations).
    """

    # Class-level flag to indicate if a login has been attempted/successful (though not used in current code)
    LOGGED_IN: bool = False

    def __init__(
        self,
        host: str,
        api_key: str,
        port: str = "8070",
        VERIFY_CERTIFICATE: bool = False,
        RETRIES: int = 5,  # Changed default retries to 5 for consistency with call method
        HTTPX_REQUETS_ARGS: Optional[Dict[str, Any]] = None,
    ):
        """
        Initializes the SabnzbdClient.

        Args:
            host (str): The host address of the SABnzbd instance (e.g., "http://localhost").
            api_key (str): The API key for SABnzbd authentication.
            port (str): The port number of the SABnzbd instance. Defaults to "8070".
            VERIFY_CERTIFICATE (bool): Whether to verify SSL certificates. Defaults to False.
            RETRIES (int): The number of retries for network requests. Defaults to 5.
            HTTPX_REQUETS_ARGS (Optional[Dict[str, Any]]): Additional arguments to pass
                                                           to all httpx requests. Defaults to None.
        """
        self._base_url: str = f"{host.rstrip('/')}:{port}/sabnzbd/api"
        self._default_params: Dict[str, str] = {"apikey": api_key, "output": "json"}
        self._VERIFY_CERTIFICATE: bool = VERIFY_CERTIFICATE
        self._RETRIES: int = RETRIES
        self._HTTPX_REQUETS_ARGS: Dict[str, Any] = HTTPX_REQUETS_ARGS if HTTPX_REQUETS_ARGS is not None else {}
        self._http_session: Optional[SabnzbdSession] = None

        # Call the base class constructor
        super().__init__()

    def _session(self) -> SabnzbdSession:
        """
        Lazily initializes and returns the httpx.AsyncClient session.

        Returns:
            SabnzbdSession: The httpx.AsyncClient session configured for SABnzbd.
        """
        if self._http_session is not None:
            return self._http_session

        # Configure AsyncHTTPTransport with retries and SSL verification
        transport = AsyncHTTPTransport(
            retries=self._RETRIES,
            verify=self._VERIFY_CERTIFICATE,
        )

        # Create the custom session
        self._http_session = SabnzbdSession(transport=transport, verify=self._VERIFY_CERTIFICATE)

        return self._http_session

    async def call(
        self,
        params: Optional[Dict[str, Any]] = None,
        api_method: str = "GET",
        requests_args: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Makes an API call to the SABnzbd instance.

        This method handles request construction, retries for transient network errors,
        and JSON response parsing.

        Args:
            params (Optional[Dict[str, Any]]): A dictionary of parameters specific to this API call.
                                                These will be merged with default parameters.
                                                Defaults to None.
            api_method (str): The HTTP method to use for the request (e.g., "GET", "POST").
                              Defaults to "GET".
            requests_args (Optional[Dict[str, Any]]): Additional httpx request arguments
                                                     for this specific call. Defaults to None.
            **kwargs: Arbitrary keyword arguments that will be merged into `params`.

        Raises:
            DecodingError: If the response cannot be decoded as JSON.
            APIConnectionError: If all retry attempts fail to establish a connection or
                                receive a valid response from the API.
            HTTPStatusError: If the HTTP response indicates an error (e.g., 4xx, 5xx).

        Returns:
            Dict[str, Any]: The JSON response from the SABnzbd API.
        """
        if params is None:
            params = {}
        if requests_args is None:
            requests_args = {}

        session = self._session()
        # Merge call-specific params with kwargs
        merged_params = {**params, **kwargs}
        # Merge global HTTPX args with call-specific HTTPX args
        requests_kwargs = {**self._HTTPX_REQUETS_ARGS, **requests_args}

        retries_attempted = 0
        response_data: Optional[Dict[str, Any]] = None

        while retries_attempted < self._RETRIES:
            try:
                res = await session.request(
                    method=api_method,
                    url=self._base_url,
                    params={**self._default_params, **merged_params},
                    **requests_kwargs,
                )
                res.raise_for_status()  # Raise HTTPStatusError for 4xx/5xx responses
                response_data = res.json()
                break  # Success, exit retry loop
            except DecodingError as e:
                # This means the response content is not valid JSON
                raise DecodingError(f"Failed to decode JSON response: {res.text}") from e
            except RequestError as e:
                # Catch network-related errors (e.g., connection refused, timeout)
                retries_attempted += 1
                if retries_attempted < self._RETRIES:
                    LOGGER.warning(
                        f"Network error during SABnzbd API call (attempt {retries_attempted}/{self._RETRIES}): {e}. Retrying..."
                    )
                    await asyncio.sleep(1)  # Small delay before retrying
                else:
                    raise APIConnectionError(f"Failed to connect to SABnzbd API after {self._RETRIES} attempts: {e}") from e
            except HTTPStatusError as e:
                # Catch HTTP status errors (e.g., 404, 500)
                raise HTTPStatusError(f"SABnzbd API returned an error status {e.response.status_code}: {e.response.text}") from e
            except Exception as e:
                # Catch any other unexpected exceptions
                raise APIConnectionError(f"An unexpected error occurred during API call: {e}") from e

        if response_data is None:
            # This case should ideally not be reached if RequestError is properly handled and retries are exhausted
            raise APIConnectionError("Failed to receive a response from SABnzbd API after multiple attempts.")

        return response_data

    async def close(self) -> None:
        """
        Closes the underlying HTTP session if it's open.
        It's important to call this method when the client is no longer needed
        to release resources.
        """
        if self._http_session is not None:
            await self._http_session.aclose()
            self._http_session = None
