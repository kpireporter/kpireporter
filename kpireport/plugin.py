import logging
import stevedore


class PluginManager:

    namespace = None
    exc_class = Exception
    type_noun = "plugin"

    def __init__(self, report, config, extension_manager=None):
        self.log = logging.getLogger(__name__)
        self.report = report

        if not self.namespace:
            self.namespace = f"kpireport.{self.type_noun}"

        # Allowing overriding the extension manager is useful for testing
        if extension_manager:
            self._mgr = extension_manager
        else:

            def on_load_failure(manager, entrypoint, exception):
                msg = exception
                if entrypoint.extras:
                    msg = (
                        f"Ensure the [{','.join(entrypoint.extras)}] "
                        "extras are installed if using this plugin."
                    )
                self.log.warn(f"Could not load plugin '{entrypoint.name}': {msg}")

            self._mgr = stevedore.ExtensionManager(
                namespace=self.namespace,
                invoke_on_load=False,
                on_load_failure_callback=on_load_failure,
                verify_requirements=True,
            )
            loaded_names = [e.name for e in self._mgr.extensions]
            self.log.info(f"Loaded {self.type_noun} plugins: {loaded_names}")

        self._instances = {}
        for id, conf in config.items():
            try:
                self._instances[id] = self.create_instance(id, conf)
                self.log.info(f"Initialized {self.type_noun} {id}")
            except Exception as exc:
                raise self.exc_class(f"Failed to load {self.type_noun} {id}") from exc

    @property
    def instances(self):
        return self._instances.items()

    def get_instance(self, id: str) -> any:
        if id not in self._instances:
            raise self.exc_class(
                (f"Could not find {self.type_noun} {id}; is it loaded?")
            )

        return self._instances[id]

    def call_instance(self, id: str, method: str, *args, **kwargs) -> any:
        instance = self.get_instance(id)
        fn = getattr(instance, method)

        if not callable(fn):
            raise self.exc_class((f"No such method {method} for {self.type_noun} {id}"))

        return fn(*args, **kwargs)

    def create_instance(self, id: str, config: dict) -> any:
        plugin = config.get("plugin")

        if not plugin:
            raise ValueError(
                (f"Each {self.type_noun} must define a 'plugin' attribute")
            )

        if plugin not in self._mgr:
            raise ValueError(f"Plugin {plugin} not loaded")

        plugin_kwargs = config.get("args", {})
        if not isinstance(plugin_kwargs, dict):
            raise ValueError(
                (f"Malformed plugin arguments: expected dict, " f"got {plugin_kwargs}")
            )

        plugin_kwargs.setdefault("id", id)

        return self.plugin_factory(self._mgr[plugin].plugin, plugin_kwargs, config)

    def plugin_factory(self, Plugin, plugin_kwargs, config):
        return Plugin(self.report, **plugin_kwargs)
