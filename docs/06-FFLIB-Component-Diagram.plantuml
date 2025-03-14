flowchart TD
    subgraph "Client Layer"
        VF[Visualforce Pages]
        LWC[Lightning Components]
        REST[REST API]
        Trig[Triggers]
        Batch[Batch Jobs]
    end
    
    subgraph "Application Factory"
        App[Application]
        App --> ServiceFac[Service Factory]
        App --> DomainFac[Domain Factory]
        App --> SelectorFac[Selector Factory]
        App --> UOWFac[Unit of Work Factory]
    end
    
    subgraph "Service Layer"
        ServiceInt[Service Interfaces]
        ServiceImpl[Service Implementations]
        ServiceFac --> ServiceInt
        ServiceInt --> ServiceImpl
    end
    
    subgraph "Domain Layer"
        DomainInt[Domain Interfaces]
        DomainImpl[Domain Implementations]
        DomainFac --> DomainInt
        DomainInt --> DomainImpl
    end
    
    subgraph "Selector Layer"
        SelectorInt[Selector Interfaces]
        SelectorImpl[Selector Implementations]
        QueryFac[Query Factory]
        SelectorFac --> SelectorInt
        SelectorInt --> SelectorImpl
        SelectorImpl --> QueryFac
    end
    
    subgraph "Unit of Work"
        UOW[Unit of Work]
        UOWFac --> UOW
    end
    
    subgraph "Database"
        DB[(Salesforce Database)]
    end
    
    %% Client connections
    VF --> ServiceInt
    LWC --> ServiceInt
    REST --> ServiceInt
    Trig --> DomainInt
    Batch --> SelectorInt
    Batch --> ServiceInt
    
    %% Service connections
    ServiceImpl --> DomainInt
    ServiceImpl --> SelectorInt
    ServiceImpl --> UOW
    
    %% Domain connections
    DomainImpl --> UOW
    
    %% Selector connections
    SelectorImpl --> DB
    
    %% UOW connections
    UOW --> DB
    
    classDef clientLayer fill:#f8cecc,stroke:#b85450
    classDef appFactory fill:#d5e8d4,stroke:#82b366
    classDef serviceLayer fill:#fff2cc,stroke:#d6b656
    classDef domainLayer fill:#ffe6cc,stroke:#d79b00
    classDef selectorLayer fill:#e1d5e7,stroke:#9673a6
    classDef unitOfWork fill:#dae8fc,stroke:#6c8ebf
    classDef database fill:#f5f5f5,stroke:#666666
    
    class VF,LWC,REST,Trig,Batch clientLayer
    class App,ServiceFac,DomainFac,SelectorFac,UOWFac appFactory
    class ServiceInt,ServiceImpl serviceLayer
    class DomainInt,DomainImpl domainLayer
    class SelectorInt,SelectorImpl,QueryFac selectorLayer
    class UOW unitOfWork
    class DB database
