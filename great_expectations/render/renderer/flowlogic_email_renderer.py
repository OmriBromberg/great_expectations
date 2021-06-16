import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from . import EmailRenderer


@dataclass
class FlowLogicEmailRenderer(EmailRenderer):
    branch: str
    ci: str
    circle_ci_url: str
    caller: str

    def render(self, validation_result=None, data_docs_pages=None, notify_with=None):
        title, html = super().render(validation_result, data_docs_pages, notify_with)

        html += f"- <strong>Branch</strong>: https://github.com/skyline-ai/flowlogic/tree/{self.branch}</br>"
        html += f"- <strong>CI Project</strong>: https://console.cloud.google.com/bigquery?project={self.ci}</br>"
        html += f"- <strong>Circle CI</strong>: {self.circle_ci_url}</br>"
        html += f"- <strong>Caller</strong>: {self.caller}</br>"

        return title, html
