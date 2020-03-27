from abc import ABC, abstractmethod
from jinja2 import Environment, ChoiceLoader, PackageLoader, Markup

from reportcard.datasource import DatasourceManager
from reportcard.plugin import PluginManager


class ViewException(Exception):
    pass


class View(ABC):

    id: str = None
    title: str = None

    def __init__(self, report, datasources: DatasourceManager, **kwargs):
        self.report = report
        self.datasources = datasources

        if "id" in kwargs:
            self.id = kwargs.pop("id")
        if "title" in kwargs:
            self.title = kwargs.pop("title")

        self._blobs = {}

        def module_root(module_str):
            return module_str.split(".")[0]

        # Allow any extending package to optionally define its own ./templates
        # directory at the root module level.
        loader = ChoiceLoader([
            PackageLoader(module_root(self.__module__)),
            PackageLoader(module_root(View.__module__))
        ])
        self.j2 = Environment(
            loader=loader,
            autoescape=True
        )
        self.j2.filters["blob"] = self.render_blob

        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

    def add_blob(self, name, blob):
        self._blobs[name] = blob

    @property
    def blobs(self) -> dict:
        return self._blobs

    def render_blob(self, name) -> Markup:
        if name not in self.blobs:
            raise ValueError(f"Could not find blob {name}")

        return Markup(f"""<img src="{self.id}/{name}" />""")


class ViewManager(PluginManager):

    namespace = "reportcard.view"
    type_noun = "view"
    exc_class = ViewException

    def __init__(self, datasource_manager, report, config,
                 extension_manager=None):
        self.datasource_manager = datasource_manager
        super(ViewManager, self).__init__(report, config, extension_manager)

    def plugin_factory(self, Plugin, plugin_kwargs):
        return Plugin(self.report, self.datasource_manager, **plugin_kwargs)

    def render(self) -> list:
        blocks = []
        for id in self.instances():
            try:
                blocks.append(dict(
                    id=id,
                    title=self.get_instance_attr(id, "title"),
                    output=self.call_instance(id, "render")
                ))
            except ViewException as exc:
                self.log.error((
                    f"Error rendering {self.type_noun} {id}: {exc}"))
                blocks.append(dict(
                    title=f"Error rendering {id}",
                    output=None
                ))
        return blocks
