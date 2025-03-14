# FFLIB Domain Layer Pattern Guide

## Introduction

The Domain Layer is a core component of the FFLIB Apex Common architecture, implementing the Domain-Driven Design (DDD) approach to encapsulate business logic. This guide provides in-depth coverage of the Domain Layer implementation, best practices, and examples.

## Purpose of the Domain Layer

The Domain Layer serves several key purposes:

1. **Encapsulating Business Logic**: Places business rules and logic related to a specific SObject in a dedicated class
2. **Enforcing Data Integrity**: Validates data consistency and enforces business rules
3. **Separating Concerns**: Isolates domain-specific logic from other aspects of the application
4. **Promoting Reusability**: Enables the reuse of business logic across different contexts
5. **Supporting Bulkification**: Ensures all operations handle collections of records

## Key Components

### Domain Interface

The domain interface defines the contract for domain classes, specifying the operations they support:

```apex
public interface IOpportunities extends fflib_ISObjects {
    void applyDiscount(Decimal discountPercentage, fflib_ISObjectUnitOfWork uow);
    Set<Id> getAccountIds();
    void generate(InvoicingService.InvoiceFactory invoiceFactory);
}

## Common Pitfalls and Solutions

### 1. Memory Limits

**Problem**: Processing large collections in domain methods can hit heap size limits.

**Solution**: Implement chunking strategies for large data sets:

```apex
public void processLargeDataSet(List<SObject> records, fflib_ISObjectUnitOfWork uow) {
    // Process in chunks to avoid heap size limits
    Integer chunkSize = 200;
    
    for(Integer i = 0; i < records.size(); i += chunkSize) {
        Integer endIndex = Math.min(i + chunkSize, records.size());
        List<SObject> chunk = records.subList(i, endIndex);
        
        // Process this chunk
        processChunk(chunk, uow);
    }
}
```

### 2. Circular References

**Problem**: Domain classes that depend on each other can create circular references.

**Solution**: Use service layer as a mediator or implement event-based communication:

```apex
// Instead of direct dependencies between domains, use service layer
public class AccountsServiceImpl implements IAccountsService {
    public void synchronizeWithContacts(Set<Id> accountIds) {
        // Get accounts
        IAccounts accounts = Accounts.newInstance(accountIds);
        
        // Get contacts
        List<Contact> contacts = ContactsSelector.newInstance()
            .selectByAccountId(accountIds);
        
        // Process the synchronization
        processSync(accounts, contacts);
    }
}
```

### 3. Overuse of Domain Methods

**Problem**: Creating too many small, specific domain methods can lead to bloated classes.

**Solution**: Group related functionality and use command pattern for specialized operations:

```apex
// Instead of many small methods
public void markAsWon() { /* ... */ }
public void markAsLost() { /* ... */ }
public void markAsDeferred() { /* ... */ }

// Use a more generic approach
public void updateStage(String stageName, fflib_ISObjectUnitOfWork uow) {
    for(Opportunity opp : (List<Opportunity>) getRecords()) {
        // Validate stage transition
        validateStageTransition(opp, stageName);
        
        // Update stage
        opp.StageName = stageName;
        
        // Handle stage-specific logic
        if(stageName == 'Closed Won') {
            opp.CloseDate = Date.today();
        }
        
        uow.registerDirty(opp);
    }
}

private void validateStageTransition(Opportunity opp, String targetStage) {
    // Validation logic
}
```

### 4. Performance Considerations

**Problem**: Domain methods can sometimes perform poorly with large data sets.

**Solution**: Optimize algorithms and database access:

```apex
// Inefficient - multiple queries inside a loop
public void processAccounts(fflib_ISObjectUnitOfWork uow) {
    for(Account account : (List<Account>) getRecords()) {
        // BAD: Query inside a loop
        List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :account.Id];
        // Process contacts
    }
}

