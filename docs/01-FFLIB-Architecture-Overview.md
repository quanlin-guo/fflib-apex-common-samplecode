# FFLIB Apex Common Architecture Overview

## Introduction

The FFLIB Apex Common library implements the "Apex Enterprise Patterns" design methodology for building scalable, maintainable applications on the Salesforce platform. It provides a structured approach to organizing code using established design patterns.

This document provides an architectural overview of the FFLIB Apex Common library and sample code, explaining its key components, patterns, and implementation details.

## Core Architecture Principles

FFLIB is built on several key design patterns:

1. **Separation of Concerns**: Code is organized into distinct layers, each with specific responsibilities
2. **Dependency Injection**: Components are loosely coupled and dependencies are injected
3. **Domain-Driven Design**: Business logic is encapsulated in domain classes that represent business entities
4. **Interface-Driven Development**: Components implement interfaces for better abstraction
5. **Factory Pattern**: Factory classes manage the creation of components
6. **Unit of Work Pattern**: Groups related operations into a single transactional unit

## Architectural Diagram

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800">
  <!-- Background -->
  <rect width="1000" height="800" fill="#f8f9fa" />
  
  <!-- Title -->
  <text x="500" y="40" font-family="Arial" font-size="24" text-anchor="middle" font-weight="bold" fill="#333">FFLIB Apex Common Architecture - Class Diagram</text>
  
  <!-- Core FFLIB Framework -->
  <rect x="50" y="80" width="200" height="260" fill="#dae8fc" stroke="#6c8ebf" stroke-width="2" rx="5" />
  <text x="150" y="100" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#333">Core FFLIB Framework</text>
  
  <rect x="70" y="120" width="160" height="30" fill="#ffffff" stroke="#6c8ebf" stroke-width="1" />
  <text x="150" y="140" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">fflib_Application</text>
  
  <rect x="70" y="160" width="160" height="30" fill="#ffffff" stroke="#6c8ebf" stroke-width="1" />
  <text x="150" y="180" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">fflib_SObjectDomain</text>
  
  <rect x="70" y="200" width="160" height="30" fill="#ffffff" stroke="#6c8ebf" stroke-width="1" />
  <text x="150" y="220" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">fflib_SObjectSelector</text>
  
  <rect x="70" y="240" width="160" height="30" fill="#ffffff" stroke="#6c8ebf" stroke-width="1" />
  <text x="150" y="260" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">fflib_SObjectUnitOfWork</text>
  
  <rect x="70" y="280" width="160" height="30" fill="#ffffff" stroke="#6c8ebf" stroke-width="1" />
  <text x="150" y="300" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">fflib_QueryFactory</text>
  
  <!-- Application Factory -->
  <rect x="280" y="80" width="220" height="260" fill="#d5e8d4" stroke="#82b366" stroke-width="2" rx="5" />
  <text x="390" y="100" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#333">Application Factory</text>
  
  <rect x="300" y="120" width="180" height="160" fill="#ffffff" stroke="#82b366" stroke-width="1" />
  <text x="390" y="140" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">Application</text>
  <text x="390" y="165" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ UnitOfWork: UnitOfWorkFactory</text>
  <text x="390" y="185" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ Domain: DomainFactory</text>
  <text x="390" y="205" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ Selector: SelectorFactory</text>
  <text x="390" y="225" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ Service: ServiceFactory</text>
  <line x1="300" y1="145" x2="480" y2="145" stroke="#82b366" stroke-width="1" />
  
  <!-- Domain Layer -->
  <rect x="530" y="80" width="420" height="175" fill="#ffe6cc" stroke="#d79b00" stroke-width="2" rx="5" />
  <text x="740" y="100" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#333">Domain Layer</text>
  
  <!-- Domain Interface -->
  <rect x="550" y="120" width="180" height="115" fill="#ffffff" stroke="#d79b00" stroke-width="1" />
  <text x="640" y="140" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">«interface»</text>
  <text x="640" y="155" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">IOpportunities</text>
  <line x1="550" y1="160" x2="730" y2="160" stroke="#d79b00" stroke-width="1" />
  <text x="640" y="175" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ applyDiscount()</text>
  <text x="640" y="195" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ getAccountIds()</text>
  <text x="640" y="215" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ generate()</text>
  
  <!-- Domain Implementation -->
  <rect x="750" y="120" width="180" height="115" fill="#ffffff" stroke="#d79b00" stroke-width="1" />
  <text x="840" y="140" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">Opportunities</text>
  <line x1="750" y1="145" x2="930" y2="145" stroke="#d79b00" stroke-width="1" />
  <text x="840" y="160" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ newInstance()</text>
  <text x="840" y="175" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ applyDiscount()</text>
  <text x="840" y="190" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ getAccountIds()</text>
  <text x="840" y="205" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ generate()</text>
  <text x="840" y="220" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ Constructor</text>
  
  <!-- Selector Layer -->
  <rect x="530" y="275" width="420" height="175" fill="#e1d5e7" stroke="#9673a6" stroke-width="2" rx="5" />
  <text x="740" y="295" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#333">Selector Layer</text>
  
  <!-- Selector Interface -->
  <rect x="550" y="315" width="180" height="115" fill="#ffffff" stroke="#9673a6" stroke-width="1" />
  <text x="640" y="335" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">«interface»</text>
  <text x="640" y="350" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">IOpportunitiesSelector</text>
  <line x1="550" y1="355" x2="730" y2="355" stroke="#9673a6" stroke-width="1" />
  <text x="640" y="370" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ selectById()</text>
  <text x="640" y="385" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ selectByIdWithProducts()</text>
  <text x="640" y="400" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ selectOpportunityInfo()</text>
  <text x="640" y="415" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ queryLocatorReadyToInvoice()</text>
  
  <!-- Selector Implementation -->
  <rect x="750" y="315" width="180" height="115" fill="#ffffff" stroke="#9673a6" stroke-width="1" />
  <text x="840" y="335" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">OpportunitiesSelector</text>
  <line x1="750" y1="340" x2="930" y2="340" stroke="#9673a6" stroke-width="1" />
  <text x="840" y="355" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ newInstance()</text>
  <text x="840" y="370" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ getSObjectFieldList()</text>
  <text x="840" y="385" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ getSObjectType()</text>
  <text x="840" y="400" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ selectById()</text>
  <text x="840" y="415" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ selectByIdWithProducts()</text>
  
  <!-- Service Layer -->
  <rect x="530" y="470" width="420" height="175" fill="#fff2cc" stroke="#d6b656" stroke-width="2" rx="5" />
  <text x="740" y="490" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#333">Service Layer</text>
  
  <!-- Service Interface -->
  <rect x="550" y="510" width="180" height="115" fill="#ffffff" stroke="#d6b656" stroke-width="1" />
  <text x="640" y="530" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">«interface»</text>
  <text x="640" y="545" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">IOpportunitiesService</text>
  <line x1="550" y1="550" x2="730" y2="550" stroke="#d6b656" stroke-width="1" />
  <text x="640" y="565" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ applyDiscounts()</text>
  <text x="640" y="580" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ createInvoices()</text>
  <text x="640" y="595" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ submitInvoicingJob()</text>
  
  <!-- Service Implementation -->
  <rect x="750" y="510" width="180" height="115" fill="#ffffff" stroke="#d6b656" stroke-width="1" />
  <text x="840" y="530" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">OpportunitiesServiceImpl</text>
  <line x1="750" y1="535" x2="930" y2="535" stroke="#d6b656" stroke-width="1" />
  <text x="840" y="550" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ applyDiscounts()</text>
  <text x="840" y="565" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ createInvoices()</text>
  <text x="840" y="580" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ submitInvoicingJob()</text>
  <text x="840" y="595" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">- applyDiscounts()</text>
  
  <!-- Client Layer -->
  <rect x="50" y="470" width="450" height="175" fill="#f8cecc" stroke="#b85450" stroke-width="2" rx="5" />
  <text x="275" y="490" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#333">Client Layer</text>
  
  <!-- Controller -->
  <rect x="70" y="510" width="180" height="115" fill="#ffffff" stroke="#b85450" stroke-width="1" />
  <text x="160" y="530" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">OpportunityController</text>
  <line x1="70" y1="535" x2="250" y2="535" stroke="#b85450" stroke-width="1" />
  <text x="160" y="550" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ applyDiscount()</text>
  <text x="160" y="565" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ createInvoice()</text>
  
  <!-- Trigger Handler -->
  <rect x="300" y="510" width="180" height="115" fill="#ffffff" stroke="#b85450" stroke-width="1" />
  <text x="390" y="530" font-family="Arial" font-size="12" text-anchor="middle" font-weight="bold" fill="#333">OpportunitiesTriggerHandler</text>
  <line x1="300" y1="535" x2="480" y2="535" stroke="#b85450" stroke-width="1" />
  <text x="390" y="550" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ onValidate()</text>
  <text x="390" y="565" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ onAfterInsert()</text>
  <text x="390" y="580" font-family="Arial" font-size="11" text-anchor="middle" fill="#666">+ Constructor</text>
  
  <!-- Relationships (Connector lines) -->
  <!-- Domain Implementation to Interface -->
  <line x1="750" y1="170" x2="730" y2="170" stroke="#333" stroke-width="1.5" />
  <polygon points="735,170 730,167 730,173" fill="#333" />
  
  <!-- Selector Implementation to Interface -->
  <line x1="750" y1="370" x2="730" y2="370" stroke="#333" stroke-width="1.5" />
  <polygon points="735,370 730,367 730,373" fill="#333" />
  
  <!-- Service Implementation to Interface -->
  <line x1="750" y1="550" x2="730" y2="550" stroke="#333" stroke-width="1.5" />
  <polygon points="735,550 730,547 730,553" fill="#333" />
  
  <!-- Application Factory to Core -->
  <line x1="280" y1="170" x2="230" y2="170" stroke="#333" stroke-width="1.5" stroke-dasharray="5,3" />
  <polygon points="235,170 230,167 230,173" fill="#333" />
  
  <!-- Controller to Service -->
  <path d="M 160 510 L 160 450 L 640 450 L 640 510" stroke="#333" stroke-width="1.5" fill="none" stroke-dasharray="5,3" />
  <polygon points="640,505 637,510 643,510" fill="#333" />
  
  <!-- Trigger Handler to Domain -->
  <path d="M 390 510 L 390 450 L 840 450 L 840 235" stroke="#333" stroke-width="1.5" fill="none" stroke-dasharray="5,3" />
  <polygon points="840,240 837,235 843,235" fill="#333" />
  
  <!-- Service to Domain -->
  <path d="M 840 510 L 840 235" stroke="#333" stroke-width="1.5" fill="none" />
  <polygon points="840,240 837,235 843,235" fill="#333" />
  
  <!-- Service to Selector -->
  <line x1="840" y1="510" x2="840" y2="430" stroke="#333" stroke-width="1.5" fill="none" />
  <polygon points="840,435 837,430 843,430" fill="#333" />
  
  <!-- Legend -->
  <rect x="50" y="670" width="900" height="80" fill="#f5f5f5" stroke="#666" stroke-width="1" rx="5" />
  <text x="500" y="690" font-family="Arial" font-size="14" text-anchor="middle" font-weight="bold" fill="#333">Legend</text>
  
  <rect x="80" y="705" width="20" height="20" fill="#dae8fc" stroke="#6c8ebf" stroke-width="1" />
  <text x="110" y="720" font-family="Arial" font-size="12" text-anchor="start" fill="#333">Core Framework</text>
  
  <rect x="220" y="705" width="20" height="20" fill="#d5e8d4" stroke="#82b366" stroke-width="1" />
  <text x="250" y="720" font-family="Arial" font-size="12" text-anchor="start" fill="#333">Application Factory</text>
  
  <rect x="380" y="705" width="20" height="20" fill="#ffe6cc" stroke="#d79b00" stroke-width
