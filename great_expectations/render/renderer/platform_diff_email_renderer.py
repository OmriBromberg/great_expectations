import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from . import EmailRenderer


@dataclass
class PlatformDiffEmailRenderer(EmailRenderer):
    environment: str
    previous_insights10_ci: str
    previous_insights20_ci: str
    current_ci: str

    def render(self, validation_result=None, data_docs_pages=None, notify_with=None):
        title, html = super().render(validation_result, data_docs_pages, notify_with)

        html += f"- <strong>Environment</strong>: {self.environment}</br>"
        html += f"- <strong>Previous Insights 1.0 CI</strong>: {self.previous_insights10_ci}</br>"
        html += f"- <strong>Previous Insights 2.0 CI</strong>: {self.previous_insights20_ci}</br>"
        html += f"- <strong>Current CI</strong>: {self.current_ci}</br>"

        return title, html