// Optimized - single query with a map
public void processAccounts(fflib_ISObjectUnitOfWork uow) {
    // Get account IDs
    Set<Id> accountIds = new Set<Id>();
    for(Account account : (List<Account>) getRecords()) {
        accountIds.add(account.Id);
    }
    
    // Single query
    List<Contact> allContacts = [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds];
    
    // Create a map for efficient lookup
    Map<Id, List<Contact>> contactsByAccountId = new Map<Id, List<Contact>>();
    for(Contact contact : allContacts) {
        if(!contactsByAccountId.containsKey(contact.AccountId)) {
            contactsByAccountId.put(contact.AccountId, new List<Contact>());
        }
        contactsByAccountId.get(contact.AccountId).add(contact);
    }
    
    // Process each account with its contacts
    for(Account account : (List<Account>) getRecords()) {
        List<Contact> contacts = contactsByAccountId.get(account.Id);
        if(contacts != null) {
            // Process contacts
        }
    }
}
```

## Conclusion

The Domain Layer is a cornerstone of the FFLIB Apex Common architecture, providing a structured approach to encapsulating business logic. By implementing this pattern effectively, you can create more maintainable, testable, and robust applications.

Key takeaways:

1. **Domain-Driven Design**: Focus on modeling business concepts and rules
2. **Separation of Concerns**: Keep domain logic separate from other aspects of the application
3. **Bulkification**: Always handle collections of records, not individual records
4. **Testing**: Thoroughly test domain logic, use mocks when appropriate
5. **Advanced Patterns**: Apply design patterns like State Machine and Specification for complex logic

By following these guidelines and best practices, you'll leverage the full power of the FFLIB Domain Layer pattern in your Salesforce applications.
```

### Domain Implementation

The domain implementation class contains the actual business logic:

```apex
public class Opportunities extends fflib_SObjects implements IOpportunities {
    public static IOpportunities newInstance(List<Opportunity> recordList) {
        return (IOpportunities) Application.Domain.newInstance(recordList);
    }
    
    public static IOpportunities newInstance(Set<Id> recordIdSet) {
        return (IOpportunities) Application.Domain.newInstance(recordIdSet);
    }
    
    public Opportunities(List<Opportunity> sObjectList) {
        super(sObjectList);
    }
    
    public void applyDiscount(Decimal discountPercentage, fflib_ISObjectUnitOfWork uow) {
        // Implementation of business logic
    }
    
    public Set<Id> getAccountIds() {
        // Implementation of data access logic
    }
    
    public void generate(InvoicingService.InvoiceFactory invoiceFactory) {
        // Implementation of generation logic
    }
    
    // Constructor class required for dynamic instantiation
    public class Constructor implements fflib_IDomainConstructor {
        public fflib_SObjects construct(List<Object> objectList) {
            return new Opportunities((List<SObject>) objectList);
        }
    }
}
```

### Trigger Handler Domain Classes

Domain classes can also serve as trigger handlers:

```apex
public class OpportunitiesTriggerHandler extends fflib_SObjectDomain {
    public OpportunitiesTriggerHandler(List<Opportunity> sObjectList) {
        super(sObjectList);
    }
    
    public override void onValidate() {
        // Validation logic for before insert/update triggers
    }
    
    public override void onBeforeInsert() {
        // Logic for before insert trigger
    }
    
    public override void onAfterInsert() {
        // Logic for after insert trigger
    }
    
    // Constructor class for triggerHandler method
    public class Constructor implements fflib_SObjectDomain.IConstructable {
        public fflib_SObjectDomain construct(List<SObject> sObjectList) {
            return new OpportunitiesTriggerHandler(sObjectList);
        }
    }
}
```

## Implementing Domain Classes

### Step 1: Define the Interface

Start by defining the domain interface:

```apex
public interface IAccounts extends fflib_ISObjects {
    void setRating(String rating, fflib_ISObjectUnitOfWork uow);
    Set<Id> getContactIds();
}
```

### Step 2: Implement the Domain Class

```apex
public class Accounts extends fflib_SObjects implements IAccounts {
    public static IAccounts newInstance(List<Account> records) {
        return (IAccounts) Application.Domain.newInstance(records);
    }
    
    public static IAccounts newInstance(Set<Id> recordIds) {
        return (IAccounts) Application.Domain.newInstance(recordIds);
    }
    
    public Accounts(List<Account> records) {
        super(records);
    }
    
    public void setRating(String rating, fflib_ISObjectUnitOfWork uow) {
        for(Account record : (List<Account>) getRecords()) {
            record.Rating = rating;
            uow.registerDirty(record);
        }
    }
    
    public Set<Id> getContactIds() {
        Set<Id> contactIds = new Set<Id>();
        for(Account record : (List<Account>) getRecords()) {
            for(Contact contact : record.Contacts) {
                contactIds.add(contact.Id);
            }
        }
        return contactIds;
    }
    
    public class Constructor implements fflib_IDomainConstructor {
        public fflib_SObjects construct(List<Object> objectList) {
            return new Accounts((List<SObject>) objectList);
        }
    }
}
```

