from sabnzbdapi.bound_methods import SubFunctions


class JobFunctions(SubFunctions):
    async def add_uri(
        self,
        url: str = "",
        file: str = "",
        nzbname: str = "",
        password: str = "",
        cat: str = "*",
        script: list | None = None,
        priority: int = 0,
        pp: int = 1,
    ):
        'return {"status": True, "nzo_ids": ["SABnzbd_nzo_kyt1f0"]}'

        if file:
            name = file
            mode = "addlocalfile"
        else:
            name = url
            mode = "addurl"

        return await self.call(
            {
                "mode": mode,
                "name": name,
                "nzbname": nzbname,
                "password": password,
                "cat": cat,
                "script": script,
                "priority": priority,
                "pp": pp,
            },
        )

    async def get_downloads(
        self,
        start: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        category: str | list[str] | None = None,
        priority: int | list[int] | None = None,
        status: str | list[str] | None = None,
        nzo_ids: str | list[str] | None = None,
    ):
        """return {
            "queue": {
                ...
            }
        }"""

        if nzo_ids:
            nzo_ids = nzo_ids if isinstance(nzo_ids, str) else ",".join(nzo_ids)
        if status:
            status = status if isinstance(status, str) else ",".join(status)
        if category:
            category = category if isinstance(category, str) else ",".join(category)
        if priority:
            priority = priority if isinstance(priority, str) else ",".join(priority)

        return await self.call(
            {
                "mode": "queue",
                "start": start,
                "limit": limit,
                "search": search,
                "category": category,
                "priority": priority,
                "status": status,
                "nzo_ids": nzo_ids,
            },
        )

    # Continue with the rest of the methods using Union and Optional for type hints
