import logging
import stevedore


class PluginManager:

    namespace = None
    exc_class = Exception
    type_noun = "plugin"

    def __init__(self, config, extension_manager=None):
        self.log = logging.getLogger(__name__)

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
                self._instances[name] = self._instantiate_plugin(conf)
                self.log.info(f"Initialized {self.type_noun} {name}")
            except Exception as exc:
                raise self.exc_class(
                    f"Failed to load {self.type_noun} {name}") from exc

    def call_instance(self, name, method, *args, **kwargs):
        if name not in self._instances:
            raise self.exc_class((
                f"Could not find {self.type_noun} {name}; is it loaded?"))

        plugin = self._instances[name]
        fn = getattr(plugin, method)

        if not callable(fn):
            raise self.exc_class((
                f"No such method {method} for {self.type_noun} {name}"))

        return fn(*args, **kwargs)

    def _instantiate_plugin(self, config):
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

        return self._mgr[plugin].plugin(**plugin_kwargs)
