# TFSec

Azure YAML

```yaml
trigger: none
pr: none

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: QualityCheckStage
  displayName: Quality Check Stage
  jobs:
    - job: TFSecJob
      displayName: Run TFSec Scan
      steps:
      # TFSec uses static analysis of Terraform templates to spot potential security issues, and 
      # checks for violations of AWS, Azure and GCP security best practice recommendations.
      # NOTE: To disable a specific check from analysis, include it in the command-line as 
      # follows: -e GEN001,GCP001,GCP002
      # Documentation: https://github.com/tfsec/tfsec
      - bash: |
          mkdir TFSecReport

          docker pull aquasec/tfsec:latest

          docker run \
            --rm \
            --volume "$(System.DefaultWorkingDirectory)/Infrastructure-Source-Code/terraform:/src" \
            aquasec/tfsec \
              /src \
              --format JUnit > $(System.DefaultWorkingDirectory)/TFSecReport/TFSec-Report.xml

          docker run \
            --rm \
            --volume "$(System.DefaultWorkingDirectory)/Infrastructure-Source-Code/terraform:/src" \
            aquasec/tfsec \
              /src
        displayName: TFSec Static Code Analysis
        name: TFSecScan
        condition: always()

      # Publish the TFSec report as an artifact to Azure Pipelines
      - task: PublishBuildArtifacts@1
        displayName: 'Publish Artifact: TFSec Report'
        condition: succeededOrFailed()
        inputs:
          PathtoPublish: '$(System.DefaultWorkingDirectory)/TFSecReport'
          ArtifactName: TFSecReport

      # Publish the results of the TFSec analysis as Test Results to the pipeline
      - task: PublishTestResults@2
        displayName: Publish TFSecReport Test Results
        condition: succeededOrFailed()
        inputs:
          testResultsFormat: 'JUnit' # Options JUnit, NUnit, VSTest, xUnit, cTest
          testResultsFiles: '**/*TFSec-Report.xml'
          searchFolder: '$(System.DefaultWorkingDirectory)/TFSecReport'
          testRunTitle: TFSecScan(via Docker Image)
          mergeTestResults: false
          failTaskOnFailedTests: false
          publishRunAttachments: true

      # Clean up any of the containers / images that were used for quality checks
      - bash: |
          docker rmi "aquasec/tfsec:latest" -f | true
        displayName: 'Remove Terraform Quality Check Docker Images'
        condition: always()

      # IMPORTANT: The version of TFSec extension (as shown on the Visual Studio Marketplace: https://marketplace.visualstudio.com/items?itemName=AquaSecurityOfficial.tfsec-official), 
        # is not the correct version to reference/use.
        # Instead, please check the AquaSec TFSec Releases page: https://github.com/aquasecurity/tfsec/releases/
        # Also, you CANNOT use "latest" as the version number, as the extension will fail to install.
      - task: tfsec@1
        displayName: TFSecScan (via Extension)
        condition: always()
        inputs:
          debug: true
          version: v1.28.1
          # args: --workspace my-workspace --config-file ./tfsec.yml
          dir: $(System.DefaultWorkingDirectory)/Infrastructure-Source-Code/terraform
          publishTestResults: true
```plaintext

GitHub Workflow

```yaml
name: INFRA - IaC - TFSec

on:
  workflow_dispatch:

jobs:
  tfsec:
    name: TFSec
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      
      - name: Run TFSec scan
        uses: tfsec/tfsec-sarif-action@master
        with:
          sarif_file: tfsec.sarif    
          working_directory: ./Infrastructure-Source-Code/terraform/azure      

      - name: Upload SARIF file
        uses: github/codeql-action/upload-sarif@v2
        with:
          # Path to SARIF file relative to the root of the repository
          sarif_file: tfsec.sarif
```plaintext
