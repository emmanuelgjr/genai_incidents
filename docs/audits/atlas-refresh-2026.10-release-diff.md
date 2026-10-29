## Release diff: ATLAS 2026.09 -> 2026.10

### Techniques added (18)

| id | name |
|---|---|
| `AML.T0017.003` | Malware |
| `AML.T0085.002` | Conversation Context and Memory |
| `AML.T0085.003` | System Instructions |
| `AML.T0135` | Outputs from AI Models |
| `AML.T0136` | Exfiltration via AI User Interface |
| `AML.T0137` | Training Data Information from AI Models |
| `AML.T0137.000` | Infer Membership |
| `AML.T0137.001` | Infer Properties |
| `AML.T0137.002` | Invert AI Model |
| `AML.T0137.003` | Extract Memorized Data |
| `AML.T0138` | Indicator Removal |
| `AML.T0139` | Compromise Accounts |
| `AML.T0140` | Centralized AI Service Request Routing |
| `AML.T0141` | AI Service Request Metadata Sanitization |
| `AML.T0142` | Event Triggered Execution |
| `AML.T0143` | LLM Prompt Propagation |
| `AML.T0144` | Recover AI Model Internals |
| `AML.T0145` | Poison AI Agent Learning Environment |

### Techniques removed / deprecated (5)

| id | name (in old release) |
|---|---|
| `AML.T0024.000` | Infer Training Data Membership |
| `AML.T0024.001` | Invert AI Model |
| `AML.T0024.002` | Extract AI Model |
| `AML.T0056` | Extract LLM System Prompt |
| `AML.T0057` | LLM Data Leakage |

### Techniques renamed (8)

| id | old name | new name |
|---|---|---|
| `AML.T0005` | Create Proxy AI Model | Replicate AI Model Behavior |
| `AML.T0005.000` | Train Proxy via Gathered AI Artifacts | Replicate Behavior from Gathered AI Artifacts |
| `AML.T0005.001` | Train Proxy via Replication | Replicate Behavior from Model Outputs |
| `AML.T0005.002` | Use Pre-Trained Model | Adapt Existing Model to Replicate Behavior |
| `AML.T0010` | AI Supply Chain Compromise | Supply Chain Compromise |
| `AML.T0010.001` | AI Software | Software |
| `AML.T0010.002` | Data | Data Repository |
| `AML.T0010.003` | Model | Model Repository |

### Technique -> tactic links changed (1)

| id | old tactics | new tactics |
|---|---|---|
| `AML.T0005` | ['AML.TA0001'] | ['AML.TA0001', 'AML.TA0003'] |

### Tactics

- added: none
- removed / deprecated: none
- renamed: none
