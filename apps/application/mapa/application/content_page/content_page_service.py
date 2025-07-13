from typing import List, Optional
from mapa.application.constants import ContentPageType
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.application.content_page.content_page_model import ContentPage, CreateContentPage, UpdateAllContentPage, UpdateContentPage
from mapa.application.content_page.content_page_repository import ContentPageRepository
from nanoid import generate


class ContentPageService(BaseEntityService[ContentPageRepository, ContentPage, CreateContentPage, UpdateContentPage, UpdateAllContentPage]):
    """ContentPageService"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ContentPageRepository, ContentPage)

    async def create(self, input_obj: CreateContentPage, tenant_id: str | None = None) -> ContentPage:
        """ContentPage oluştururken page tipine göre default schema atayarak kaydeder."""
        if input_obj.designer_schema == None:
            if input_obj.type == ContentPageType.BLANK:
                input_obj.designer_schema = {"html": "<b>Welcome</b>"}
            elif input_obj.type == ContentPageType.PAGE:
                input_obj.designer_schema = {"form": {"labelCol": 6, "wrapperCol": 12}, "schema": {"type": "object", "properties": {
                }, "x-designable-id": generate(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', size=8)}}
            else:
                input_obj.designer_schema = {}

        return await super().create(input_obj, tenant_id)

    async def create_all(self, input_objs: List[CreateContentPage], tenant_id: str | None = None) -> List[ContentPage]:
        """ContentPage oluştururken page tipine göre default schema atayarak kaydeder."""
        for create_content_page in input_objs:
            if create_content_page.designer_schema == None:
                if create_content_page.type == ContentPageType.BLANK:
                    create_content_page.designer_schema = {
                        "html": "<b>Welcome</b>"}
                elif create_content_page.type == ContentPageType.PAGE:
                    create_content_page.designer_schema = {"form": {"labelCol": 6, "wrapperCol": 12}, "schema": {"type": "object", "properties": {
                    }, "x-designable-id": generate(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', size=8)}}
                else:
                    create_content_page.designer_schema = {}

        return await super().create_all(input_objs, tenant_id)
