"""
For some reason, people at Terraform thought it'd be a great idea
to include a custom scripting language inside their spec.
It's not particularly quick to parse either.
You can view documentation at:
https://github.com/hashicorp/hcl/blob/main/hclsyntax/spec.md#template-expressions

For the moment, the best thing to do is to implement a rough parser to resolve
simple template string such as:
-   "${var.instance_zone}" -> Lookup in the parsed variables
-   "${local.availability_zone}" -> Lookup in the parsed locals
-   "${aws_security_group.this.id}" -> Lookup in the resources
"""

import re

def parse_template_string(input, model):
    if not isinstance(input, str):
        return input

    lookup_value_re = r'\${(\w*)\.(\w*)}'
    lookup_resource_re = r'\${(\w*)\.(\w*)\.(\w*)}'
    lookup_data_re = r'\${data\.(\w*)\.(\w*)\.(\w*)}'
    
    if m := re.match(lookup_value_re, input):
        src = m.group(1)
        id = m.group(2)
        match src:
            case 'var': 
                return model['variable'][id]
            case 'local': 
                return model['locals'][id]
    elif m := re.match(lookup_resource_re, input):
        cat = m.group(1)
        id = m.group(2)
        prop = m.group(3)
        if prop == 'id':
            return f'{cat}::{id}'
        else:
            print("TODO: Add support (and figure out) for resource attributes that are not 'id'.")
    elif m := re.match(lookup_data_re, input):
        cat = m.group(1)
        id = m.group(2)
        prop = m.group(3)
        if prop == 'id':
            return model['data'][cat][id]
        else:
            print("TODO: Add support (and figure out) for data attributes that are not 'id'.")
    else:
        return input