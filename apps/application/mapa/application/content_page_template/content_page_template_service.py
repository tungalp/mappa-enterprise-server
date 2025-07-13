from typing import List
from mapa.application.constants import ContentPageType
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.application.content_page_template.content_page_template_model import ContentPageTemplate, CreateContentPageTemplate, UpdateAllContentPageTemplate, UpdateContentPageTemplate
from mapa.application.content_page_template.content_page_template_repository import ContentPageTemplateRepository
from nanoid import generate

from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


class ContentPageTemplateService(BaseEntityService[ContentPageTemplateRepository, ContentPageTemplate, CreateContentPageTemplate, UpdateContentPageTemplate, UpdateAllContentPageTemplate]):
    """ContentPageTemplateService"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ContentPageTemplateRepository, ContentPageTemplate)

    async def create(self, input_obj: CreateContentPageTemplate, tenant_id: str | None = None) -> ContentPageTemplate:
        """ContentPage oluştururken page tipine göre default schema atayarak kaydeder."""

        query_args = QueryArgs(where=[
            Filter(field="name", op=FilterOp.EQUAL, value=input_obj.name),
        ])
        count = await self.repo.count(query_args, tenant_id)
        if count > 0:
            raise Exception("duplicate_template_name")

        if input_obj.designer_schema == None:
            if input_obj.type == ContentPageType.BLANK:
                input_obj.designer_schema = {"html": "<b>Welcome</b>"}
            elif input_obj.type == ContentPageType.PAGE:
                input_obj.designer_schema = {"form": {"labelCol": 6, "wrapperCol": 12}, "schema": {"type": "object", "properties": {
                }, "x-designable-id": generate(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', size=8)}}
            else:
                input_obj.designer_schema = {}

        return await super().create(input_obj, tenant_id)

    async def create_all(self, input_objs: List[CreateContentPageTemplate], tenant_id: str | None = None) -> List[ContentPageTemplate]:
        """ContentPage oluştururken page tipine göre default schema atayarak kaydeder."""
        for create_content_page in input_objs:
            query_args = QueryArgs(where=[
            Filter(field="name", op=FilterOp.EQUAL, value=create_content_page.name),
            ])
            count = await self.repo.count(query_args, tenant_id)
            if count > 0:
                raise Exception("duplicate_template_name")
        
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
