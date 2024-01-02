import argparse
from importlib.resources import files
import json
from pathlib import Path
from flask import Flask, render_template
from markupsafe import escape
from pprint import pprint
import assets.examples
import assets.templates
from tfmc import solver
from tfmc.cache import cache, clear_cache
from tfmc.resource_transformer import transform_resources
from tfmc.loader import load_tf_model
from tfmc.schema_gen import SchemaEncoder, decode_schema, generate_schema
from tfmc.visualizer import visualize

argparser = argparse.ArgumentParser("TFMC")
argparser.add_argument(
    "-cc",
    "--clearcache",
    help="Skips cached files.",
    action=argparse.BooleanOptionalAction,
)
argparser.add_argument(
    "-sws",
    "--skipwebserver",
    help="Doesn't use web server",
    action=argparse.BooleanOptionalAction,
)
argparser.add_argument(
    "-smm",
    "--summarize_mm",
    help="Produce a smaller graphical representation of the metamodel",
    action=argparse.BooleanOptionalAction,
)

args = argparser.parse_args()

# Load the metamodel
if args.clearcache:
    clear_cache()

schema = cache(
    "aws-schema-mm",
    lambda: SchemaEncoder().encode(generate_schema()),
    lambda x: decode_schema(json.loads(x)),
)


def validate_model(name: str):
    # Load a file by folder name
    # Path is /assets/examples/<name>
    model = load_tf_model(name)

    # resources are infrastructure object
    resources = model["resources"]
    # data are object defined outside of Terraform
    data = model["data"]  # TODO: Should we really handle these?

    variables = model[
        "variable"
    ]  # do we need this? probably are resolved by the parser
    locals = model["locals"]  # do we need this? maybe
    output = model["output"]  # do we need this? probably not

    refs = transform_resources(resources, schema)  # type: ignore

    refs.gen_association_refs()

    s = solver.init(refs)

    # outdir = Path(f".output/{name}")
    # outdir.mkdir(parents=True, exist_ok=True)

    # also save mermaid representation of MM and IM diagram in '.output' folder
    mm_diag, im_diag = visualize(refs, summarize_mm=args.summarize_mm)

    return mm_diag, im_diag


if not args.skipwebserver:
    # start html server to display output
    app = Flask(__name__, template_folder=files(assets.templates))  # type: ignore

    @app.route("/")
    def projects():
        _projects = [
            p.name
            for p in files(assets.examples).iterdir()
            if p.is_dir() and p.name != "__pycache__"
        ]
        return render_template("projects.html", projects=_projects)

    @app.route("/<tfproj>")
    def load_proj(tfproj):
        project_name = escape(tfproj)

        mm_diag, im_diag = validate_model(project_name)

        return render_template(
            "results.html", name=project_name, mm_diagram=mm_diag, im_diagram=im_diag
        )

    app.run()

else:
    validate_model("aws_ec2_ebs_docker_host")
