from core.exceptions.exceptions import MISError


class ModuleBinomCompanionError(MISError):
    pass


class ProxyDomainCheckError(ModuleBinomCompanionError):
    pass


class NoProxiesError(ModuleBinomCompanionError):
    pass
