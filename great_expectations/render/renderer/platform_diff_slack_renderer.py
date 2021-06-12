import logging
from dataclasses import dataclass


logger = logging.getLogger(__name__)

from ...core.id_dict import BatchKwargs
from . import SlackRenderer


@dataclass
class PlatformDiffSlackRenderer(SlackRenderer):
    environment: str
    previous_insights10_ci: str
    previous_insights20_ci: str
    current_ci: str

    def render(
        self,
        validation_result=None,
        data_docs_pages=None,
        notify_with=None,
    ):
        query = super().render(validation_result, data_docs_pages, notify_with)
        platform_diff_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Environment*: {self.environment}\n"
                        f"*Previous Insights 1.0 CI*: {self.previous_insights10_ci}\n"
                        f"*Previous Insights 2.0 CI*: {self.previous_insights20_ci}\n"
                        f"*Current CI*: {self.current_ci}",
            },
        }
        query["blocks"].insert(-2, platform_diff_block)

        return query