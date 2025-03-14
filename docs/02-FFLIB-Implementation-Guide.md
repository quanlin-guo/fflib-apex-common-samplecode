# FFLIB Implementation Guide & Best Practices

This guide provides detailed implementation instructions and best practices for using the FFLIB Apex Common library in your Salesforce projects.

## Getting Started

### Prerequisites

1. **Understanding of Apex**: Basic knowledge of Apex programming
2. **Salesforce Development**: Familiarity with Salesforce development concepts
3. **Design Patterns**: General understanding of software design patterns

### Installation

To use FFLIB Apex Common, you need to install the following components in your Salesforce org:

1. **Apex Mocks**: [fflib-apex-mocks](https://github.com/apex-enterprise-patterns/fflib-apex-mocks)
2. **Apex Common**: [fflib-apex-common](https://github.com/apex-enterprise-patterns/fflib-apex-common)
3. **Sample Code** (optional): [fflib-apex-common-samplecode](https://github.com/apex-enterprise-patterns/fflib-apex-common-samplecode)

## Setting Up the Application Class

The first step is to create an Application class that serves as the central configuration for your application:

```apex
public class Application {
    // Configure and create the UnitOfWorkFactory for your application
    public static final fflib_Application.UnitOfWorkFactory UnitOfWork = 
        new fflib_Application.UnitOfWorkFactory(
            new List<SObjectType> {
                Account.SObjectType,
                Contact.SObjectType,
                Opportunity.SObjectType
                // Add other SObject types in dependency order
            });

    // Configure and create the ServiceFactory for your application
    public static final fflib_Application.ServiceFactory Service = 
        new fflib_Application.ServiceFactory( 
            new Map<Type, Type> {
                IAccountsService.class => AccountsServiceImpl.class,
                IOpportunitiesService.class => OpportunitiesServiceImpl.class
                // Map interfaces to implementations
            });

    // Configure and create the SelectorFactory for your application
    public static final fflib_Application.SelectorFactory Selector = 
        new fflib_Application.SelectorFactory(
            new Map<SObjectType, Type> {
                Account.SObjectType => AccountsSelector.class,
                Opportunity.SObjectType => OpportunitiesSelector.class
                // Map SObject types to selector classes
            });

    // Configure and create the DomainFactory for your application
    public static final fflib_Application.DomainFactory Domain = 
        new fflib_Application.DomainFactory(
            Application.Selector,
            new Map<SObjectType, Type> {
                Account.SObjectType => Accounts.Constructor.class,
                Opportunity.SObjectType => Opportunities.Constructor.class
                // Map SObject types to domain classes
            });
}
```

## Implementing the Layers

### 1. Domain Layer

The domain layer encapsulates business logic related to SObjects.

#### Step 1: Create the domain interface

```apex
public interface IAccounts extends fflib_ISObjects {
    void setRating(String rating, fflib_ISObjectUnitOfWork uow);
    Set<Id> getContactIds();
}
```

#### Step 2: Implement the domain class

```apex
public class Accounts extends fflib_SObjectDomain implements IAccounts {
    // Constructor
    public Accounts(List<Account> records) {
        super(records);
    }
    
    // Factory method to create new instances
    public static IAccounts newInstance(List<Account> records) {
        return (IAccounts) Application.Domain.newInstance(records);
    }
    
    // Factory method to create with query by id
    public static IAccounts newInstance(Set<Id> recordIds) {
        return (IAccounts) Application.Domain.newInstance(recordIds);
    }
    
    // Domain logic methods
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
    
    // Trigger event handling methods
    public override void onValidate() {
        for(Account record : (List<Account>) getRecords()) {
            if(record.Name == null) {
                record.Name.addError('Account Name is required');
            }
        }
    }
    
    // Required constructor class for factory instantiation
    public class Constructor implements fflib_SObjectDomain.IConstructable {
        public fflib_SObjectDomain construct(List<SObject> records) {
            return new Accounts(records);
        }
    }
}
```

### 2. Selector Layer

The selector layer handles data retrieval from the database.

#### Step 1: Create the selector interface

```apex
public interface IAccountsSelector {
    List<Account> selectById(Set<Id> idSet);
    List<Account> selectByIdWithContacts(Set<Id> idSet);
}
```

#### Step 2: Implement the selector class

```apex
public class AccountsSelector extends fflib_SObjectSelector implements IAccountsSelector {
    // Factory method
    public static IAccountsSelector newInstance() {
        return (IAccountsSelector) Application.Selector.newInstance(Account.SObjectType);
    }
    
    // Required methods from fflib_SObjectSelector
    public List<Schema.SObjectField> getSObjectFieldList() {
        return new List<Schema.SObjectField> {
            Account.Id,
            Account.Name,
            Account.Rating,
            Account.Industry,
            Account.AnnualRevenue
        };
    }
    
    public Schema.SObjectType getSObjectType() {
        return Account.SObjectType;
    }
    
    // Selector methods
    public List<Account> selectById(Set<Id> idSet) {
        return (List<Account>) selectSObjectsById(idSet);
    }
    
    public List<Account> selectByIdWithContacts(Set<Id> idSet) {
        fflib_QueryFactory accountsQueryFactory = newQueryFactory();
        
        // Add subselect for contacts
        new ContactsSelector().addQueryFactorySubselect(accountsQueryFactory);
        
        return (List<Account>) Database.query(
            accountsQueryFactory.setCondition('Id IN :idSet').toSOQL()
        );
    }
}
```

### 3. Service Layer

The service layer coordinates activities and provides entry points for business operations.

#### Step 1: Create the service interface

```apex
public interface IAccountsService {
    void updateRatings(Set<Id> accountIds, String rating);
    Map<Id, List<Contact>> getAccountContacts(Set<Id> accountIds);
}
```

#### Step 2: Implement the service class

```apex
public class AccountsServiceImpl implements IAccountsService {
    public void updateRatings(Set<Id> accountIds, String rating) {
        // Create unit of work to manage transaction
        fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();
        
        // Get accounts via selector
        IAccounts accounts = Accounts.newInstance(
            AccountsSelector.newInstance().selectById(accountIds)
        );
        
        // Apply domain logic
        accounts.setRating(rating, uow);
        
        // Commit work
        uow.commitWork();
    }
    
    public Map<Id, List<Contact>> getAccountContacts(Set<Id> accountIds) {
        // Query accounts with contacts
        List<Account> accountsWithContacts = 
            AccountsSelector.newInstance().selectByIdWithContacts(accountIds);
        
        // Process results
        Map<Id, List<Contact>> accountContactsMap = new Map<Id, List<Contact>>();
        for(Account account : accountsWithContacts) {
            accountContactsMap.put(account.Id, account.Contacts);
        }
        
        return accountContactsMap;
    }
}
```

### 4. Controller Layer

The controller layer handles user interactions and calls services.

```apex
public with sharing class AccountController {
    public Account Account { get; set; }
    
    public AccountController(ApexPages.StandardController stdController) {
        this.Account = (Account)stdController.getRecord();
    }
    
    public PageReference updateRating() {
        try {
            // Call service layer
            IAccountsService accountsService = 
                (IAccountsService) Application.Service.newInstance(IAccountsService.class);
            accountsService.updateRatings(new Set<Id>{ Account.Id }, 'Hot');
            
            // Success message
            ApexPages.addMessage(new ApexPages.Message(
                ApexPages.Severity.INFO, 'Account rating updated successfully.'));
        } catch(Exception e) {
            // Error handling
            ApexPages.addMessage(new ApexPages.Message(
                ApexPages.Severity.ERROR, 'Error updating account: ' + e.getMessage()));
        }
        
        return null;
    }
}
```

### 5. Trigger Implementation

Implement triggers that delegate to domain classes:

```apex
// AccountTrigger.trigger
trigger AccountTrigger on Account (
    before insert, before update, before delete, 
    after insert, after update, after delete, after undelete
) {
    // Create domain class instance for this trigger context
    fflib_SObjectDomain.triggerHandler(AccountsHandler.class);
}

// AccountsHandler.cls
public class AccountsHandler extends fflib_SObjectDomain {
    public AccountsHandler(List<Account> records) {
        super(records);
    }
    
    public override void onValidate() {
        // Validation logic
    }
    
    public override void onAfterInsert() {
        // Post-insert logic
    }
    
    // Constructor class
    public class Constructor implements fflib_SObjectDomain.IConstructable {
        public fflib_SObjectDomain construct(List<SObject> records) {
            return new AccountsHandler(records);
        }
    }
}
```

## Advanced Techniques

### 1. Using the Unit of Work Pattern

The Unit of Work pattern manages database operations as a single transaction:

```apex
// Create unit of work
fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();

// Register new records
Account account = new Account(Name = 'New Account');
uow.registerNew(account);

// Register new records with relationships
Contact contact = new Contact(FirstName = 'John', LastName = 'Doe');
uow.registerNew(contact, Contact.AccountId, account);

// Register dirty (updated) records
Account existingAccount = [SELECT Id, Name FROM Account WHERE Id = :someId];
existingAccount.Name = 'Updated Name';
uow.registerDirty(existingAccount);

// Register deleted records
Contact oldContact = [SELECT Id FROM Contact WHERE Id = :oldContactId];
uow.registerDeleted(oldContact);

// Commit all changes as a single transaction
uow.commitWork();
```

### 2. Advanced Selectors with QueryFactory

Use the QueryFactory for complex queries:

```apex
public List<Account> selectWithComplexCriteria(String industry, Decimal minRevenue) {
    fflib_QueryFactory queryFactory = newQueryFactory();
    
    // Add conditions
    queryFactory.setCondition('Industry = :industry AND AnnualRevenue >= :minRevenue');
    
    // Add ordering
    queryFactory.addOrdering('Name', fflib_QueryFactory.SortOrder.ASCENDING);
    
    // Execute query
    return (List<Account>) Database.query(queryFactory.toSOQL());
}
```

### 3. Bulk Processing in Domain Classes

Always design domain methods to handle lists of records:

```apex
public void applyDiscounts(Decimal discountPercent, fflib_ISObjectUnitOfWork uow) {
    // Process all records in the list
    for(Opportunity opportunity : (List<Opportunity>) getRecords()) {
        // Apply discount to each record
        opportunity.Amount = opportunity.Amount * (1 - (discountPercent / 100));
        uow.registerDirty(opportunity);
    }
}
```

### 4. Working with Related Records

Access and manage related records:

```apex
public class Opportunities extends fflib_SObjectDomain implements IOpportunities {
    public Opportunities(List<Opportunity> records) {
        super(records);
    }
    
    public void addProducts(List<Product2> products, fflib_ISObjectUnitOfWork uow) {
        for(Opportunity opp : (List<Opportunity>) getRecords()) {
            for(Product2 product : products) {
                // Get standard pricebook entry for this product
                PricebookEntry pbe = [SELECT Id, UnitPrice FROM PricebookEntry 
                                       WHERE Product2Id = :product.Id 
                                         AND Pricebook2.IsStandard = true 
                                         LIMIT 1];
                
                // Create opportunity line item
                OpportunityLineItem lineItem = new OpportunityLineItem(
                    OpportunityId = opp.Id,
                    PricebookEntryId = pbe.Id,
                    Quantity = 1,
                    UnitPrice = pbe.UnitPrice
                );
                
                uow.registerNew(lineItem);
            }
        }
    }
}
```

## Testing Strategies

### 1. Unit Testing with Mocks

```apex
@IsTest
private class AccountsServiceTest {
    @IsTest
    static void testUpdateRatings() {
        // Create test data
        Account testAccount = new Account(Id = fflib_IDGenerator.generate(Account.SObjectType), Name = 'Test');
        
        // Create mocks
        fflib_ApexMocks mocks = new fflib_ApexMocks();
        IAccountsSelector mockSelector = (IAccountsSelector)mocks.mock(IAccountsSelector.class);
        IAccounts mockDomain = (IAccounts)mocks.mock(IAccounts.class);
        fflib_ISObjectUnitOfWork mockUow = (fflib_ISObjectUnitOfWork)mocks.mock(fflib_ISObjectUnitOfWork.class);
        
        // Set up stubs and expectations
        mocks.startStubbing();
        mocks.when(mockSelector.selectById(new Set<Id>{testAccount.Id}))
             .thenReturn(new List<Account>{testAccount});
        mocks.stopStubbing();
        
        // Set mock implementations
        Application.Selector.setMock(mockSelector);
        Application.UnitOfWork.setMock(mockUow);
        Application.Domain.setMock(mockDomain);
        
        // Call method to test
        Test.startTest();
        IAccountsService service = (IAccountsService) Application.Service.newInstance(IAccountsService.class);
        service.updateRatings(new Set<Id>{testAccount.Id}, 'Hot');
        Test.stopTest();
        
        // Verify expected behavior
        ((IAccounts)mocks.verify(mockDomain)).setRating('Hot', mockUow);
        ((fflib_ISObjectUnitOfWork)mocks.verify(mockUow)).commitWork();
    }
}
```

### 2. Integration Testing

```apex
@IsTest
private class AccountsIntegrationTest {
    @IsTest
    static void testEndToEndProcess() {
        // Set up test data
        Account testAccount = new Account(Name = 'Integration Test Account');
        
        // Insert test data
        Test.startTest();
        insert testAccount;
        
        // Call service method
        IAccountsService service = (IAccountsService) Application.Service.newInstance(IAccountsService.class);
        service.updateRatings(new Set<Id>{testAccount.Id}, 'Hot');
        
        // Query the result
        Account updatedAccount = [SELECT Id, Name, Rating FROM Account WHERE Id = :testAccount.Id];
        Test.stopTest();
        
        // Verify result
        System.assertEquals('Hot', updatedAccount.Rating, 'Rating should be updated to Hot');
    }
}
```

## Best Practices

### 1. Organizational Structure

Organize your code in a consistent directory structure:

```
/classes
  /domains        # Domain layer classes
    /interfaces   # Domain interfaces
    /impl         # Domain implementations
  /selectors      # Selector layer classes
    /interfaces   # Selector interfaces
    /impl         # Selector implementations
  /services       # Service layer classes
    /interfaces   # Service interfaces
    /impl         # Service implementations
  /controllers    # Controller classes
  /triggers       # Trigger handlers
  /utils          # Utility classes
```

### 2. Naming Conventions

Follow consistent naming conventions:

- **Interfaces**: Prefix with `I` (e.g., `IAccounts`, `IAccountsService`)
- **Implementations**: Suffix with appropriate type (e.g., `AccountsServiceImpl`, `AccountsSelector`)
- **Domain Classes**: Plural noun for SObject type (e.g., `Accounts`, `Opportunities`)
- **Selectors**: SObject name plus `Selector` (e.g., `AccountsSelector`)
- **Services**: SObject name plus `Service` (e.g., `AccountsService`)
- **Trigger Handlers**: SObject name plus `TriggerHandler` (e.g., `AccountsTriggerHandler`)

### 3. Code Organization Guidelines

1. **Keep methods small and focused**
   - Each method should do one thing and do it well
   - Consider 30-50 lines as a good target

2. **Use appropriate layer for logic**
   - Business logic belongs in domain classes
   - Cross-object processes belong in services
   - Data access belongs in selectors

3. **Consistent error handling**
   - Use custom exceptions where appropriate
   - Provide meaningful error messages
   - Consider creating an error handling utility

```apex
public class ApplicationException extends Exception {}

public class AccountsServiceImpl implements IAccountsService {
    public void updateRatings(Set<Id> accountIds, String rating) {
        if (accountIds == null || accountIds.isEmpty()) {
            throw new ApplicationException('Account IDs cannot be null or empty');
        }
        
        if (String.isBlank(rating)) {
            throw new ApplicationException('Rating cannot be blank');
        }
        
        // Continue with implementation...
    }
}
```

### 4. Security Best Practices

1. **Enforce CRUD and FLS in selectors**
   - Use `enforceSecurity` in selectors

```apex
public class AccountsSelector extends fflib_SObjectSelector implements IAccountsSelector {
    public AccountsSelector() {
        super(true); // Enforce security by default
    }
    
    // Enable security enforcement for specific queries
    public List<Account> selectById(Set<Id> idSet) {
        return (List<Account>) Database.query(
            newQueryFactory()
                .setEnforceFLS(true)
                .selectField('Name')
                .selectField('Rating')
                .setCondition('Id IN :idSet')
                .toSOQL()
        );
    }
}
```

2. **Use with sharing appropriately**
   - Use `with sharing` in service classes for standard operations
   - Use `without sharing` only when specifically needed

### 5. Performance Considerations

1. **Minimize SOQL queries**
   - Use composite queries with relationships when possible
   - Leverage selector methods that fetch all needed data at once

2. **Bulkify all operations**
   - Design all methods to handle collections, not single records
   - Test with bulk data (200+ records)

3. **Monitor governor limits**
   - Consider creating a limits utility for high-volume operations
   - Use batch apex for very large data sets

```apex
public class LimitsUtility {
    public static void checkLimits(String context) {
        Integer queriesRemaining = Limits.getLimitQueries() - Limits.getQueries();
        Integer dmlRemaining = Limits.getLimitDMLStatements() - Limits.getDMLStatements();
        
        if (queriesRemaining < 10 || dmlRemaining < 5) {
            System.debug(LoggingLevel.WARN, 
                'Near governor limits in ' + context + 
                ': SOQL=' + queriesRemaining + 
                ', DML=' + dmlRemaining);
        }
    }
}
```

## Common Patterns

### 1. Chain of Responsibility Pattern

Use the chain of responsibility pattern for complex validation logic:

```apex
public class AccountValidationChain {
    public static void validate(List<Account> records) {
        // Execute validators in sequence
        new NameValidator().validate(records);
        new IndustryValidator().validate(records);
        new CreditValidator().validate(records);
    }
    
    private interface IValidator {
        void validate(List<Account> records);
    }
    
    private class NameValidator implements IValidator {
        public void validate(List<Account> records) {
            for (Account record : records) {
                if (String.isBlank(record.Name)) {
                    record.Name.addError('Account name is required');
                }
            }
        }
    }
    
    private class IndustryValidator implements IValidator {
        public void validate(List<Account> records) {
            // Validation logic for Industry
        }
    }
    
    private class CreditValidator implements IValidator {
        public void validate(List<Account> records) {
            // Validation logic for Credit
        }
    }
}
```

### 2. Command Pattern

Use the command pattern for actions that need to be executed or queued:

```apex
public interface ICommand {
    void execute();
}

public class UpdateAccountRatingCommand implements ICommand {
    private Set<Id> accountIds;
    private String rating;
    
    public UpdateAccountRatingCommand(Set<Id> accountIds, String rating) {
        this.accountIds = accountIds;
        this.rating = rating;
    }
    
    public void execute() {
        IAccountsService service = (IAccountsService) Application.Service.newInstance(IAccountsService.class);
        service.updateRatings(accountIds, rating);
    }
}

// Usage
ICommand command = new UpdateAccountRatingCommand(accountIds, 'Hot');
command.execute();
```

### 3. Builder Pattern

Use the builder pattern for complex object creation:

```apex
public class OpportunityBuilder {
    private Opportunity opp;
    private fflib_ISObjectUnitOfWork uow;
    private List<Product2> products;
    
    public OpportunityBuilder(fflib_ISObjectUnitOfWork uow) {
        this.uow = uow;
        this.opp = new Opportunity();
        this.products = new List<Product2>();
    }
    
    public OpportunityBuilder setName(String name) {
        this.opp.Name = name;
        return this;
    }
    
    public OpportunityBuilder setAccount(Account account) {
        this.opp.AccountId = account.Id;
        return this;
    }
    
    public OpportunityBuilder setCloseDate(Date closeDate) {
        this.opp.CloseDate = closeDate;
        return this;
    }
    
    public OpportunityBuilder setStage(String stageName) {
        this.opp.StageName = stageName;
        return this;
    }
    
    public OpportunityBuilder addProduct(Product2 product) {
        this.products.add(product);
        return this;
    }
    
    public Opportunity build() {
        // Register new opportunity
        uow.registerNew(this.opp);
        
        // Add products if any
        if (!this.products.isEmpty()) {
            // Logic to add products...
        }
        
        return this.opp;
    }
}

// Usage
Opportunity newOpp = new OpportunityBuilder(uow)
    .setName('New Deal')
    .setAccount(account)
    .setCloseDate(Date.today().addDays(30))
    .setStage('Prospecting')
    .addProduct(product1)
    .addProduct(product2)
    .build();
```

## Troubleshooting and Common Issues

### 1. Circular Dependencies

**Problem**: Class A depends on Class B, which depends on Class A, causing compilation errors.

**Solution**: 
- Use interfaces to break circular dependencies
- Extract common dependencies to separate classes
- Use the Service Locator pattern for complex dependencies

### 2. Governor Limit Exceptions

**Problem**: Hitting governor limits in complex transactions or with large data volumes.

**Solutions**:
- Review SOQL queries for optimization opportunities
- Use batch apex for processing large datasets
- Consider asynchronous processing with queueable apex
- Implement chunking strategies for large operations

### 3. Test Data Setup Issues

**Problem**: Complex data setup makes tests brittle and hard to maintain.

**Solution**: Create test data factories that centralize data creation:

```apex
public class TestDataFactory {
    public static Account createAccount(Boolean doInsert) {
        Account acc = new Account(Name = 'Test Account');
        if (doInsert) {
            insert acc;
        }
        return acc;
    }
    
    public static List<Account> createAccounts(Integer count, Boolean doInsert) {
        List<Account> accounts = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            accounts.add(new Account(Name = 'Test Account ' + i));
        }
        
        if (doInsert) {
            insert accounts;
        }
        return accounts;
    }
    
    public static Opportunity createOpportunity(Id accountId, Boolean doInsert) {
        Opportunity opp = new Opportunity(
            Name = 'Test Opportunity',
            AccountId = accountId,
            CloseDate = Date.today().addDays(30),
            StageName = 'Prospecting'
        );
        
        if (doInsert) {
            insert opp;
        }
        return opp;
    }
}
```

## Migrating Existing Code to FFLIB

### 1. Gradual Migration Strategy

1. **Start with the Application class**
   - Set up the central configuration

2. **Create selectors first**
   - Convert existing queries to selector methods
   - This provides immediate benefits without major refactoring

3. **Implement domain classes**
   - Move business logic from triggers to domain classes
   - Create interfaces for domain classes

4. **Create service layer**
   - Move controller and utility logic to service classes
   - Define service interfaces

5. **Refactor triggers**
   - Convert triggers to use the fflib_SObjectDomain handler

### 2. Coexistence Strategy

For large codebases, implement a strategy that allows FFLIB and legacy code to coexist:

```apex
public class LegacyBridge {
    // Methods to bridge between legacy code and FFLIB
    public static List<Account> getAccounts(Set<Id> accountIds) {
        // Use FFLIB selector in legacy code
        return AccountsSelector.newInstance().selectById(accountIds);
    }
    
    public static void updateAccount(Account account) {
        // Use FFLIB domain and UoW in legacy code
        fflib_ISObjectUnitOfWork uow = Application.UnitOfWork.newInstance();
        uow.registerDirty(account);
        uow.commitWork();
    }
}
```

## Conclusion

Implementing the FFLIB Apex Common architecture provides a robust foundation for building maintainable, testable, and scalable applications on the Salesforce platform. By following these implementation guidelines and best practices, you can fully leverage the benefits of this proven enterprise pattern framework.

Remember that architecture is a means to an end, not an end in itself. The goal is to create applications that deliver business value while being maintainable and adaptable to changing requirements. FFLIB provides a structured approach to achieve this goal, but should be applied pragmatically to suit your specific project needs.
