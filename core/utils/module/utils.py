from loguru import logger
import importlib
import sys

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pydantic import ValidationError

from const import MODULES_DIR
from core.db.models import Module
from core.dependencies.variable_service import get_variable_service
from core.schemas.module import ModuleManifest, ModuleDependency
from core.utils.app_context import AppContext
from libs.eventory import Eventory


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


def module_dependency_check(module_manifest: ModuleManifest, all_manifests: dict[str, ModuleManifest]) -> bool:
    """Checks is all dependencies has correct version"""
    if module_manifest is None:
        logger.warning(f"Manifest is missing, skip dependency check!")
        return False

    for dependency in module_manifest.dependencies:
        if all_manifests[dependency.module] is None:
            logger.warning(f"Manifest for module {dependency.module} is missing, "
                           f"skip dependency check for current module {module_manifest.name}!")
            return False

        is_valid_dependency = check_version_dependency(
            current_version=all_manifests[dependency.module].version,
            dependency_version=dependency.version,
        )
        if not is_valid_dependency:
            logger.warning(f"[{module_manifest.name}] Version dependency error! "
                           f"Dependency module '{dependency.module}' required '{dependency.version}'")
            return False
    return True


def manifests_sort_by_dependency(manifests: dict[str, ModuleManifest]) -> dict[str, ModuleManifest]:
    """Sort apps by their dependencies on other apps"""
    dependency_graph: dict[str, list[ModuleDependency]] = {}

    for module_name, manifest in manifests.items():
        dependency_graph[module_name] = manifest.dependencies

    sorted_manifests: dict[str, ModuleManifest] = {}
    for module_name in topological_sort(dependency_graph):
        manifest = manifests.get(module_name)
        sorted_manifests[module_name] = manifest
    return sorted_manifests


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
            visit(dependency.module)
        result.append(node_item)  # Add the current node to the result

    for node in graph:  # Start sorting from each node
        visit(node)

    return result


def check_version_dependency(current_version: str, dependency_version: str):
    """Check version dependency by packaging"""
    version = Version(current_version)
    dependency = SpecifierSet(dependency_version)
    return dependency.contains(version)


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


def read_module_manifest(module_name: str) -> ModuleManifest | None:
    with open(MODULES_DIR / module_name / 'manifest.json', 'r') as f:
        manifest_json = f.read()

    try:
        return ModuleManifest.model_validate_json(manifest_json)
    except ValidationError as error:
        logger.error(f"[{module_name}] Invalid manifest.json content! {error}")
        return None


async def get_app_context(app: Module, user=None, team=None):
    variable_service = get_variable_service()
    return AppContext(
        user=user,
        team=team,
        variables=await variable_service.make_variable_set(user=user, team=await user.team if user else None, app=app),
        app_name=app.name,
        routing_keys=await Eventory.make_routing_keys_set(app=app)
    )
