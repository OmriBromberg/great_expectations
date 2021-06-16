import logging
from dataclasses import dataclass


logger = logging.getLogger(__name__)

from . import SlackRenderer


@dataclass
class FlowLogicSlackRenderer(SlackRenderer):
    branch: str
    ci: str
    circle_ci_url: str
    caller: str

    def render(
        self,
        validation_result=None,
        data_docs_pages=None,
        notify_with=None,
    ):
        query = super().render(validation_result, data_docs_pages, notify_with)
        flowlogic_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Branch*: {self.branch}\n"
                        f"*CI Project*: https://console.cloud.google.com/bigquery?project={self.ci}\n"
                        f"*Circle CI:*: {self.circle_ci_url}\n"
                        f"*Caller*: {self.caller}",
            },
        }
        query["blocks"].insert(-2, flowlogic_block)

        return query