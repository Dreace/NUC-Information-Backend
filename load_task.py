import importlib
import logging
import os
import re
import traceback


def load_task(module_name: str) -> bool:
    """
    Load a module as a plugin.

    :param module_name: name of module to import
    :return: successful or not
    """
    try:
        importlib.import_module(module_name)
        logging.info("加载 %s" % module_name)
        return True
    except:
        logging.error(traceback.format_exc())
        return False


def load_tasks(plugin_dir: str, module_prefix: str):
    """
    Find all non-hidden plugins or packages in a given directory,
    and import them with the given module prefix.

    :param plugin_dir: plugin directory to search
    :param module_prefix: module prefix used while importing
    :return: number of plugins successfully loaded
    """
    cnt = 0
    for name in os.listdir(plugin_dir):
        path = os.path.join(plugin_dir, name)
        if os.path.isfile(path) and \
                (name.startswith('_') or not name.endswith('.py')):
            continue
        if os.path.isdir(path) and \
                (name.startswith('_') or not os.path.exists(
                    os.path.join(path, '__init__.py'))):
            continue

        m = re.match(r'([_A-Z0-9a-z]+)(.py)?', name)
        if not m:
            continue

        load_task(f'{module_prefix}.{m.group(1)}')
        cnt += 1
    logging.info("成功加载 %s 个任务" % cnt)
