from abc import ABC, abstractmethod
from jinja2 import Environment, ChoiceLoader, PackageLoader
from jinja2 import evalcontextfilter

from reportcard.datasource import DatasourceManager
from reportcard.output import OutputDriver
from reportcard.plugin import PluginManager
from reportcard.utils import module_root


class ViewException(Exception):
    pass


class View(ABC):

    id: str = None
    title: str = None

    def __init__(self, report, datasources: DatasourceManager, **kwargs):
        self.report = report
        self.datasources = datasources
        self._blobs = {}

        if "id" in kwargs:
            self.id = kwargs.pop("id")
        if "title" in kwargs:
            self.title = kwargs.pop("title")
        if "cols" in kwargs:
            self.cols = kwargs.pop("cols")
        else:
            self.cols = report.theme.num_columns

        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    @abstractmethod
    def render(self, env: Environment) -> str:
        pass

    def add_blob(self, id, blob, mime_type=None):
        self._blobs[id] = dict(id=f"{self.id}/{id}", content=blob,
                               mime_type=mime_type)

    def get_blob(self, id):
        return self._blobs.get(id)

    @property
    def blobs(self):
        return self._blobs.values()


class ViewManager(PluginManager):

    namespace = "reportcard.view"
    type_noun = "view"
    exc_class = ViewException

    def __init__(self, datasource_manager, report, config,
                 extension_manager=None):
        self.datasource_manager = datasource_manager
        super(ViewManager, self).__init__(report, config, extension_manager)

    def plugin_factory(self, Plugin, plugin_kwargs, config):
        for attr in ["title", "cols"]:
            value = config.get(attr)
            if value:
                plugin_kwargs.setdefault(attr, value)

        return Plugin(self.report, self.datasource_manager, **plugin_kwargs)

    def _blob_filter(self, output_driver):
        @evalcontextfilter
        def render_blob(eval_ctx, blob_id):
            view_id = eval_ctx.environment.view_id

            blob = self.call_instance(view_id, "get_blob", blob_id)
            if not blob:
                raise ViewException((
                    f"Missing content for blob {blob_id}. Make sure the blob "
                    "was added before rendering the View template"))

            return output_driver.render_blob_inline(blob)

        return render_blob

    def render(self, env: Environment, output_driver: OutputDriver) -> list:
        blocks = []
        for id, view in self.instances:
            try:
                # Allow any extending package to optionally define its own
                # ./templates directory at the root module level.
                view_env = env.overlay(
                    loader=ChoiceLoader([
                        PackageLoader(module_root(view.__module__)),
                        PackageLoader(module_root(View.__module__))
                    ])
                )
                view_env.extend(view_id=id)
                view_env.filters["blob"] = self._blob_filter(output_driver)

                output = view.render(view_env)
                if not isinstance(output, str):
                    raise ViewException((
                        "The view did not render a valid string"))

                blocks.append(dict(
                    id=id,
                    title=view.title or "",
                    cols=view.cols,
                    output=output
                ))
            except Exception as exc:
                self.log.error((
                    f"Error rendering {self.type_noun} {id}: {exc}"))
                blocks.append(dict(
                    id=id,
                    title="",
                    cols=view.cols,
                    output=f"Error rendering {id}"
                ))
        return blocks

    @property
    def blobs(self):
        _blobs = []
        for id, view in self.instances:
            _blobs.extend(view.blobs)
        return _blobs
