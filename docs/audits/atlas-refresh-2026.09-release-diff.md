## Release diff: ATLAS 2026.06 -> 2026.09

### Techniques added (38)

| id | name |
|---|---|
| `AML.T0000.003` | Scan Databases |
| `AML.T0006.000` | Enumerate Hosted AI Resources |
| `AML.T0006.001` | Query Platform Metadata APIs |
| `AML.T0006.002` | Scan for Exposed AI Infrastructure |
| `AML.T0006.003` | Probe AI Agent Trigger Channels |
| `AML.T0016.003` | Exploits |
| `AML.T0016.004` | AI Agent Tools |
| `AML.T0017.001` | Autonomous Exploit Development |
| `AML.T0017.002` | AI Agent Tools |
| `AML.T0018.003` | Modify Prompt Construction Logic |
| `AML.T0110.000` | Definition and Instructions |
| `AML.T0110.001` | Implementation |
| `AML.T0110.002` | Runtime Response |
| `AML.T0115` | Publish Poisoned AI Artifacts |
| `AML.T0115.000` | Datasets |
| `AML.T0115.001` | Models |
| `AML.T0115.002` | AI Agent Tools |
| `AML.T0116` | Autonomous Reconnaissance |
| `AML.T0117` | Autonomous Attack-Path Adaptation |
| `AML.T0118` | Autonomous AI Agent Communication |
| `AML.T0118.000` | Communication via Shared Artifacts |
| `AML.T0118.001` | Direct Agent Communication |
| `AML.T0119` | Exploit Automated Artifact Processing Pipeline |
| `AML.T0120` | AI Artifact Repository |
| `AML.T0121` | AI Agent Environment Reconstruction |
| `AML.T0122` | Exploitation of Remote Services |
| `AML.T0123` | Obfuscated Files or Information |
| `AML.T0124` | Autonomous Attack Orchestration |
| `AML.T0125` | Create Account |
| `AML.T0126` | Automated Collection |
| `AML.T0127` | Data Staged |
| `AML.T0128` | Compromise Infrastructure |
| `AML.T0129` | Triggers in Multimodal Inputs |
| `AML.T0130` | AI Agent Response Biasing |
| `AML.T0131` | Crafted AI Assistant Links |
| `AML.T0132` | Misconfigured or Publicly Exposed AI Services |
| `AML.T0133` | Discover AI Agent Runtime Capabilities |
| `AML.T0134` | AI Targeted Cloaking |

### Techniques removed / deprecated (3)

| id | name (in old release) |
|---|---|
| `AML.T0019` | Publish Poisoned Datasets |
| `AML.T0058` | Publish Poisoned Models |
| `AML.T0104` | Publish Poisoned AI Agent Tool |

### Techniques renamed (4)

| id | old name | new name |
|---|---|---|
| `AML.T0020` | Poison Training Data | Training Data Poisoning |
| `AML.T0072` | Reverse Shell | Cyber Communication Channel |
| `AML.T0075` | Cloud Service Discovery | Enterprise Resource Discovery |
| `AML.T0089` | Process Discovery | Enterprise Environment Discovery |

### Technique -> tactic links changed (5)

| id | old tactics | new tactics |
|---|---|---|
| `AML.T0012` | ['AML.TA0004', 'AML.TA0012'] | ['AML.TA0004', 'AML.TA0012', 'AML.TA0015'] |
| `AML.T0020` | ['AML.TA0003', 'AML.TA0006'] | ['AML.TA0006'] |
| `AML.T0053` | ['AML.TA0005', 'AML.TA0012'] | ['AML.TA0005', 'AML.TA0012', 'AML.TA0015'] |
| `AML.T0065` | ['AML.TA0003'] | ['AML.TA0001'] |
| `AML.T0066` | ['AML.TA0003'] | ['AML.TA0001'] |

### Tactics

- added: none
- removed / deprecated: none
- renamed: `AML.TA0001` 'AI Attack Staging' -> 'AI Attack Adaptation'