```

## Architectural Layers

The library implements a layered architecture with the following main components:

| Platform Feature       | Patterns Used                                                                                   |
|------------------------|-------------------------------------------------------------------------------------------------|
| **Custom Buttons**     | Building UI logic and calling **Service Layer** code from Controllers                           |
| **Batch Apex**         | Reusing **Service** and **Selector Layer** code from within a Batch context                     |
| **Integration API**    | Exposing an Integration API via **Service Layer** using Apex and REST                           |
| **Apex Triggers**      | Factoring your Apex Trigger logic via the **Domain Layer** (wrappers)                           |
| **VisualForce Remoting** | Exposing **Service Layer** code to HTML5 / JavaScript libraries such as jQuery               |

### 1. Service Layer

**Purpose**: Coordinates activities across multiple domains, provides entry points for business operations.

**Key Characteristics**:
- Implements business processes that span multiple domains
- Transactional coordination
- Acts as the main entry point for controllers and external systems
- Handles cross-cutting concerns

**Implementation**:
- Interface-based design (e.g., `IOpportunitiesService`)
- Implementation classes (e.g., `OpportunitiesServiceImpl`)
- Registration in Application factory

### 2. Domain Layer

**Purpose**: Contains business logic for each SObject type and enforces business rules.

**Key Characteristics**:
- Encapsulates business logic related to a specific SObject
- Validates data integrity
- Implements domain-specific operations
- Uses the Unit of Work for transaction management

**Implementation**:
- Base class `fflib_SObjectDomain` extended by domain classes (e.g., `Opportunities`)
- Interface representation (e.g., `IOpportunities`)
- Constructor class pattern for dynamic instantiation
- Event-based methods (e.g., `onValidate()`, `onBeforeInsert()`)

### 3. Selector Layer

**Purpose**: Retrieves data from the database with consistent, optimized queries.

**Key Characteristics**:
- Encapsulates SOQL queries
- Implements field security
- Provides consistent query patterns
- Supports composite queries with relationships

**Implementation**:
- Base class `fflib_SObjectSelector` extended by selector classes
- Interface representation (e.g., `IOpportunitiesSelector`)
- Explicit field listings for security and maintainability
- Query factory pattern for complex queries

### 4. Unit of Work

**Purpose**: Manages database operations as a single transaction.

**Key Characteristics**:
- Manages DML operations
- Handles object relationships
- Ensures transactional integrity
- Maintains proper order of operations

**Implementation**:
- `fflib_SObjectUnitOfWork` class
- Registration methods for Insert, Update, Delete operations
- Relationship registration
- Commit operations

## Application Factory

The central component that ties all layers together is the Application class. It:

1. Configures the factory components
2. Maps interfaces to implementations
3. Registers SObject types for domains and selectors
4. Provides factory methods for creating components

```apex
public class Application {
    // Configure and create the UnitOfWorkFactory
    public static final fflib_Application.UnitOfWorkFactory UnitOfWork = 
        new fflib_Application.UnitOfWorkFactory(
            new List<SObjectType> { Account.SObjectType, Opportunity.SObjectType, ... });

