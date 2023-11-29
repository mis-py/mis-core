from loguru import logger
import importlib
import sys

from services.modules.utils.module_dependency import ModuleDependency


def import_module(app_name: str, package: str = 'modules'):
    logger.debug(f'[ModuleService] Importing {package}.{app_name}')
    try:
        new_module = importlib.import_module(f"{package}.{app_name}")
    except Exception as e:
        logger.error(f'[ModuleService] Not found module in {package}.{app_name} or got exception "{e}"')
        logger.exception(e)
        return None

    logger.debug(f"[ModuleService] Successfully imported from {package}.{app_name}")

    return new_module


def unload_module(app_name: str, package: str = 'modules'):
    for module in list(filter(lambda m: m.startswith(f'{package}.{app_name}'), sys.modules)):
        del sys.modules[module]


def module_dependency_check(module, loaded_apps):
    # TODO currently not work
    if not set(module.dependencies.keys()).issubset(set(loaded_apps.keys())):
        logger.warning(f"[{module.name}] Dependency modules {list(module.dependencies.keys())} not loaded, please add them first!")
        return False

    for dependency_module_name, dependency_info in module.dependencies.items():
        dependency_module = loaded_apps[dependency_module_name]
        min_version = dependency_info["min_version"]
        max_version = dependency_info["max_version"]
        if not version_check(dependency_module.version, min_version, max_version):
            logger.warning(f"[{module.name}] Dependency module '{dependency_module_name}' "
                           f"version='{dependency_module.version}' "
                           f"but need {dependency_info}")
            return False
    return True


def apps_sort_by_dependency(apps: list['App']) -> list['App']:
    """Sort apps by their dependencies on other apps"""
    dependency_graph: dict[str, list[ModuleDependency]] = {}
    apps_dict: dict[str: 'App'] = {}

    for app in apps:
        # import can return None
        if app is None:
            continue

        module = app.module

        dependency_graph[module.name] = module.dependencies
        apps_dict[module.name] = module

    result: list['App'] = []
    for app_name in topological_sort(dependency_graph):
        app = apps_dict.get(app_name)
        result.append(app)
    return result


def topological_sort(graph: dict[str, list[ModuleDependency]]):
    """
    Sort by dependency

    Example:
    graph:
    {
        'statabot': [],
        'auto_admin': ['proxy'],
        'binom_companion': ['proxy'],
        'proxy': [],
    }
    result: ['statabot', 'proxy', 'auto_admin', 'binom_companion']
    """

    result = []  # List to store the sorted nodes
    visited = set()  # Set to keep track of visited nodes

    def visit(node_item):
        if node_item in visited:
            return
        visited.add(node_item)
        for dependency in graph.get(node_item, []):  # Visit dependencies
            visit(dependency.module_name)
        result.append(node_item)  # Add the current node to the result

    for node in graph:  # Start sorting from each node
        visit(node)

    return result


def version_check(version: str, min_version: str, max_version: str):
    # function to compare versions in string format (e.g., "1.0.4")
    version_parts = tuple(map(int, version.split('.')))
    min_version_parts = tuple(map(int, min_version.split('.')))
    max_version_parts = tuple(map(int, max_version.split('.')))
    if min_version_parts <= version_parts <= max_version_parts:
        return True
    return False


def _try_clone(self, url, branch, path):
    # try:
    #     return Repo.clone_from(url, branch=branch, to_path=path)
    # except GitCommandError as e:
    #     logger.error(f'GIT ERROR: {e.stderr}')
    #     logger.error(f'ON COMMAND: {" ".join(e.command)}')
    logger.error(f'GIT NOT IMPLEMENTED')


def _patch_with_token(self, git_url):
    # return git_url.replace('/git.', f'/{core_settings.GIT_API_TOKEN}@git.')
    logger.error(f'GIT NOT IMPLEMENTED')


def download_app(self, url: str, branch: str):
    # app_name = urllib3.util.parse_url(url).path.replace('.git', '').split('/')[-1]
    # app_path = APPS_DIR / app_name
    #
    # self._try_clone(
    #     self._patch_with_token(url),
    #     branch,
    #     app_path
    # )
    #
    # if 'frontend' in os.listdir(app_path):
    #     shutil.copy(app_path / 'frontend', FRONTEND_DIR / app_name)
    #
    # return app_name
    logger.error(f'GIT NOT IMPLEMENTED')
