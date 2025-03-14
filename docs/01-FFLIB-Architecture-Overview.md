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

## Architectural Layers

The library implements a layered architecture with the following main components:

![FFLIB Architecture Layers](https://raw.githubusercontent.com/apex-enterprise-patterns/fflib-apex-common-samplecode/master/images/sampleappoverview.png)

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