    // Configure and create the ServiceFactory
    public static final fflib_Application.ServiceFactory Service = 
        new fflib_Application.ServiceFactory(
            new Map<Type, Type> { IAccountsService.class => AccountsServiceImpl.class, ... });

    // Configure and create the SelectorFactory
    public static final fflib_Application.SelectorFactory Selector = 
        new fflib_Application.SelectorFactory(
            new Map<SObjectType, Type> { Account.SObjectType => AccountsSelector.class, ... });

    // Configure and create the DomainFactory
    public static final fflib_Application.DomainFactory Domain = 
        new fflib_Application.DomainFactory(
            Application.Selector,
            new Map<SObjectType, Type> { Opportunity.SObjectType => Opportunities.Constructor.class, ... });
}
```

## Design Patterns Implementation

### 1. Factory Pattern

The factory pattern is extensively used to create instances of components:

```apex
// Service Factory usage
IOpportunitiesService service = (IOpportunitiesService) Application.Service.newInstance(IOpportunitiesService.class);

// Domain Factory usage
IOpportunities opportunities = Opportunities.newInstance(opportunityRecords);

// Selector Factory usage
IOpportunitiesSelector selector = OpportunitiesSelector.newInstance();

// Unit of Work Factory usage
fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();
```

### 2. Unit of Work Pattern

The Unit of Work pattern manages database operations:

```apex
// Create unit of work
fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();

