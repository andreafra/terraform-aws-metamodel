import argparse
import os
from pprint import pprint
from tfmc import solver
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

# Load the metamodel
# if args.nocache:
#     clear_cache()
schema = generate_schema()
# else:
#     schema = cache("aws-schema-mm", lambda: generate_schema())

# Load a file by folder name
# Path is /assets/examples/<name>
model = load_tf_model("aws_ec2_ebs_docker_host")

# resources are infrastructure object
resources = model["resources"]
# data are object defined outside of Terraform
data = model["data"]  # TODO: Should we really handle these?

variables = model["variable"]  # do we need this? probably are resolved by the parser
locals = model["locals"]  # do we need this? maybe
output = model["output"]  # do we need this? probably not

refs = transform_resources(resources, schema)

refs.gen_association_refs()

s = solver.init(refs)

print(s)
