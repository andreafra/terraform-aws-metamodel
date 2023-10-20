# Docs

This project aims to replicate what was done for the [PIACERE DOML Model Checker](https://github.com/andreafra/piacere-model-checker) but for AWS on Terraform.

## Idea

We don't really have a metamodel (i.e.: ) of the [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest), but we can generate a schema using the CLI with `terraform provider schema -json`. This schema describes all the properties of all the supported resources, except the fact that it does not explicit relationships between them. Lucky for us, the written [docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) actually provide that information, and even better, in most cases we can infer it by simply manipulating the strings.

For example: the property `subnet_id` should refer to the `aws_subnet` resource.

- There might be some exceptions to be fixed manually.
- We can also assume by default a Zero-to-Many relationship to simplify things, in order to not have to infer plurals.

The schema is then mapped to another schema provided with properties describing the target 'class' of the relationship.