from abc import ABC, abstractmethod
import traceback

from jinja2 import Environment, ChoiceLoader, PackageLoader
from jinja2 import evalcontextfilter

from kpireport.datasource import DatasourceManager
from kpireport.output import OutputDriver
from kpireport.plugin import PluginManager
from kpireport.utils import module_root


class ViewException(Exception):
    pass


class Blob:
    def __init__(self, id, content, mime_type=None, title=None):
        self.id = id
        self.content = content
        self.mime_type = mime_type
        self.title = title


class View(ABC):
    """The view"""

    id: str = None
    title: str = None
    description: str = None

    def __init__(self, report: "Report", datasources: DatasourceManager, **kwargs):
        self.report = report
        self.datasources = datasources
        self._blobs = {}

        if "id" in kwargs:
            self.id = kwargs.pop("id")
        if "title" in kwargs:
            self.title = kwargs.pop("title")
        if "description" in kwargs:
            self.description = kwargs.pop("description")
        if "cols" in kwargs:
            self.cols = kwargs.pop("cols")
        else:
            self.cols = report.theme.num_columns

        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    def supports(self, fmt) -> bool:
        return callable(getattr(self, f"render_{fmt}", None))

    def render(self, env: Environment, fmt="html") -> str:
        if not self.supports(fmt):
            raise ValueError(f"No {fmt} renderer found")

        return getattr(self, f"render_{fmt}")(env)

    def add_blob(self, id, blob, mime_type, title=None):
        self._blobs[id] = Blob(
            id=f"{self.id}/{id}",
            content=blob,
            mime_type=mime_type,
            title=title or self.title,
        )

    def get_blob(self, id) -> Blob:
        return self._blobs.get(id)

    @property
    def blobs(self) -> "List[Blob]":
        return self._blobs.values()


class ViewManager(PluginManager):

    namespace = "kpireport.view"
    type_noun = "view"
    exc_class = ViewException

    def __init__(self, datasource_manager, report, config, extension_manager=None):
        self.datasource_manager = datasource_manager
        super(ViewManager, self).__init__(report, config, extension_manager)

    def plugin_factory(self, config, plugin_class, plugin_kwargs):
        for attr in ["title", "description", "cols"]:
            value = config.get(attr)
            if value:
                plugin_kwargs.setdefault(attr, value)

        return plugin_class(self.report, self.datasource_manager, **plugin_kwargs)

    def _blob_filter(self, output_driver):
        @evalcontextfilter
        def render_blob(eval_ctx, blob_id):
            view_id = eval_ctx.environment.view_id
            fmt = eval_ctx.environment.fmt

            blob = self.call_instance(view_id, "get_blob", blob_id)
            if not blob:
                raise ViewException(
                    (
                        f"Missing content for blob '{blob_id}'. Make sure the "
                        "blob was added before rendering the View template"
                    )
                )

            return output_driver.render_blob_inline(blob, fmt)

        return render_blob

    def render(self, env: Environment, fmt: str, output_driver: OutputDriver) -> list:
        if not output_driver.can_render(fmt):
            return []

        blocks = []
        for id, view in self.instances:
            block = dict(
                id=id,
                title=view.title or "",
                description=view.description,
                cols=view.cols,
                blobs=view.blobs,
                tags=[],
            )

            try:
                # Allow any extending package to optionally define its own
                # ./templates directory at the root module level.
                view_pkg_loader = PackageLoader(module_root(view.__module__))
                if isinstance(env.loader, ChoiceLoader):
                    # If we're already using a ChoiceLoader it's because there
                    # is a theme directory loader in place; ensure we always
                    # let the theme take priority.
                    loaders = env.loader.loaders.copy()
                    loaders.insert(1, view_pkg_loader)
                    new_loader = ChoiceLoader(loaders)
                else:
                    new_loader = ChoiceLoader([view_pkg_loader, env.loader])
                view_env = env.overlay(loader=new_loader)
                view_env.extend(view_id=id, fmt=fmt)
                view_env.filters["blob"] = self._blob_filter(output_driver)

                output = view.render(view_env, fmt=fmt)
                if not isinstance(output, str):
                    raise ViewException(("The view did not render a valid string"))

                block.update(output=output)
            except Exception as exc:
                self.log.error(
                    (f"Error rendering {self.type_noun} {id} ({fmt}): {exc}")
                )
                self.log.debug(traceback.format_exc())
                block.update(output=f"Error rendering {id}", tags=["error"])

            blocks.append(block)

        return blocks

    @property
    def blobs(self):
        _blobs = []
        for id, view in self.instances:
            _blobs.extend(view.blobs)
        return _blobs
