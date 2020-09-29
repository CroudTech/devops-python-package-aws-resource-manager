import importlib

from . import result_classes


def factory(config, callback, result, output):
    class_name = "%s_%s" % (config["service"], callback)
    try:
        result_class = getattr(
            importlib.import_module(
                ".result_classes.result_classes", package="aws_resource_inventory"
            ),
            class_name,
        )
        return result_class(config=config, result=result, output=output)
    except AttributeError:
        return result_classes.ServiceResult(config=config, result=result, output=output)
