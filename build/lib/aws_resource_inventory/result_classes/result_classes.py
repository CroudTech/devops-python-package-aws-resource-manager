from collections import UserDict
import jmespath


class ServiceResult(UserDict):
    def __init__(self, result, config, output):
        self.config = config
        self.output = output
        self.parseData(result)

    def parseData(self, result):
        try:
            items = jmespath.search(self.config["jmespath"], result)
            self.data = items if items is not None else []
        except jmespath.exceptions.JMESPathTypeError:
            self.data = []


class AwsInventoryItem(UserDict):
    def get_tags_dict(self, tags):
        return {tag["Key"]: tag["Value"] for tag in tags}


class Instance(AwsInventoryItem):
    def __init__(self, instance):
        self.data = {
            key: value for key, value in instance.items() if key in ["InstanceId"]
        }
        self.data["Tags"] = self.get_tags_dict(instance["Tags"])
        self.data["Name"] = (
            self.data["InstanceId"]
            if "Name" not in self.data["Tags"]
            else self.data["Tags"]["Name"]
        )
