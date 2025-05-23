from typing import List, Optional, Union, Dict, Any

from sabnzbdapi.bound_methods import SubFunctions


class JobFunctions(SubFunctions):
    """
    Provides methods for interacting with SABnzbd's job and queue management API.

    This class extends `SubFunctions` (assumed to provide the `call` method)
    and offers convenient asynchronous methods to add, manage, and query
    NZB downloads, as well as control SABnzbd's general behavior like speed limits
    and configuration.
    """

    async def add_uri(
        self,
        url: str = "",
        file: str = "",
        nzbname: str = "",
        password: str = "",
        cat: str = "*",
        script: Optional[List[str]] = None,
        priority: int = 0,
        pp: int = 1,
    ) -> Dict[str, Any]:
        """
        Adds a new NZB job to SABnzbd's queue either from a URL or a local file.

        You must provide either `url` or `file`, but not both.

        Args:
            url (str): The URL of the NZB file to add. Used if `file` is empty.
            file (str): The path to a local NZB file to add. Used if `url` is empty.
            nzbname (str): The desired name for the job in SABnzbd.
            password (str): Password for the NZB if it's protected.
            cat (str): The category for the job. Defaults to "*".
            script (Optional[List[str]]): List of scripts to run after download. Defaults to None.
            priority (int): The priority of the job (0=Normal, -100=Paused, 1=High, 100=Force).
            pp (int): Post-processing options (0=None, 1=Default, 2=Full, 3=Skip). Defaults to 1.

        Returns:
            Dict[str, Any]: A dictionary containing the status and nzo_ids of the added job(s),
                            e.g., `{"status": True, "nzo_ids": ["SABnzbd_nzo_kyt1f0"]}`.

        Raises:
            ValueError: If neither `url` nor `file` is provided, or if both are provided.
        """
        if not url and not file:
            raise ValueError("Either 'url' or 'file' must be provided.")
        if url and file:
            raise ValueError("Cannot provide both 'url' and 'file'. Choose one.")

        if file:
            name = file
            mode = "addlocalfile"
        else:
            name = url
            mode = "addurl"

        params = {
            "mode": mode,
            "name": name,
            "nzbname": nzbname,
            "password": password,
            "cat": cat,
            "script": script,
            "priority": priority,
            "pp": pp,
        }
        # Filter out empty parameters if SABnzbd API handles them poorly
        params = {k: v for k, v in params.items() if v is not None and v != "" and v != []}

        return await self.call(params)

    async def get_downloads(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        category: Optional[Union[str, List[str]]] = None,
        priority: Optional[Union[int, List[str]]] = None, # SABnzbd API uses string for priority like 'Normal', 'High'
        status: Optional[Union[str, List[str]]] = None,
        nzo_ids: Optional[Union[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves a list of current downloads in the queue, with optional filtering.

        Args:
            start (Optional[int]): The starting index for the list of downloads.
            limit (Optional[int]): The maximum number of downloads to return.
            search (Optional[str]): Search string to filter downloads by name.
            category (Optional[Union[str, List[str]]]): Filter by category or a comma-separated list of categories.
            priority (Optional[Union[int, List[str]]]): Filter by priority. Use integer codes (0=Normal, 1=High, 100=Force, -100=Paused)
                                                       or a comma-separated list of string priorities (e.g., "Normal", "High").
            status (Optional[Union[str, List[str]]]): Filter by status (e.g., "Downloading", "Queued", "Paused").
            nzo_ids (Optional[Union[str, List[str]]]): Filter by specific NFO ID(s) (comma-separated if list).

        Returns:
            Dict[str, Any]: A dictionary containing queue information and a list of download slots.
                            See SABnzbd API documentation for full response structure.
        """
        params: Dict[str, Any] = {"mode": "queue"}

        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        # Convert list parameters to comma-separated strings if necessary
        if category:
            params["category"] = category if isinstance(category, str) else ",".join(category)
        if priority:
            # Handle both int and list[str] for priority
            if isinstance(priority, list):
                params["priority"] = ",".join(str(p) for p in priority)
            else:
                params["priority"] = priority
        if status:
            params["status"] = status if isinstance(status, str) else ",".join(status)
        if nzo_ids:
            params["nzo_ids"] = nzo_ids if isinstance(nzo_ids, str) else ",".join(nzo_ids)

        return await self.call(params)

    async def pause_job(self, nzo_id: str) -> Dict[str, Any]:
        """
        Pauses a specific download job by its NFO ID.

        Args:
            nzo_id (str): The NFO ID of the job to pause.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True, "nzo_ids": ["all effected ids"]}`.
        """
        return await self.call({"mode": "queue", "name": "pause", "value": nzo_id})

    async def resume_job(self, nzo_id: str) -> Dict[str, Any]:
        """
        Resumes a specific download job by its NFO ID.

        Args:
            nzo_id (str): The NFO ID of the job to resume.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True, "nzo_ids": ["all effected ids"]}`.
        """
        return await self.call({"mode": "queue", "name": "resume", "value": nzo_id})

    async def delete_job(self, nzo_id: Union[str, List[str]], delete_files: bool = False) -> Dict[str, Any]:
        """
        Deletes one or more jobs from the queue.

        Args:
            nzo_id (Union[str, List[str]]): The NFO ID(s) of the job(s) to delete.
            delete_files (bool): If True, also deletes the associated downloaded files. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True, "nzo_ids": ["all effected ids"]}`.
        """
        nzo_id_str = nzo_id if isinstance(nzo_id, str) else ",".join(nzo_id)
        return await self.call(
            {
                "mode": "queue",
                "name": "delete",
                "value": nzo_id_str,
                "del_files": 1 if delete_files else 0,
            },
        )

    async def pause_all(self) -> Dict[str, Any]:
        """
        Pauses all active downloads in SABnzbd.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call({"mode": "pause"})

    async def resume_all(self) -> Dict[str, Any]:
        """
        Resumes all paused downloads in SABnzbd.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call({"mode": "resume"})

    async def purge_all(self, delete_files: bool = False) -> Dict[str, Any]:
        """
        Purges all items from the queue (downloads that are still active will be cancelled).

        Args:
            delete_files (bool): If True, also deletes associated downloaded files. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True, "nzo_ids": ["all effected ids"]}`.
        """
        return await self.call(
            {
                "mode": "queue",
                "name": "purge",
                "del_files": 1 if delete_files else 0,
            },
        )

    async def get_files(self, nzo_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about files within a specific NZB job.

        Args:
            nzo_id (str): The NFO ID of the job to get file details for.

        Returns:
            Dict[str, Any]: A dictionary containing a list of file details for the specified job.
                            See SABnzbd API documentation for full response structure.
        """
        return await self.call({"mode": "get_files", "value": nzo_id})

    async def remove_file(self, nzo_id: str, file_ids: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Removes one or more files from a specific NZB job.

        Args:
            nzo_id (str): The NFO ID of the parent job.
            file_ids (Union[str, List[str]]): The NZF ID(s) of the file(s) to remove (comma-separated if list).

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation.
                            Note: The exact return value for removed file NZF IDs is not consistent
                            in SABnzbd API documentation, but typically includes status.
        """
        file_ids_str = file_ids if isinstance(file_ids, str) else ",".join(file_ids)
        return await self.call(
            {
                "mode": "queue",
                "name": "delete_nzf",
                "value": nzo_id,
                "value2": file_ids_str,
            },
        )

    async def get_history(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        category: Optional[Union[str, List[str]]] = None,
        archive: Optional[int] = None, # 0=not in archive, 1=in archive
        status: Optional[Union[str, List[str]]] = None,
        nzo_ids: Optional[Union[str, List[str]]] = None,
        failed_only: bool = False,
        last_history_update: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves the download history from SABnzbd, with optional filtering.

        Args:
            start (Optional[int]): The starting index for the list of history entries.
            limit (Optional[int]): The maximum number of history entries to return.
            search (Optional[str]): Search string to filter history entries by name.
            category (Optional[Union[str, List[str]]]): Filter by category or a comma-separated list of categories.
            archive (Optional[int]): Filter by archive status (0: not archived, 1: archived).
            status (Optional[Union[str, List[str]]]): Filter by status (e.g., "Completed", "Failed").
            nzo_ids (Optional[Union[str, List[str]]]): Filter by specific NFO ID(s) (comma-separated if list).
            failed_only (bool): If True, only retrieve failed history entries. Defaults to False.
            last_history_update (Optional[int]): Timestamp to get history updated since this time.

        Returns:
            Dict[str, Any]: A dictionary containing history information and a list of history slots.
                            See SABnzbd API documentation for full response structure.
        """
        params: Dict[str, Any] = {"mode": "history"}

        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if archive is not None:
            params["archive"] = archive
        if failed_only:
            params["failed_only"] = 1
        if last_history_update is not None:
            params["last_history_update"] = last_history_update

        # Convert list parameters to comma-separated strings if necessary
        if category:
            params["category"] = category if isinstance(category, str) else ",".join(category)
        if status:
            params["status"] = status if isinstance(status, str) else ",".join(status)
        if nzo_ids:
            params["nzo_ids"] = nzo_ids if isinstance(nzo_ids, str) else ",".join(nzo_ids)

        return await self.call(params)

    async def retry_item(self, nzo_id: str, password: str = "") -> Dict[str, Any]:
        """
        Retries a specific failed item from the history.

        Args:
            nzo_id (str): The NFO ID of the item to retry.
            password (str): Optional password for the NZB if it's protected.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call(
            {"mode": "retry", "value": nzo_id, "password": password},
        )

    async def retry_all(self) -> Dict[str, Any]:
        """
        Retries all failed items in the history.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call({"mode": "retry_all"})

    async def delete_history(
        self,
        nzo_ids: Union[str, List[str]],
        archive: int = 0, # SABnzbd uses 0 for no archive, 1 for archive
        delete_files: bool = False,
    ) -> Dict[str, Any]:
        """
        Deletes one or more entries from the download history.

        Args:
            nzo_ids (Union[str, List[str]]): The NFO ID(s) of the history entry/entries to delete.
            archive (int): Whether to only delete items that are archived (1) or not (0). Defaults to 0.
            delete_files (bool): If True, also deletes the associated downloaded files. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        nzo_ids_str = nzo_ids if isinstance(nzo_ids, str) else ",".join(nzo_ids)
        return await self.call(
            {
                "mode": "history",
                "name": "delete",
                "value": nzo_ids_str,
                "archive": archive,
                "del_files": 1 if delete_files else 0,
            },
        )

    async def change_job_pp(self, nzo_id: str, pp: int) -> Dict[str, Any]:
        """
        Changes the post-processing setting for a specific job.

        Args:
            nzo_id (str): The NFO ID of the job.
            pp (int): The new post-processing option (0=None, 1=Default, 2=Full, 3=Skip).

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call(
            {"mode": "change_opts", "value": nzo_id, "value2": pp},
        )

    async def set_speedlimit(self, limit: Union[str, int]) -> Dict[str, Any]:
        """
        Sets the global download speed limit for SABnzbd.

        The limit can be an integer (in KB/s) or a string like "1.5M" for 1.5 MB/s.
        Use "0" or 0 for unlimited speed.

        Args:
            limit (Union[str, int]): The desired speed limit.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call(
            {"mode": "config", "name": "speedlimit", "value": limit},
        )

    async def delete_config(self, section: str, keyword: str) -> Dict[str, Any]:
        """
        Deletes a specific configuration keyword within a section.

        Args:
            section (str): The configuration section (e.g., "misc", "servers").
            keyword (str): The keyword to delete (e.g., "max_concurrent_downloads").

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call(
            {"mode": "del_config", "section": section, "keyword": keyword},
        )

    async def set_config_default(self, keyword: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Resets one or more configuration keywords to their default values.

        Args:
            keyword (Union[str, List[str]]): The keyword(s) to reset.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        keyword_str = keyword if isinstance(keyword, str) else ",".join(keyword)
        return await self.call({"mode": "set_config_default", "keyword": keyword_str})

    async def get_config(
        self,
        section: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves SABnzbd's configuration settings.

        Args:
            section (Optional[str]): If provided, retrieves settings only for this section.
            keyword (Optional[str]): If provided, retrieves only this specific keyword's value.

        Returns:
            Dict[str, Any]: A dictionary representing the configuration.
                            If no section/keyword is specified, returns the full config.
        """
        params = {"mode": "get_config"}
        if section is not None:
            params["section"] = section
        if keyword is not None:
            params["keyword"] = keyword
        return await self.call(params)

    async def set_config(self, section: str, keyword: str, value: str) -> Dict[str, Any]:
        """
        Sets a specific configuration keyword to a new value.

        Args:
            section (str): The configuration section.
            keyword (str): The keyword to set.
            value (str): The new value for the keyword.

        Returns:
            Dict[str, Any]: A dictionary containing the new setting if saved successfully.
        """
        return await self.call(
            {
                "mode": "set_config",
                "section": section,
                "keyword": keyword,
                "value": value,
            },
        )

    async def set_special_config(self, section: str, items: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sets multiple configuration items within a specific section.

        This is useful for setting multiple keywords in one API call.

        Args:
            section (str): The configuration section.
            items (Dict[str, Any]): A dictionary where keys are keywords and values are their new settings.

        Returns:
            Dict[str, Any]: A dictionary containing the new settings if saved successfully.
        """
        return await self.call(
            {
                "mode": "set_config",
                "section": section,
                **items,  # Unpack items directly into parameters
            },
        )

    async def server_stats(self) -> Dict[str, Any]:
        """
        Retrieves detailed download statistics per server.

        Returns:
            Dict[str, Any]: A dictionary containing overall and per-server download statistics.
                            See SABnzbd API documentation for full response structure.
        """
        return await self.call({"mode": "server_stats"})

    async def version(self) -> Dict[str, Any]:
        """
        Retrieves the SABnzbd version number.

        Returns:
            Dict[str, Any]: A dictionary containing the version, e.g., `{'version': '4.2.2'}`.
        """
        return await self.call({"mode": "version"})

    async def restart(self) -> Dict[str, Any]:
        """
        Restarts the SABnzbd application.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call({"mode": "restart"})

    async def restart_repair(self) -> Dict[str, Any]:
        """
        Restarts SABnzbd after checking for and repairing any issues.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call({"mode": "restart_repair"})

    async def shutdown(self) -> Dict[str, Any]:
        """
        Shuts down the SABnzbd application.

        Returns:
            Dict[str, Any]: A dictionary indicating the status of the operation,
                            e.g., `{"status": True}`.
        """
        return await self.call({"mode": "shutdown"})