### Step 3: Register in Application Factory

Register the domain class in your Application factory:

```apex
public class Application {
    // Other factory configurations...
    
    // Configure and create the DomainFactory
    public static final fflib_Application.DomainFactory Domain = 
        new fflib_Application.DomainFactory(
            Application.Selector,
            new Map<SObjectType, Type> {
                Account.SObjectType => Accounts.Constructor.class
                // Add other mappings
            });
}
```

## Domain Layer Patterns and Best Practices

### 1. Domain Logic Organization

Structure your domain logic using these patterns:

#### Validation Logic

```apex
public override void onValidate() {
    for(Opportunity opp : (List<Opportunity>) this.records) {
        // Required Field Validation
        if(opp.Type != null && opp.Type.startsWith('Existing') && opp.AccountId == null) {
            opp.AccountId.addError('You must provide an Account for Opportunities for existing Customers.');
        }
        
        // Business Rule Validation
        if(opp.Amount != null && opp.Amount < 0) {
            opp.Amount.addError('Opportunity Amount cannot be negative.');
        }
    }
}
```

#### State Transitions

```apex
public void close(String stage, Date closeDate, fflib_ISObjectUnitOfWork uow) {
    for(Opportunity opp : (List<Opportunity>) getRecords()) {
        // Validate state transition is allowed
        if(opp.IsClosed) {
            throw new ApplicationException('Cannot close an already closed Opportunity.');
        }
        
        // Update fields for state transition
        opp.StageName = stage;
        opp.CloseDate = closeDate;
        
        // Register change with Unit of Work
        uow.registerDirty(opp);
    }
}
```

#### Complex Calculations

```apex
public void calculateCommission(fflib_ISObjectUnitOfWork uow) {
    for(Opportunity opp : (List<Opportunity>) getRecords()) {
        // Skip if not applicable
        if(opp.Amount == null || opp.Amount <= 0) continue;
        
        // Perform complex calculation
        Decimal commissionRate = 0.1; // Default rate
        
        // Adjust rate based on amount tiers
        if(opp.Amount > 100000) {
            commissionRate = 0.15;
        } else if(opp.Amount > 50000) {
            commissionRate = 0.12;
        }
        
        // Apply special rules
        if(opp.Type == 'New Customer') {
            commissionRate += 0.02; // Additional bonus for new customers
        }
        
        // Update commission field
        opp.Commission__c = opp.Amount * commissionRate;
        
        // Register update
        uow.registerDirty(opp);
    }
}
```

### 2. Working with Related Records

Process parent and child records efficiently:

```apex
public void syncWithContacts(fflib_ISObjectUnitOfWork uow) {
    // Get the Account IDs
    Set<Id> accountIds = new Set<Id>();
    for(Account account : (List<Account>) getRecords()) {
        accountIds.add(account.Id);
    }
    
    // Query related contacts
    List<Contact> contacts = [SELECT Id, FirstName, LastName, AccountId 
                               FROM Contact 
                              WHERE AccountId IN :accountIds];
    
    // Group contacts by AccountId
    Map<Id, List<Contact>> contactsByAccountId = new Map<Id, List<Contact>>();
    for(Contact contact : contacts) {
        if(!contactsByAccountId.containsKey(contact.AccountId)) {
            contactsByAccountId.put(contact.AccountId, new List<Contact>());
        }
        contactsByAccountId.get(contact.AccountId).add(contact);
    }
    
    // Process each account with its contacts
    for(Account account : (List<Account>) getRecords()) {
        if(!contactsByAccountId.containsKey(account.Id)) continue;
        
        // Process contacts for this account
        for(Contact contact : contactsByAccountId.get(account.Id)) {
            // Apply business logic
            if(contact.LastName != account.Name) {
                contact.LastName = account.Name;
                uow.registerDirty(contact);
            }
        }
    }
}
```

### 3. Cross-Domain Logic

For logic that spans multiple domains, consider these approaches:

#### Service Layer Coordination

Use the service layer to coordinate between domains:

