import inspect
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from jinja2 import ChoiceLoader, Environment, PackageLoader, pass_eval_context

from kpireport.datasource import DatasourceManager
from kpireport.output import OutputDriver
from kpireport.plugin import PluginManager
from kpireport.utils import module_root

if TYPE_CHECKING:
    from typing import List, Optional

    from kpireport.report import Report


class ViewException(Exception):
    pass


@dataclass
class Block:
    id: str
    title: str
    description: str
    cols: int
    blobs: "List[Blob]"
    tags: "List[str]"


@dataclass
class Blob:
    id: str
    content: str
    mime_type: "Optional[str]"
    title: "Optional[str]"


def make_render_env(
    env: "Environment", view: "View", output_driver: "OutputDriver", fmt: str
):
    """Create a Jinja environment for rendering the view.

    The environment is specific to the view, output driver, and output format, and
    should only be used for that combination of entities. As such, it is best
    to create this environment just before rendering the view.
    """
    # Allow any extending package to optionally define its own
    # ./templates directory at the root module level. To do this, we
    # inspect the current View class and find all modules in its inheritance
    # tree up until the base View class. We will search each one in order,
    # from the concrete class up through each base class, until we get to
    # the root.
    mod_tree = [c.__module__ for c in inspect.getmro(view.__class__)]
    view_pkg_loaders = []

    # Ignore base clases higher than this module.
    for mod in mod_tree[: mod_tree.index("kpireport.view") + 1]:
        try:
            view_pkg_loaders.append(PackageLoader(module_root(mod)))
        except ValueError:
            # The module has no "templates" folder; skip it.
            pass

    if isinstance(env.loader, ChoiceLoader):
        # If we're already using a ChoiceLoader it's because there
        # is a theme directory loader in place; ensure we always
        # let the theme take priority.
        loaders = env.loader.loaders.copy()
        loaders = loaders[:1] + view_pkg_loaders + loaders[1:]
        new_loader = ChoiceLoader(loaders)
    else:
        new_loader = ChoiceLoader(view_pkg_loaders + [env.loader])

    view_env = env.overlay(loader=new_loader)

    @pass_eval_context
    def render_blob(eval_ctx, blob_id):
        fmt = eval_ctx.environment.fmt

        blob = view.get_blob(blob_id)
        if not blob:
            raise ViewException(
                (
                    f"Missing content for blob '{blob_id}'. Make sure the "
                    "blob was added before rendering the View template"
                )
            )

        return output_driver.render_blob_inline(blob, fmt)

    view_env.filters["blob"] = render_blob
    view_env.fmt = fmt

    return view_env


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
            self.cols = int(kwargs.pop("cols"))
        else:
            self.cols = report.theme.num_columns

        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    def supports(self, fmt) -> bool:
        return callable(getattr(self, f"render_{fmt}", None))

    def render(self, env: Environment) -> str:
        fmt = getattr(env, "fmt")
        assert fmt is not None

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

    def get_blob(self, id) -> "Blob":
        return self._blobs.get(id)

    @property
    def blobs(self) -> "List[Blob]":
        return self._blobs.values()


class ViewManager(PluginManager[View]):

    namespace = "kpireport.view"
    type_noun = "view"
    exc_class = ViewException

    def __init__(self, datasource_manager, report, config, extension_manager=None):
        self.datasource_manager = datasource_manager
        super(ViewManager, self).__init__(report, config, extension_manager)

    def plugin_factory(self, config, plugin_class, plugin_kwargs) -> "View":
        for attr in ["title", "description", "cols"]:
            value = config.get(attr)
            if value:
                plugin_kwargs.setdefault(attr, value)

        return plugin_class(self.report, self.datasource_manager, **plugin_kwargs)

    def render(self, env: Environment, fmt: str, output_driver: OutputDriver) -> "List":
        if not output_driver.can_render(fmt):
            return []

        blocks = []
        for id, view in self.instances:
            block = Block(
                id=id,
                title=view.title or "",
                description=view.description,
                cols=view.cols,
                blobs=view.blobs,
                tags=[],
            )

            try:
                output = view.render(make_render_env(env, view, output_driver, fmt))
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
    def blobs(self) -> "List":
        _blobs = []
        for id, view in self.instances:
            _blobs.extend(view.blobs)
        return _blobs
