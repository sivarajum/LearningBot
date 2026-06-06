# Streamlit Visual Playbook

## Architecture Flow
```mermaid
flowchart TD
    subgraph Browser
        U[User] -->|Widgets/Chat| UI[Streamlit Frontend]
    end
    UI -->|REST/WebSocket| API[Inference API / LangChain Router]
    API --> Models[(Models / Vector DB)]
    UI --> Cache[(cache_data / cache_resource)]
    UI --> Storage[(S3 / GCS assets)]
    UI --> Logging[(Tracing / Metrics)]
```

## Layout Blueprint
```mermaid
graph LR
    Sidebar --> Filters[Controls]
    Sidebar --> Settings
    Main --> Tabs
    Tabs --> OverviewTab
    Tabs --> DetailsTab
    OverviewTab --> KPI[Metrics Cards]
    OverviewTab --> ChartArea[Plotly/Altair]
    DetailsTab --> Table[st.dataframe]
    DetailsTab --> ChatZone[st.chat_message]
```

## Data Journey
```mermaid
stateDiagram-v2
    [*] --> LoadConfig
    LoadConfig --> FetchData: cache_data
    FetchData --> RenderWidgets
    RenderWidgets --> UserInput
    UserInput --> ProcessEvent: session_state + forms
    ProcessEvent --> ExternalAPIs
    ExternalAPIs --> UpdateState
    UpdateState --> RenderWidgets
```

## Deployment Topology
```mermaid
graph LR
    DevRepo --> CI[Build & Test]
    CI --> Image[Container Registry]
    Image --> StreamlitCloud
    Image --> CloudRun
    Image --> ECS
    StreamlitCloud --> Users
    CloudRun --> Users
    ECS --> Users
```

## Comparison Grid
| Mode | Layout | State Strategy | Deployment |
| --- | --- | --- | --- |
| Speed Cards | Single page, top metrics | Minimal `session_state`, no cache | Streamlit Cloud preview |
| Deep Dive | Multi-page, sidebar filters | `session_state`, `cache_data` | Docker + Cloud Run |
| Architect | Tabs + chat + diagnostics | `session_state`, background APIs, feature flags | ECS/Fargate or GKE |

## Visual Cues
- **Color coding**: use primary color for actions, neutral gray for data tables, accent for alerts.
- **Status panels**: `st.metric`, `st.progress`, `st.status` (1.31+) for pipeline health.
- **Diagram embed**: `st.image` for exported PNGs or `components.html` for Mermaid-in-iframe when needed.

