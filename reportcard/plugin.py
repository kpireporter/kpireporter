import logging
import stevedore


class PluginManager:

    namespace = None
    exc_class = Exception
    type_noun = "plugin"

    def __init__(self, config, report=None, extension_manager=None):
        self.log = logging.getLogger(__name__)
        self.report = report

        if not self.namespace:
            self.namespace = f"reportcard.{self.type_noun}"

        # Allowing overriding the extension manager is useful for testing
        if extension_manager:
            self._mgr = extension_manager
        else:
            def on_load_failure(manager, entrypoint, exception):
                self.log.error(f"Failed to load {entrypoint}: {exception}")

            self._mgr = stevedore.ExtensionManager(
                namespace=self.namespace,
                invoke_on_load=False,
                on_load_failure_callback=on_load_failure,
            )

        self._instances = {}
        for name, conf in config.items():
            try:
                self._instances[name] = self.create_instance(conf)
                self.log.info(f"Initialized {self.type_noun} {name}")
            except Exception as exc:
                raise self.exc_class(
                    f"Failed to load {self.type_noun} {name}") from exc

    def instances(self):
        return self._instances.keys()

    def get_instance_attr(self, name: str, attr: str) -> any:
        if name not in self._instances:
            raise self.exc_class((
                f"Could not find {self.type_noun} {name}; is it loaded?"))

        plugin = self._instances[name]
        
        return getattr(plugin, attr)

    def call_instance(self, name: str, method: str, *args, **kwargs) -> any:
        fn = self.get_instance_attr(name, method)

        if not callable(fn):
            raise self.exc_class((
                f"No such method {method} for {self.type_noun} {name}"))

        return fn(*args, **kwargs)

    def create_instance(self, config: dict) -> any:
        plugin = config.get("plugin")

        if not plugin:
            raise ValueError((
                f"Each {self.type_noun} must define a 'plugin' attribute"))

        if plugin not in self._mgr:
            raise ValueError(f"Plugin {plugin} not loaded")

        plugin_kwargs = config.get("args", {})
        if not isinstance(plugin_kwargs, dict):
            raise ValueError((
                f"Malformed plugin arguments: expected dict, "
                f"got {plugin_kwargs}"))

        return self.plugin_factory(self._mgr[plugin].plugin, plugin_kwargs)

    def plugin_factory(self, plugin_ctor, plugin_kwargs):
        return plugin_ctor(**plugin_kwargs)
