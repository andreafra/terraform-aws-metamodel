from pprint import pprint
from tfmc.loader import load_tf_project
from tfmc.schema_gen import generate_schema

schema = generate_schema()

project = load_tf_project('aws_ec2_ebs_docker_host')

pprint(project['resource'])