import os
from pprint import pprint
from tfmc.cache import cache
from tfmc.class_transformer import transform
from tfmc.loader import load_tf_model
from tfmc.schema_gen import generate_schema

# Enable colored text in output
os.system('color')

# Load the metamodel
schema = cache('aws-schema-mm', lambda: generate_schema())

# Load a file by folder name
# Path is /assets/examples/<name>
model = load_tf_model('aws_ec2_ebs_docker_host')

resources = model['resources']
data = model['data']
variables = model['variable'] # do we need this?
locals = model['locals'] # do we need this?
output = model['output'] # do we need this?

im_resources = []

for category_and_id, props in resources.items():

    [category, id] = category_and_id.split('.')

    # just a double check to not get weird parsed stuff
    assert category == props.get('__tfmeta').get('label')

    # check if metamodel specify this category
    if category in schema:
        schema_data = schema[category]
        im_resources.append(transform(category, id, props, model, schema_data))
    else:
        print(f'Category \'{category}\' is unsupported by the TF Schema.')

for res in im_resources:
    print(res)

# TODO: Handle associations