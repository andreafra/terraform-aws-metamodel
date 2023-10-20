from importlib.resources import files
import os
import hcl2
import assets.examples as examples



def _parse_bulk_tf(project_dir):
    # Get references to required files
    TF_SOURCE_DIR = files(examples) / project_dir
    assert TF_SOURCE_DIR.is_dir()
    # A terraform project is just a collection of files in the same folder.
    # We need to import them one by one because the HCL2 library won't do that.
    # Alternatively, we could append the contents of each in the same file,
    # and parse the file once.
    sources = [f for f in os.listdir(TF_SOURCE_DIR) if f.endswith('.tf')]

    print(f"Found the following TF sources: {", ".join(sources)}",)

    # Load and merge together the resources
    tf_project = {}
    for source in sources:
        with open(TF_SOURCE_DIR / source, "r") as f:
            tf_fragment = hcl2.load(f)
            
            for k, v in tf_fragment.items():
                if tf_project.get(k):
                    tf_project[k] += v
                else:
                    tf_project[k] = v

    return tf_project

type TFProjectSource = dict[str, list[dict[str, dict[str, dict]]]]
#                           pkg            type      id   props
type TFProjectTarget = dict[str, dict[str, dict[str, dict]]]
#                           pkg       type      id   props

def _normalize_tf(tf: TFProjectSource) -> TFProjectTarget:
    pkgs = {}
    for pkg, catlist in tf.items():
        pkgs[pkg] = {}
        for cat in catlist:
            for cat_id, elem in cat.items():
                if not pkgs[pkg].get(cat_id):
                    pkgs[pkg][cat_id] = {}
                if isinstance(elem, dict):
                    for name, props in elem.items():
                        pkgs[pkg][cat_id][name] = props
                else:
                    # Maybe handle these differently?
                    pkgs[pkg][cat_id] = elem
    return pkgs

def _handle_nested_blocks(resources):
    for _, category in resources.items():
        for id, props in category.items():
            print(id)
            for prop_k, prop_v in props.items():
                if isinstance(prop_v, list) and len(prop_v) > 0 and isinstance(prop_v[0], dict):
                    # In case we need to do something with it
                    print(prop_k)

def load_tf_project(project_dir):
    data = _parse_bulk_tf(project_dir)
    data = _normalize_tf(data)
    # _handle_nested_blocks(data['resource'])
    return data