```apex
public class AccountsServiceImpl implements IAccountsService {
    public void synchronizeWithOpportunities(Set<Id> accountIds) {
        // Get the UOW
        fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();
        
        // Get accounts via domain
        IAccounts accounts = Accounts.newInstance(
            AccountsSelector.newInstance().selectById(accountIds)
        );
        
        // Get related opportunities
        List<Opportunity> opps = OpportunitiesSelector.newInstance()
            .selectByAccountId(accountIds);
        
        // Apply cross-domain logic
        accounts.updateFromOpportunities(opps, uow);
        
        // Commit the changes
        uow.commitWork();
    }
}
```

#### Domain Events

Implement a domain event pattern for loosely coupled communication:

```apex
public class AccountMergedEvent {
    public Id masterAccountId { get; private set; }
    public List<Id> mergedAccountIds { get; private set; }
    
    public AccountMergedEvent(Id masterId, List<Id> mergedIds) {
        this.masterAccountId = masterId;
        this.mergedAccountIds = mergedIds;
    }
}

// In the domain class
public void merge(Id masterAccountId, Set<Id> accountsToMerge, fflib_ISObjectUnitOfWork uow) {
    // Perform merge logic
    // ...
    
    // Publish domain event
    EventBus.publish(new AccountMergedEvent(masterAccountId, new List<Id>(accountsToMerge)));
}

// In a subscriber class
public class OpportunitiesAccountMergeHandler implements IEventSubscriber {
    public void handleEvent(Object event) {
        if(event instanceof AccountMergedEvent) {
            AccountMergedEvent mergeEvent = (AccountMergedEvent)event;
            
            // Update opportunities accordingly
            // ...
        }
    }
}
```

### 4. Behavior Inheritance and Mixins

For shared behavior across domain classes, use inheritance or mixin patterns:

#### Base Domain Class

```apex
public abstract class CustomDomain extends fflib_SObjectDomain {
    public CustomDomain(List<SObject> records) {
        super(records);
    }
    
    // Shared validation logic
    public override void onValidate() {
        // Call standard validation
        super.onValidate();
        
        // Add custom shared validation
        validateRequiredFields();
    }
    
    // Template method for subclasses
    protected abstract void validateRequiredFields();
}

// Subclass implementing the template method
public class Accounts extends CustomDomain {
    public Accounts(List<Account> records) {
        super(records);
    }
    
    protected override void validateRequiredFields() {
        for(Account account : (List<Account>) getRecords()) {
            if(String.isBlank(account.Name)) {
                account.Name.addError('Name is required');
            }
        }
    }
}
```

#### Behavior Mixin

```apex
public interface IAuditableEntity {
    void setAuditFields(fflib_ISObjectUnitOfWork uow);
}

public class AuditableBehavior implements IAuditableEntity {
    private List<SObject> records;
    
    public AuditableBehavior(List<SObject> records) {
        this.records = records;
    }
    
    public void setAuditFields(fflib_ISObjectUnitOfWork uow) {
        for(SObject record : records) {
            if(record.get('LastModifiedDate') == null) {
                record.put('CreatedById', UserInfo.getUserId());
                record.put('CreatedDate', DateTime.now());
            }
            record.put('LastModifiedById', UserInfo.getUserId());
            record.put('LastModifiedDate', DateTime.now());
            
            uow.registerDirty(record);
        }
    }
}

// Using the mixin in a domain class
public class Accounts extends fflib_SObjects implements IAccounts {
    private IAuditableEntity auditableBehavior;
    
    public Accounts(List<Account> records) {
        super(records);
        this.auditableBehavior = new AuditableBehavior(records);
    }
    
    public void setAuditFields(fflib_ISObjectUnitOfWork uow) {
        auditableBehavior.setAuditFields(uow);
    }
}
```

## Trigger Framework Integration

The FFLIB Domain layer integrates elegantly with triggers:

### 1. Trigger Implementation

```apex
trigger AccountTrigger on Account (
    before insert, before update, before delete, 
    after insert, after update, after delete, after undelete
) {
    fflib_SObjectDomain.triggerHandler(AccountsTriggerHandler.class);
}
```

### 2. Domain Trigger Handler

