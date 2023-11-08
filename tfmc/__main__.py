import argparse
import os
from pprint import pprint
from tfmc.cache import cache, clear_cache
from tfmc.resource_transformer import transform_resources
from tfmc.loader import load_tf_model
from tfmc.schema_gen import generate_schema

argparser = argparse.ArgumentParser("TFMC")
argparser.add_argument(
    "-nc",
    "--nocache",
    help="Skips cached files.",
    action=argparse.BooleanOptionalAction,
)

args = argparser.parse_args()

# Enable colored text in output
os.system("color")

# Load the metamodel
if args.nocache:
    clear_cache()
    schema = generate_schema()
else:
    schema = cache("aws-schema-mm", lambda: generate_schema())

# Load a file by folder name
# Path is /assets/examples/<name>
model = load_tf_model("aws_ec2_ebs_docker_host")

resources = model["resources"]

data = model["data"]
variables = model["variable"]  # do we need this?
locals = model["locals"]  # do we need this?
output = model["output"]  # do we need this?

refs = transform_resources(resources, schema)

for res in refs.im_resources.values():
    print(res)

# TODO: Handle associations
