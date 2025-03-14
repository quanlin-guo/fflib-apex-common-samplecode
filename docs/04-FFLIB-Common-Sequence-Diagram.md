![FFLIB Common Sequence Diagram](https://www.plantuml.com/plantuml/png/ZPH1Zzem48Nl-okUzWGI_04Egrr8Ao7HiYk4EBlEf6iryKIsiuX_tuo25OBJXXD8yxvva-UnNtrGBZHL-LItlqQRMjc03TlWk2p9GNayx-kQMv4ruT9Ndfy0u9Pwgsk8lFqjZLR1i4r51t9VHjDTNqF-MXWZIjA1NOh4IifaN2bZKo9L7lSdYEpO2i05Jkp-ZFHRGqIP2kgNyksGei1F3WJ-8dSJs29Rho09N90PhxbfwUybdpkYrs7vyXB3M4494FL-ndtWszmla5yhx-GqsJ2NNX6MHcAumiQH2eJHY62i3yfg4bJaM0u6c8I6Vb6nWYVvjsxdF9dm-UuuRtJo1Tt0NPVOMzf8LeVznmuV3RaB2dR3GN1kUo8s5Rv5i1nEq1CNEDBiyYldg5I1yY4VkV7lVx39u_bFvpukdZAHTTqNignJ3hroedrtP-vsSNQtUWiqV9xVhtz4DwhKZUI5YA5GadRls4a7Xcsqchm7AVrvUn0zb3fj2rX6QIp11AhyeXiRWGT7-LR946FkSl5NSFJR-40kCovSRfTsFc4-vRnhwriffzxfkYJG-9b6_oaaDHmb7Zjf0AFqlp8ihu9vicGzeRcgJ92Ld7KoUOJZUv3zsE5Ovrqqv5GmR0TNl-jnQBGiJSI7In-hGtjHz0zmB_h_M_xDvk1Yz4b_9PitLVaN)

```plantuml
@startuml
    participant Controller as "OpportunityController"
    participant App as "Application"
    participant Service as "OpportunitiesService"
    participant Selector as "OpportunitiesSelector"
    participant Domain as "Opportunities"
    participant UOW as "Unit of Work"
    participant DB as "Database"

    Note over Controller,DB: Apply Discount Flow

    Controller ->> Service: applyDiscounts(opportunityIds, discountPercent)
    Service ->> App: Create OpportunitiesSelector instance
    App -->> Service: OpportunitiesSelector instance
    Service ->> Selector: selectByIdWithProducts(opportunityIds)
    
    Selector ->> DB: SOQL Query for Opportunities with Products
    DB -->> Selector: Opportunity records with related Products
    Selector -->> Service: Opportunity records with related Products
    
    Service ->> App: Create Opportunities instance
    App -->> Service: Opportunities instance
    
    Service ->> App: Create UnitOfWork instance
    App -->> Service: UnitOfWork instance
    
    Service ->> Domain: applyDiscount(discountPercent, uow)

    Note over Domain: Calculate discount factor
    
    Domain ->> Domain: Process each Opportunity
    
    Note over Domain: If no line items, apply to Opportunity Amount
    
    Domain ->> UOW: registerDirty(opportunity)
    
    Note over Domain: If line items, apply to OpportunityLineItems
    
    Domain ->> App: Create OpportunityLineItems instance
    App -->> Domain: OpportunityLineItems instance
    
    Domain ->> OpportunityLineItems: applyDiscount(discountPercent, uow)
    OpportunityLineItems ->> UOW: registerDirty(lineItem)
    
    Service ->> UOW: commitWork()
    UOW ->> DB: DML Update Operations
    DB -->> UOW: Success
    UOW -->> Service: Success
    Service -->> Controller: Success

    Note over Controller,DB: End of Apply Discount Flow
@enduml
```
