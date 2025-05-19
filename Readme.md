```mermaid
flowchart LR
    subgraph Sources
        A[CoinBase\nWebSocket\nAPI]
        B[Yahoo Finance\nWebSocket\nAPI]
    end

    subgraph Producers
        C[CoinBase Producer]
        D[Yahoo Finance Producer]
    end

    subgraph Kafka
        E[Kafka Broker]
        F[Topic]
        G[Topic]
    end

    subgraph Processing
        H[Transformation\n(Flink\nKafka Streams\nFaust)]
        I[Enriched Topic]
    end

    subgraph Storage
        J[Apache Pinot]
    end

    subgraph Dashboard
        K[Superset Dashboard]
    end

    %% Edges
    A --> C
    B --> D
    C --> F
    D --> G
    F --> E
    G --> E
    E --> H
    H --> I
    I --> J
    J --> K
```