```apex
public class AccountsTriggerHandler extends fflib_SObjectDomain {
    public AccountsTriggerHandler(List<Account> records) {
        super(records);
        // Configure trigger behavior
        Configuration.disableTriggerCRUDSecurity();
    }
    
    // Before trigger events
    public override void onBeforeInsert() {
        // Set default values
    }
    
    public override void onBeforeUpdate(Map<Id, SObject> existingRecords) {
        // Validate changes
    }
    
    // After trigger events
    public override void onAfterInsert() {
        // Create related records
    }
    
    public override void onAfterUpdate(Map<Id, SObject> existingRecords) {
        // Update related records
    }
    
    public class Constructor implements fflib_SObjectDomain.IConstructable {
        public fflib_SObjectDomain construct(List<SObject> records) {
            return new AccountsTriggerHandler(records);
        }
    }
}
```

### 3. Trigger Settings

Implement custom trigger settings for controlled behavior:

```apex
public class AccountsTriggerHandler extends fflib_SObjectDomain {
    public AccountsTriggerHandler(List<Account> records) {
        super(records);
        
        // Apply custom configuration
        if(!TriggerSettings__c.getInstance().Account_Triggers_Enabled__c) {
            // Disable all triggers for this object
            Configuration.disableTriggerState();
        }
        
        if(!TriggerSettings__c.getInstance().Account_Validation_Rules_Enabled__c) {
            // Disable specific trigger events
            Configuration.disableTriggerEvent(
                fflib_SObjectDomain.TriggerEvent.BeforeUpdate,
                fflib_SObjectDomain.TriggerOperation.ValidationRules);
        }
    }
}
```

## Advanced Patterns

### 1. Domain Process Injection

Implement domain process injection for extensible logic:

```apex
public interface IOpportunityProcessHandler {
    void process(List<Opportunity> opportunities, fflib_ISObjectUnitOfWork uow);
}

public class AutomatedDiscountHandler implements IOpportunityProcessHandler {
    public void process(List<Opportunity> opportunities, fflib_ISObjectUnitOfWork uow) {
        for(Opportunity opp : opportunities) {
            if(opp.Amount > 100000) {
                opp.DiscountPercentage__c = 5;
                uow.registerDirty(opp);
            }
        }
    }
}

// In Opportunities domain
public void applyProcessHandlers(fflib_ISObjectUnitOfWork uow) {
    // Get the process handlers
    List<IOpportunityProcessHandler> handlers = getProcessHandlers();
    
    // Apply each handler
    for(IOpportunityProcessHandler handler : handlers) {
        handler.process((List<Opportunity>)getRecords(), uow);
    }
}

private List<IOpportunityProcessHandler> getProcessHandlers() {
    // Could be dynamically loaded from Custom Metadata
    return new List<IOpportunityProcessHandler> {
        new AutomatedDiscountHandler(),
        new OpportunityTeamAssignmentHandler()
    };
}
```

### 2. State Machine Pattern

For complex state transitions, implement a state machine pattern:

```apex
public class OpportunityStateMachine {
    private Opportunity opportunity;
    private Map<String, Set<String>> allowedTransitions;
    
    public OpportunityStateMachine(Opportunity opportunity) {
        this.opportunity = opportunity;
        initializeTransitions();
    }
    
    private void initializeTransitions() {
        allowedTransitions = new Map<String, Set<String>>();
        
        // Define allowed state transitions
        allowedTransitions.put('Prospecting', new Set<String>{
            'Qualification', 'Closed Lost'
        });
        
        allowedTransitions.put('Qualification', new Set<String>{
            'Needs Analysis', 'Closed Lost'
        });
        
        allowedTransitions.put('Needs Analysis', new Set<String>{
            'Value Proposition', 'Closed Lost'
        });
        
        // More transitions...
    }
    
    public Boolean canTransitionTo(String targetStage) {
        String currentStage = opportunity.StageName;
        
        // Check if transition is allowed
        return allowedTransitions.containsKey(currentStage) && 
               allowedTransitions.get(currentStage).contains(targetStage);
    }
    
    public void transitionTo(String targetStage, fflib_ISObjectUnitOfWork uow) {
        if(!canTransitionTo(targetStage)) {
            throw new IllegalStateTransitionException(
                'Cannot transition from ' + opportunity.StageName + ' to ' + targetStage
            );
        }
        
        // Perform the transition
        opportunity.StageName = targetStage;
        
        // Update additional fields based on target state
        if(targetStage == 'Closed Won') {
            opportunity.CloseDate = Date.today();
        }
        
        // Register the change
        uow.registerDirty(opportunity);
    }
    
    public class IllegalStateTransitionException extends Exception {}
}

// Using the state machine in domain class
public void advanceStage(String targetStage, fflib_ISObjectUnitOfWork uow) {
    for(Opportunity opp : (List<Opportunity>) getRecords()) {
        OpportunityStateMachine stateMachine = new OpportunityStateMachine(opp);
        stateMachine.transitionTo(targetStage, uow);
    }
}
```

