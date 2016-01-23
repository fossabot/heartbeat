import importlib


class ModuleLoader(object):

    """
    Dynamically loads modules at runtime for loading plugins.
    """

    def load_multiple(paths, full_classpath=False):
        """
        Loads multiple modules from a module path or a full classpath

        Params:
            Array paths: A list of paths to load
            Bool full_classpath: Whether the paths provided are a full classpath
        """
        modules = []
        for p in paths:
            modules.append(ModuleLoader.load_module(p, full_classpath))

        return modules

    def load(path, full_classpath=False):
        """
        Loads a single module from a path

        Params:
            String path: the path to load
            Bool full_classpath: Whether the path provided is a full classpath
        """
        if full_classpath:
            path = ".".join(path.split(".")[:-1])

        module = importlib.import_module(path)
        return module


class PluginRegistry(type):

    """
    Registry of loaded plugins. This is populated automatically
    when plugins are imported.

    This relies on a whitelist, populated from the configuration and
    will attempt to only import plugins that are configured.
    """

    plugins = {}
    whitelist = []

    def __init__(cls, name, bases, attrs):
        full_class = cls.__module__ + "." + name
        if name != 'Plugin' and full_class in PluginRegistry.whitelist:
            PluginRegistry.plugins[cls.__module__ + "." + name] = cls

    def filter_by_package(package):
        """
        Returns a list of plugins contained within a particular package

        Parameters:
            str package
        """

        filtered = {}

        for pkg, c in PluginRegistry.plugins.items():
            if pkg.startswith(package):
                filtered[pkg] = c

        return filtered

    def populate_whitelist(allowed_plugins):
        """
        Populates the plugin whitelist with a list of allowed plugins

        Parameters:
            Array[str] allowed_plugins
        """
        if PluginRegistry.whitelist == []:
            PluginRegistry.whitelist = allowed_plugins
        else:
            raise Exception("The PluginRegistry whitelist has already been configured")

    def populate_from_settings(settings=None):
        """
        Populates the plugin registry from the settings

        Paremeters:
            ConfigManager settings: defaults to None
        """
        if settings is None:
            settings = get_config_manager()

        if settings.heartbeat.plugins is None:
            return None

        PluginRegistry.populate_whitelist(settings.heartbeat.plugins)

        for p in settings.heartbeat.plugins:
            ModuleLoader.load(p, full_classpath=True)


class Plugin(object, metaclass=PluginRegistry):

    """
    The base heartbeat Plugin class that all plugins are
    required to inherit from. When inheriting classes are
    imported, they will automatically be registered with
    the PluginRegistry if they appear in the configuration.
    """

    def get_subscriptions(self):
        """
        Returns a dictionary of topics mapped to
        callbacks which heartbeat will set up.
        The default at this level is an empty
        dictionary.

        Returns:
            dict(Topic: Callback)
        """
        return {}

    def get_producers(self):
        """
        Returns a dictionary of producers and types
        (realtime and otherwise) that will produce
        Events that heartbeat will dispatch. The default
        at this level is an empty dictionary.

        Returns:
            dict(MonitorType: Callback)
        """
        return {}
