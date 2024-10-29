# edp-deploy-orchestrator-action

This Action allow users of EDP Deploy (Formerly Runtimes) to deploy infrastructures with the *plan* step easilly.
This GitHub Action is designed to facilitate the deployment of infrastructure using a self-hosted runtime. It supports both AWS IAM roles and AWS access keys for authentication, and it orchestrates the deployment of infrastructure using Terraform.

### Requirements
To get the account keys (`CLIENT_ID`, `CLIENT_KEY` and `CLIENT_REALM`), please login using a **ADMIN** user on the [StackSpot Portal](https:#stackspot.com), and generate new keys at [Access Token](https:#stackspot.com/en/settings/access-token).

## Inputs

| Name                        | Description                                                                 | Required | Default                                  |
|-----------------------------|-----------------------------------------------------------------------------|----------|------------------------------------------|
| `level-log`                 | The runtime log level.                                                      | No       | `info`                                   |
| `tfstate-bucket-name`       | The bucket for runtime inventory.                                           | Yes      | N/A                                      |
| `tfstate-bucket-region`     | The region of the bucket for runtime inventory.                             | No       | `sa-east-1`                              |
| `iac-bucket-name`           | The bucket for storing IaC (Infrastructure as Code) files.                  | Yes      | N/A                                      |
| `iac-bucket-region`         | The region of the bucket for IaC files.                                     | No       | `sa-east-1`                              |
| `container-iac-version`     | The container version for IaC tasks.                                        | No       | `stackspot/runtime-job-iac:latest`       |
| `container-deploy-version`  | The container version for deployment tasks.                                 | No       | `stackspot/runtime-job-deploy:latest`    |
| `container-destroy-version` | The container version for destroy tasks.                                    | No       | `stackspot/runtime-job-destroy:latest`   |
| `container-unified-version` | The container version for unified tasks.                                    | No       | `stackspot/runtime-job-unified:latest`   |
| `dynamic-inputs`            | Dynamic inputs for the action.                                              | No       | `""`                                     |
| `workspace`                 | The slug of the workspace.                                                  | Yes      | N/A                                      |
| `environment`               | The environment for the deployment.                                         | Yes      | `""`                                     |
| `version`                   | The version of the deployment.                                              | Yes      | N/A                                      |
| `terraform-parallelism`     | The parallelism level for Terraform.                                        | No       | `10`                                     |
| `workdir`                   | The path to the directory where the `.stk` is located.                      | No       | `./`                                     |
| `checkout-branch`           | Whether or not to enable branch checkout.                                   | No       | `false`                                  |
| `repository-name`           | The name of the Git repository.                                             | Yes      | N/A                                      |
| `path-to-mount`             | The path to mount inside the provisioning Docker container.                 | Yes      | N/A                                      |
| `aws-iam-role`              | The AWS IAM role to use for deploying infrastructure.                       | No       | N/A                                      |
| `aws-iam-account-region`    | The AWS IAM account region.                                                 | No       | `sa-east-1`                              |
| `aws-access-key-id`         | The AWS access key ID for deploying infrastructure.                         | No       | N/A                                      |
| `aws-secret-access-key`     | The AWS secret access key for deploying infrastructure.                     | No       | N/A                                      |
| `aws-session-token`         | The AWS session token for deploying infrastructure.                         | No       | N/A                                      |
| `stk-client-id`             | The client identifier of the account.                                       | Yes      | N/A                                      |
| `stk-client-secret`         | The client secret of the account.                                           | Yes      | N/A                                      |
| `stk-realm`                 | The realm of the account.                                                   | Yes      | N/A                                      |
| `features-terraform-modules`| Terraform modules to be used.                                               | No       | N/A                                      |
| `tf-log-provider`           | The log level for Terraform (info, debug, warn, trace).                     | No       | N/A                                      |
| `base-path-output`          | The file name to save outputs.                                              | No       | `outputs.json`                           |
| `local-exec-enabled`        | Whether to allow execution of the `local-exec` command within Terraform.    | No       | `false`                                  |
| `verbose`                   | Whether to show extra logs during execution.                                | No       | `false`                                  |
| `open-api-path`             | The path to the OpenAPI/Swagger file within the repository.                 | No       | N/A                                      |

## Outputs

| Name           | Description               |
|----------------|---------------------------|
| `apply_tasks`  | Post-plan tasks.           |
| `run_id`       | The ID of the current run. |

## Usage

Here is an example of how to use this action in your GitHub workflow:

**NOTE: This action should NOT be used on its own, its supposed to be used along with [stack-spot/runtime-tasks-action](https:#github.com/stack-spot/runtime-tasks-action) and [stack-spot/runtime-cancel-run-action](https:#github.com/stack-spot/runtime-cancel-run-action) as the example below shows**

```yaml
name: Deploy Infrastructure

on:
  push:
    branches:
      - main

jobs:
  orquestrate_and_plan:
    runs-on: ubuntu-latest # Here you should use a runner that can access your cloud account
    outputs: 
        apply_tasks: ${{ steps.orquestration_and_plan.outputs.apply_tasks }}
        run_id: ${{ steps.orquestration_and_plan.outputs.run_id }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Deploy Infrastructure
        uses: stackspot/edp-deploy-orchestration-action@v1
        id: orquestration_and_plan
        with:
            tfstate-bucket-name: "my-tfstate-bucket"
            tfstate-bucket-region: sa-east-1
            iac-bucket-name: "my-iac-bucket"
            iac-bucket-region: sa-east-1
            workspace: "my-workspace"
            environment: "production"
            version: "v1.0.0"
            repository-name: ${{ github.event.repository.name }}
            path-to-mount: /home/runner/_work/${{ github.event.repository.name }}/${{ github.event.repository.name }}
            stk-client-id: ${{ secrets.STK_CLIENT_ID }}
            stk-client-secret: ${{ secrets.STK_CLIENT_SECRET }}
            stk-realm: ${{ secrets.STK_REALM }}
            aws-iam-role: ${{ secrets.AWS_ROLE_ARN }}
            aws-iam-account-region: sa-east-1

  plan-approve-and-apply:
    name: Deploy
    needs: [orquestrate_and_plan]
    runs-on: ubuntu-latest # Here you should use a runner that can access your cloud account
    environment: production # Here you set the environments that the user is supposed to aprrove the changes planned from orquestration step
    steps:
      - name: Service Provision
        id: run-task
        uses: stack-spot/runtime-tasks-action@stg
        if: needs.orquestrate_and_plan.outputs.run_id != ''
        with:
          RUN_ID: ${{ needs.orquestrate_and_plan.outputs.run_id }}
          TASK_LIST: ${{ needs.orquestrate_and_plan.outputs.apply_tasks }}
          REPOSITORY_NAME: ${{ github.event.repository.name }}
          PATH_TO_MOUNT: /home/runner/_work/${{ github.event.repository.name }}/${{ github.event.repository.name }}
          AWS_REGION: sa-east-1
          AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN }}
          FEATURES_TERRAFORM_MODULES: >-
              [
                  {
                    "sourceType": "gitHttps",
                    "path": "github.com/stack-spot",
                    "private":  true,
                    "app": "app",
                    "token": "token"
                  },
                  {
                    "sourceType": "terraformRegistry",
                    "path": "hashicorp/stack-spot", 
                    "private":  false
                  }
              ]
          CLIENT_ID: ${{ secrets.STK_CLIENT_ID }}
          CLIENT_KEY: ${{ secrets.STK_CLIENT_SECRET }}
          CLIENT_REALM: ${{ secrets.STK_REALM }}

  cancel: # in case something in your pipeline breaks, or someone cancels it mid deployment, its required to run this action in order to let Stackspot know that an error has ocurred and not block next deployments
    runs-on: ubuntu-latest # Here you should use a runner that can access your cloud account
    needs: [orquestrate_and_plan, plan-approve-and-apply]
    if: ${{ always() && (contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')) }} 
    steps:
      - name: Cancel run
        if: needs.orquestrate_and_plan.outputs.run_id != '' 
        id: run-cancel
        uses: stack-spot/runtime-cancel-run-action@stg
        with:
          CLIENT_ID: ${{ secrets.STK_CLIENT_ID }}
          CLIENT_KEY: ${{ secrets.STK_CLIENT_SECRET }}
          CLIENT_REALM: ${{ secrets.STK_REALM }}
          RUN_ID: ${{ needs.orquestrate_and_plan.outputs.run_id }}

```

### AWS Authentication
This action supports two methods of AWS authentication:

Using an AWS IAM Role: Provide the aws-iam-role input.
Using AWS Access Keys: Provide the aws-access-key-id, aws-secret-access-key, and aws-session-token inputs.
Note: You must provide either the IAM role or the access keys, but not both. If both are provided, the action will fail.

#### Example with AWS Access Keys

```yaml
- name: Deploy Infrastructure with AWS Access Keys
  uses: stackspot/edp-deploy-orchestration-action@v1
  with:
      # aws-iam-role: ${{ secrets.AWS_ROLE_ARN }}
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws-session-token: ${{ secrets.AWS_SESSION_TOKEN }}
      aws-iam-account-region: sa-east-1

``` 


### Complex Inputs

#### `checkout-branch`

When the input `checkout-branch` is used, within the IAC step of the tasks, the repository will be cloned within the `iac.zip` with the following structure, in case repository files are necessary within terraform. it works in tandem with `path_to_mount` input, which should point to your repository after checkout, the value we indicate using for `path_to_mount` is `/home/runner/_work/${{ github.event.repository.name }}/${{ github.event.repository.name }}`, so terraform has access to the files, but you can change this however you wish.

_**Note**: the contents of the branch input don't really matter, the branch cloned will be the branch used to dispatch the workflow as long as it is not empty_

```
├── main.tf
├── outputs.tf
├── repodir
│   ├── .git/
│   ├── .stk/
│   │   └── stk.yaml
│   ├── src/
│   ├── tests/
│   └── ... {repository-files}
└── variables.tf
└── ... {templates-deploy}
```

#### `dynamic-inputs`

When the input `dynamic-inputs` is used, the flags passes in these inputs will be added to every plugin applied as their input, and could be used by Jinja engine to modify the IaC file created

**e.g:**

`dynamic-inputs = --app_repository="https:#github.com/stack-spot/edp-deploy-orchestrator-action"`

_main.tf_
```jinja
{% if app_repository is defined %}
    resource_source  = {{ app_repository }}
{% else %}
    resource_source  = "default"
{% endif %}
```

#### `features-terraform-modules`

When `features-terraform-modules` is used, the application will allow the modules provided in this inputs to be executed. This is a security measurement to only allow trusted modules to be used.

It should follow this structure:

```yaml
features-terraform-modules: >-
    [
        {
            "sourceType": "gitHttps",
            "path": "github.com/stack-spot", # Allows all repositories on stack-spot org
            "private": true,
            "app": "app", # Substitute with appName
            "token": "token" # Substitute with github access token
        },
        {
            "sourceType": "terraformRegistry",
            "path": "hashicorp/stack-spot", # Allows all modules on stack-spot org
            "private": false
        }
    ]
```


### Error Handling
If both AWS IAM role and AWS access keys are provided, the action will fail with an error.

If neither AWS IAM role nor AWS access keys are provided, the action will fail with an error.

In case of a Deployment error, please look at [Stackspot EDP Portal](https:#app.stackspot.com/) at your workspace and application/shared infrastructure within the environment deployed and look at activities tab, there should be the error messages.


## License
This project is licensed under the MIT License.