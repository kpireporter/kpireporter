from abc import ABC, abstractmethod

from kpireport.plugin import PluginManager


class OutputDriverError(Exception):
    pass


class OutputDriver(ABC):
    """
    :param report: the Report object.
    :type report: :class:`kpireport.report.Report`
    :param id: the Output driver ID declared in the report configuration.
    :type id: str
    :param **kwargs: Additional output driver parameters, declared as ``args``
                     in the report configuration.
    """
    id: str = None
    supported_formats: list = ["md", "html"]

    def __init__(self, report, **kwargs):
        self.report = report
        if "id" in kwargs:
            self.id = kwargs.pop("id")
        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        """
        Initialize the output driver from the report configuration.

        :param **kwargs: Arbitrary keyword arguments, declared as ``args``
                         in the report configuration.
        """
        pass

    def render_blob_inline(self, blob, fmt=None):
        raise NotImplementedError(
            f"'{self.id}' driver does not support inline blobs")

    def can_render(self, fmt):
        return fmt in self.supported_formats

    @abstractmethod
    def render_output(self, content, blobs):
        """
        Render the report content for the target delivery mechanism.

        :param content: The report contents, rendered in a variety of formats:

          :html: (str) The HTML content
          :md: (str) The Markdown content
          :views_html: (list) The individual Views HTML output
          :views_md: (list) The individual Views MD output

        :type content: dict
        :param blobs: The list of Blobs rendered by all Views in the report.
        :type blobs: list
        """
        pass


class OutputDriverManager(PluginManager):
    namespace = "kpireport.output"
    type_noun = "output driver"
    exc_class = OutputDriverError
