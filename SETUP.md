# Setup
This project runs on Python 3.12.

## Requirements
1.  Install the following tools:

    - [`pyenv`](https://github.com/pyenv/pyenv#installation) to manage multiple Python installations (optional, but recommended)
    - [`terraform`](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) 
        to validate and generate the required schema for this tool

2.  Configure then a new Python environment with:
    ```bash
    pyenv virtualenv 3.11 tfmc-env-3.11
    ```

    If you've set up `pyenv` correctly, it should automatically enable/disable the virtual environment
    when entering/leaving the directory.

3.  Install the dependecies with:
    ```bash
    pip install -r requirements.txt
    ```
4.  Initialize Terraform by running:
    ```bash
    terraform init
    ```

5.  Generate the schema file in:
    ```bash
    terraform providers schema -json > assets/schemas/aws-schema.json
    ```
6.  Download some example projects and put them in the `assets/examples` folder. I'm testing with [this one](https://github.com/futurice/terraform-examples/tree/master/aws). 
