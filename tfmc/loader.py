from importlib.resources import files
import json
import os
from pprint import pprint
import assets.examples as examples
from tfparse import load_from_path

def _normalize(raw_model):
    """ The parser (tfparse) now generates the UUID for each resource, as well as
        the links between resources.

        The input structure is as follows:
        dict[ # resource categories
            list[ # resources in that category
                dict { # the actual resource
                    - __tfmeta: contains details about the TF source file (USEFUL for outputs)
                    -   attributes that have a plain value are directly properties
                    -   attributes/associations that map to another object actually
                        are a dict:
                        - __name__: the resource name
                        - __ref__: the UUID
                        - __type__: the referenced target type
                        - __attribute(s)__: the source string
                }
            ]
        ]
    """

    model = {
        'resources': {},
        'data': {}
    }
    uuid_map = {}

    special_categories = [
        'locals',
        'output',
        'variable'
    ]

    for category, resources in raw_model.items():
        if category not in special_categories:
            for resource in resources:
                id = resource['__tfmeta']['path']
                type = resource['__tfmeta']['type']
                uuid = resource['id']
                uuid_map[uuid] = resource
                if type == 'resource':
                    model['resources'][id] = resource
                elif type == 'data':
                    model['data'][id] = resource

    # TODO: Might need parsing and/or adding their UUID to the map
    for sp in special_categories:
        model[sp] = raw_model[sp]

    return model



def load_tf_model(project_dir):
    TF_SOURCE_DIR = files(examples) / project_dir

    parsed = load_from_path(TF_SOURCE_DIR)

    model = _normalize(parsed)

    return model