// Register operations
uow.registerNew(account);
uow.registerNew(contact, Contact.AccountId, account);
uow.registerDirty(opportunity);
uow.registerDeleted(oldTask);

// Commit as a single transaction
uow.commitWork();
```

### 3. Dependency Injection

Dependencies are injected through factories:

```apex
// Service methods take dependencies as parameters
public void applyDiscounts(IOpportunities opportunities, Decimal discountPercentage) {
    fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();
    opportunities.applyDiscount(discountPercentage, uow);
    uow.commitWork();
}
```

## Sample Code Components

The sample application implements these patterns through several components:

### 1. Controller Layer

Controllers are lightweight and delegate to the service layer:

```apex
// Example from OpportunityApplyDiscountController
public PageReference applyDiscount() {
    try {
        // Delegate to service layer
        OpportunitiesService.applyDiscounts(
            new Set<Id> { standardController.getId() }, DiscountPercentage);
    }
    catch (Exception e) {
        ApexPages.addMessages(e);
    }        
    return ApexPages.hasMessages() ? null : standardController.view();              
}
```

### 2. Service Layer

Services implement business processes:

```apex
// Example from OpportunitiesServiceImpl
public void applyDiscounts(Set<Id> opportunityIds, Decimal discountPercentage) {
    applyDiscounts(
        OpportunitiesSelector.newInstance().selectByIdWithProducts(opportunityIds),
        discountPercentage);
}

