from core.exceptions import MISError


class ModuleProxyError(MISError):
    pass


class InstanceInvalid(ModuleProxyError):
    pass


class ProxyCheckError(ModuleProxyError):
    pass