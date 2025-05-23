# Mend ( WhiteSource )

```yaml
# NOTE: Having issues with the new Mend site, and gaining access to my account.

trigger: none
pr: none

pool:
  vmImage: 'windows-latest'

variables:
- group: SecureVariables
- name: WhiteSource-ProductName
  value: DevSecOpsProduct
- name: WhiteSource-ProjectName
  value: DevSecOpsProject

stages:
- stage: QualityCheckStage
  displayName: Quality Check Stage
  jobs:
  - job: WhiteSourceJob
    displayName: Run Mend (WhiteSource) Scan
    steps:
    - task: DotNetCoreCLI@2
      displayName: .NET Restore
      inputs:
        command: "restore"
        projects: "**/*.csproj"
        # feedsToUse: "config"
        # nugetConfigPath: "nuget.config"
    
    - task: WhiteSource@21
      displayName: Run Mend (formerly WhiteSource) scan
      inputs:
        cwd: '$(System.DefaultWorkingDirectory)/Application-Source-Code'
        projectName: $(WhiteSource-ProjectName)

    # - task: CmdLine@2
    #   displayName: "Download WhiteSource Unified Agent"
    #   inputs:
    #     script: curl -LJO https://github.com/whitesource/unified-agent-distribution/releases/latest/download/wss-unified-agent.jar

    # - task: CmdLine@2
    #   displayName: "Run WhiteSource Unified Agent Scan"
    #   inputs:
    #     script: |
    #       java -jar wss-unified-agent.jar -c whitesource-fs-agent.config -product $(WhiteSource-ProductName) -project $(WhiteSource-ProjectName) -apiKey $(WhiteSource-APIKey)
    #       exit $?


    # - script: | 
    #     curl -LJO https://github.com/whitesource/unified-agent-distribution/releases/latest/download/wss-unified-agent.jar
    #   displayName: 'Download the latest Unified Agent'
    
    # - script:  | 
    #     ls -la
    #   displayName: Root DIR Contents

    # - script: | 
    #     java -jar wss-unified-agent.jar -c ./whitesource-fs-agent.config -apiKey $(WhiteSource-APIKey) -product DevSecOpsProduct -project DevSecOpsProject
    #   displayName: 'Run Unified Agent Scan'
```plaintext