private void applyDiscounts(IOpportunities opportunitiesWithProducts, Decimal discountPercentage) {
    // Create unit of work
    fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();
    // Apply domain logic
    opportunitiesWithProducts.applyDiscount(discountPercentage, uow);
    // Commit transaction
    uow.commitWork();
}
```

### 3. Domain Layer

Domains encapsulate business logic:

```apex
// Example from Opportunities class
public void applyDiscount(Decimal discountPercentage, fflib_ISObjectUnitOfWork uow) {
    // Calculate discount factor
    Decimal factor = calculateDiscountFactor(discountPercentage);
    
    // Apply discount logic
    for(Opportunity opportunity : (List<Opportunity>) getRecords()) {
        // Apply to the Opportunity Amount if no line items
        if(opportunity.OpportunityLineItems == null || opportunity.OpportunityLineItems.isEmpty()) {
            opportunity.Amount = opportunity.Amount * factor;
            uow.registerDirty(opportunity);
        }
        else {
            // Otherwise apply to line items
            lineItems.applyDiscount(this, discountPercentage, uow);
        }
    }
}
```

### 4. Selector Layer

Selectors handle data retrieval:

```apex
// Example from OpportunitiesSelector
public List<Opportunity> selectByIdWithProducts(Set<Id> idSet) {
    fflib_QueryFactory opportunitiesQueryFactory = newQueryFactory();

    // Configure query with related objects
    fflib_QueryFactory lineItemsQueryFactory = 
        new OpportunityLineItemsSelector().
            addQueryFactorySubselect(opportunitiesQueryFactory);
    
    new PricebookEntriesSelector().
        configureQueryFactoryFields(lineItemsQueryFactory, 'PricebookEntry');
    new ProductsSelector().
        configureQueryFactoryFields(lineItemsQueryFactory, 'PricebookEntry.Product2');

    // Execute query
    return (List<Opportunity>) Database.query(
        opportunitiesQueryFactory.setCondition('id in :idSet').toSOQL());
}
```

### 5. Trigger Handlers

Triggers are thin and delegate to domain classes:

```apex
// Example from OpportunitiesTriggerHandler
public override void onValidate() {
    // Validate OpportunityTriggerHandler
    for(Opportunity opp : (List<Opportunity>) this.records) {
        if(opp.Type != null && opp.Type.startsWith('Existing') && opp.AccountId == null) {
            opp.AccountId.addError('You must provide an Account for Opportunities for existing Customers.');
        }
    }
}
```

## Integration Points

The framework integrates with different Salesforce components:

1. **Visualforce Controllers**: Service layer methods are called from controllers
2. **REST APIs**: API endpoints delegate to service layer
3. **Batch Jobs**: Batch Apex classes use selectors and services
4. **Triggers**: Triggers delegate to domain classes

## Testing Approach

The framework supports unit testing through mocking:

1. **Service Mocking**: `Application.Service.setMock(interfaceType, mockImplementation)`
2. **Domain Mocking**: `Application.Domain.setMock(mockDomain)`
3. **Selector Mocking**: `Application.Selector.setMock(mockSelector)`
4. **UnitOfWork Mocking**: `Application.UnitOfWork.setMock(mockUow)`

## Benefits of FFLIB Architecture

1. **Separation of Concerns**: Clear responsibilities for each component
2. **Testability**: Easy to mock and test components in isolation
3. **Maintainability**: Structured approach to code organization
4. **Scalability**: Framework handles bulkification and transaction management
5. **Reusability**: Common patterns promote code reuse
6. **Consistency**: Standard approach to common problems

## Considerations and Best Practices

1. **Start with Interfaces**: Define interfaces first, then implementations
2. **Keep Controllers Thin**: Controllers should only delegate to services
3. **Domain Logic in Domains**: Business logic belongs in domain classes
4. **Selectors for Queries**: All queries should go through selectors
5. **Unit of Work for DML**: Use UoW for all database operations
6. **Follow Naming Conventions**: Consistent naming improves readability

## Conclusion

The FFLIB Apex Common architecture provides a robust framework for building enterprise applications on the Salesforce platform. By adhering to established design patterns and separation of concerns, it promotes code that is maintainable, testable, and scalable.

This architecture enables development teams to work more efficiently and consistently while producing high-quality applications that can evolve with changing business requirements.
