import yaml
import os
import boto3
import botocore
import re
import inflection
from copy import copy
from .result_classes.factory import factory as result_classes_factory
import json
import backoff
from botocore.exceptions import (
    ConnectionClosedError,
    EndpointConnectionError,
    HTTPClientError,
    ReadTimeoutError,
    ProxyConnectionError,
    ConnectTimeoutError,
    SSLError,
)


class Service:
    service_name_map = {
        "AutoScalingPlans": "autoscaling-plans",
        "ApplicationAutoScaling": "application-autoscaling",
        "ApplicationInsights": "application-insights",
        "CognitoIdentity": "cognito-identity",
    }

    def __init__(self, config, region_name, output):
        self.config = config
        self.region_name = region_name
        self.output = output

    @property
    def client(self):
        if not hasattr(self, "_client"):
            self._client = boto3.client(self.service_name, region_name=self.region_name)
        return self._client

    @property
    def service_name(self):
        if not hasattr(self, "_service_name"):
            if self.config["service"] in self.service_name_map:
                self._service_name = self.service_name_map[self.config["service"]]
            else:
                self._service_name = self.config["service"].lower()
        return self._service_name

    @property
    def method_name(self):
        return inflection.underscore(self.config["api"])

    def call_client_method(self):
        try:
            if hasattr(self.client, self.method_name):
                return self._call_client_method()
            else:
                self.output.echo(
                    self.output.style(
                        "%s does not have method %s"
                        % (self.config["service"], self.method_name),
                        fg="red",
                    ),
                )
        except (
            ConnectionClosedError,
            EndpointConnectionError,
            HTTPClientError,
            ReadTimeoutError,
            ProxyConnectionError,
            ConnectTimeoutError,
            SSLError,
        ) as Exp:
            self.output.echo(self.output.style(str(Exp), fg="red"))
        return {}

    @backoff.on_exception(
        backoff.expo,
        (
            ConnectionClosedError,
            EndpointConnectionError,
            HTTPClientError,
            ReadTimeoutError,
            ProxyConnectionError,
            ConnectTimeoutError,
            SSLError,
        ),
        max_time=20,
    )
    def _call_client_method(self):
        callback = getattr(self.client, self.method_name)

        if "params" in self.config:
            params = self.config["params"]
        else:
            params = {}
        try:
            result = callback(**params)
            result_obj = result_classes_factory(
                config=self.config,
                callback=self.config["api"],
                result=result,
                output=self.output,
            )
        except botocore.exceptions.EndpointConnectionError:
            self.output.echo(
                self.output.style(
                    "Failed to connect to endpoint for %s in region %s"
                    % (self.config["service"], self.region_name),
                    fg="red",
                )
            )
            return {}
        return result_obj

    def is_available_in(self):
        if not hasattr(self.client, "describe_availability_zones"):
            return True
        if not hasattr(self, "available_in"):
            self.available_in = list(
                set(
                    [
                        zone["RegionName"]
                        for zone in self.client.describe_availability_zones()[
                            "AvailabilityZones"
                        ]
                        if zone["State"] == "available"
                    ]
                )
            )
        return self.region_name in self.available_in

    def get_inventory(self):

        if (
            self.is_available_in()
            and (
                "skip_regions" not in self.config
                or self.region_name not in self.config["skip_regions"]
            )
            and (
                "only_regions" not in self.config
                or self.region_name in self.config["only_regions"]
            )
        ):
            try:
                params = self.config["params"] if "params" in self.config else {}
                self.output.echo(
                    self.output.style(
                        "Checking service %s API %s region %s params(%s)"
                        % (
                            self.config["service"],
                            self.config["api"],
                            self.region_name,
                            json.dumps(params),
                        ),
                        fg="green",
                    )
                )
                return self.call_client_method()
            except botocore.exceptions.ClientError as identifier:
                pass
        return {}


class Inventory:
    def __init__(self, output_file, output, config=None):
        self.output = output
        if config:
            self._config = config
        else:
            self._config = yaml.load(
                open(os.path.dirname(__file__) + "/default_config.yaml"),
                Loader=yaml.Loader,
            )
        self.output_file = output_file

    @property
    def config(self):
        return self._config

    def get_inventory(self):
        if not hasattr(self, "inventory"):
            self.inventory = {region: {} for region in self.config["regions"]}
        for item in self._config["services"]:
            # self._config["regions"]
            key = "%s_%s" % (item["service"], item["api"])
            for region in self.config["regions"]:
                service = Service(item, region, output=self.output)
                inventory = service.get_inventory()
                self.inventory[region][key] = [
                    value for value in inventory if value is not None
                ]
                if len(self.inventory[region][key]) == 0:
                    del self.inventory[region][key]
        with open(self.output_file, "w") as output_file:
            dumped = yaml.dump(self.inventory, output_file, default_flow_style=False)