### 3. Specification Pattern

For complex validation logic, use the specification pattern:

```apex
public interface ISpecification {
    Boolean isSatisfiedBy(SObject record);
    String getErrorMessage();
}

public class OpportunityAmountSpecification implements ISpecification {
    private Decimal minimumAmount;
    
    public OpportunityAmountSpecification(Decimal minimumAmount) {
        this.minimumAmount = minimumAmount;
    }
    
    public Boolean isSatisfiedBy(SObject record) {
        Opportunity opp = (Opportunity)record;
        return opp.Amount >= minimumAmount;
    }
    
    public String getErrorMessage() {
        return 'Opportunity amount must be at least ' + minimumAmount;
    }
}

// Using specifications in the domain
public override void onValidate() {
    // Create specifications
    List<ISpecification> specs = new List<ISpecification>{
        new OpportunityAmountSpecification(1000),
        new OpportunityCloseDateSpecification()
    };
    
    // Apply specifications
    for(Opportunity opp : (List<Opportunity>) getRecords()) {
        for(ISpecification spec : specs) {
            if(!spec.isSatisfiedBy(opp)) {
                opp.addError(spec.getErrorMessage());
            }
        }
    }
}
```

## Testing Domain Classes

### 1. Unit Testing Domain Classes

```apex
### 3. Testing Trigger Handlers

```apex
@IsTest
private class AccountsTriggerHandlerTest {
    @IsTest
    static void testBeforeInsert() {
        // Create test data
        Account testAccount = new Account(
            Name = 'Test Account'
        );
        
        // Execute in trigger context
        Test.startTest();
        
        // This will invoke the trigger handler
        insert testAccount;
        
        Test.stopTest();
        
        // Verify results
        testAccount = [SELECT Id, Name, Rating FROM Account WHERE Id = :testAccount.Id];
        System.assertEquals('New', testAccount.Rating, 'Default rating should be set');
    }
}

### 4. Testing Domain-Specific Behavior

```apex
@IsTest
private class OpportunitiesTest {
    @IsTest
    static void testWithMocks() {
        // Create test data
        Opportunity opp = new Opportunity(
            Id = fflib_IDGenerator.generate(Opportunity.SObjectType),
            Name = 'Test Opportunity',
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 1000
        );
        
        // Create mocks
        fflib_ApexMocks mocks = new fflib_ApexMocks();
        fflib_ISObjectUnitOfWork mockUow = (fflib_ISObjectUnitOfWork)mocks.mock(fflib_ISObjectUnitOfWork.class);
        
        // Create the domain instance
        IOpportunities domainObj = new Opportunities(new List<Opportunity>{ opp });
        
        // Call the method to test
        Test.startTest();
        domainObj.applyDiscount(10, mockUow);
        Test.stopTest();
        
        // Verify interactions with the UOW
        ((fflib_ISObjectUnitOfWork)mocks.verify(mockUow, 1)).registerDirty(opp);
    }
}

private class OpportunitiesTest {
    @IsTest
    static void testApplyDiscount() {
        // Create test data
        Opportunity opp = new Opportunity(
            Name = 'Test Opportunity',
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 1000
        );
        
        // Create the domain instance
        Opportunities domainObj = new Opportunities(new List<Opportunity>{ opp });
        
        // Create mock UOW
        fflib_SObjectUnitOfWork uow = new fflib_SObjectUnitOfWork(
            new List<SObjectType>{ Opportunity.SObjectType }
        );
        
        // Call the method to test
        Test.startTest();
        domainObj.applyDiscount(10, uow);
        Test.stopTest();
        
        // Verify outcome
        System.assertEquals(900, opp.Amount, 'Discount was not applied correctly');
    }
}
```

### 2. Testing with Mocks

```apex
@IsTest
