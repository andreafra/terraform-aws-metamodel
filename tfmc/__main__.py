from pprint import pprint
from tfmc.cache import cache
from tfmc.class_transformer import transform
from tfmc.loader import load_tf_project
from tfmc.schema_gen import generate_schema

schema = cache('aws-schema-mm', lambda: generate_schema())

project = load_tf_project('aws_ec2_ebs_docker_host')

data = project['data'] # do we need this?
resources = project['resource']
variables = project['variable'] # do we need this?
locals = project['locals'] # do we need this?
output = project['output'] # do we need this?

im_resources = []

for category, items in resources.items():
    if category in schema:
        schema_data = schema[category]
        for item_id, item in items.items():
            im_resources.append(transform(category, item_id, item, schema_data))
    else:
        print(f'Category \'{category}\' is unsupported by the TF Schema.')

pprint(im_resources)