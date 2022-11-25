import importlib
import os
import pkgutil

from price_tracker.shop import Shop

pkg_dir = os.path.dirname(__file__)
for (module_loader, name, _) in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)

    all_my_base_classes = [cls for cls in Shop.__subclasses__()]
