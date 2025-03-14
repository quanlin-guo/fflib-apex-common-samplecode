# FFLIB Selector Layer Pattern Guide

## Introduction

The Selector Layer is a critical component of the FFLIB Apex Common architecture that encapsulates all data retrieval operations. This guide provides a comprehensive overview of the Selector Layer, its implementation, best practices, and advanced techniques.

## Purpose of the Selector Layer

The Selector Layer serves several key purposes:

1. **Centralizing Queries**: Provides a single place for all SOQL queries related to a specific SObject
2. **Implementing Field Security**: Consistently enforces Field-Level Security (FLS) when appropriate
3. **Standardizing Query Structure**: Creates a consistent approach to querying data
4. **Supporting Complex Queries**: Provides tools for building complex queries with relationships
5. **Promoting Reusability**: Enables reuse of query logic across the application

## Key Components

### Selector Interface

The selector interface defines the contract for selector classes:

```apex
public interface IOpportunitiesSelector {
    List<Opportunity> selectById(Set<Id> idSet);
    List<Opportunity> selectByIdWithProducts(Set<Id> idSet);
    List<OpportunityInfo> selectOpportunityInfo(Set<Id> idSet);
    Database.QueryLocator queryLocatorReadyToInvoice();
}
```

### Selector Implementation

The selector implementation contains the actual query logic:

```apex
public class OpportunitiesSelector extends fflib_SObjectSelector implements IOpportunitiesSelector {
    public static IOpportunitiesSelector newInstance() {
        return (IOpportunitiesSelector) Application.Selector.newInstance(Opportunity.SObjectType);
    }
    
    public List<Schema.SObjectField> getSObjectFieldList() {
        return new List<Schema.SObjectField> {
            Opportunity.Id,
            Opportunity.Name,
            Opportunity.AccountId,
            Opportunity.Amount,
            Opportunity.CloseDate,
            Opportunity.StageName
        };
    }
    
    public Schema.SObjectType getSObjectType() {
        return Opportunity.SObjectType;
    }
    
    public List<Opportunity> selectById(Set<Id> idSet) {
        return (List<Opportunity>) selectSObjectsById(idSet);
    }
    
    public List<Opportunity> selectByIdWithProducts(Set<Id> idSet) {
        fflib_QueryFactory opportunitiesQueryFactory = newQueryFactory();
        
        fflib_QueryFactory lineItemsQueryFactory = 
            new OpportunityLineItemsSelector().
                addQueryFactorySubselect(opportunitiesQueryFactory);
        
        new PricebookEntriesSelector().
            configureQueryFactoryFields(lineItemsQueryFactory, 'PricebookEntry');
        
        return (List<Opportunity>) Database.query(
            opportunitiesQueryFactory.setCondition('id in :idSet').toSOQL());
    }
    
    // Other methods...
}
```

## Implementing Selector Classes

### Step 1: Define the Interface

Start by defining the selector interface:

```apex
public interface IAccountsSelector {
    List<Account> selectById(Set<Id> idSet);
    List<Account> selectByName(String name);
    List<Account> selectByIdWithContacts(Set<Id> idSet);
}
```

### Step 2: Implement the Selector Class

```apex
public class AccountsSelector extends fflib_SObjectSelector implements IAccountsSelector {
    public static IAccountsSelector newInstance() {
        return (IAccountsSelector) Application.Selector.newInstance(Account.SObjectType);
    }
    
    public AccountsSelector() {
        super();
    }
    
    public List<Schema.SObjectField> getSObjectFieldList() {
        return new List<Schema.SObjectField> {
            Account.Id,
            Account.Name,
            Account.Industry,
            Account.AnnualRevenue,
            Account.BillingCity,
            Account.BillingCountry
        };
    }
    
    public Schema.SObjectType getSObjectType() {
        return Account.SObjectType;
    }
    
    public List<Account> selectById(Set<Id> idSet) {
        return (List<Account>) selectSObjectsById(idSet);
    }
    
    public List<Account> selectByName(String name) {
        return Database.query(
            newQueryFactory()
                .setCondition('Name = :name')
                .toSOQL()
        );
    }
    
    public List<Account> selectByIdWithContacts(Set<Id> idSet) {
        fflib_QueryFactory accountsQueryFactory = newQueryFactory();
        
        new ContactsSelector().addQueryFactorySubselect(accountsQueryFactory);
        
        return (List<Account>) Database.query(
            accountsQueryFactory.setCondition('Id IN :idSet').toSOQL()
        );
    }
}
```

### Step 3: Register in Application Factory

Register the selector class in your Application factory:

```apex
public class Application {
    // Other factory configurations...
    
    // Configure and create the SelectorFactory
    public static final fflib_Application.SelectorFactory Selector = 
        new fflib_Application.SelectorFactory(
            new Map<SObjectType, Type> {
                Account.SObjectType => AccountsSelector.class,
                Contact.SObjectType => ContactsSelector.class
                // Add other mappings
            });
}
```

## Selector Layer Patterns and Best Practices

### 1. Security Enforcement

Control Field-Level Security (FLS) enforcement:

```apex
public class AccountsSelector extends fflib_SObjectSelector implements IAccountsSelector {
    public AccountsSelector() {
        // Enforce FLS by default
        super(true);
    }
    
    // Override for specific queries
    public List<Account> selectInternalSystemRecords() {
        // Disable FLS for system-level operations
        return Database.query(
            newQueryFactory(false)  // false = don't enforce FLS
                .setCondition('IsSystemAccount__c = true')
                .toSOQL()
        );
    }
}
```

### 2. Working with Query Factory

The `fflib_QueryFactory` provides powerful capabilities for building complex queries:

```apex
public List<Account> selectWithCompoundCriteria(String industry, Decimal minRevenue, List<String> countries) {
    fflib_QueryFactory queryFactory = newQueryFactory();
    
    // Add base condition
    queryFactory.setCondition('Industry = :industry');
    
    // Add additional conditions if parameters are provided
    if(minRevenue != null) {
        queryFactory.setCondition(queryFactory.getCondition() + ' AND AnnualRevenue >= :minRevenue');
    }
    
    if(countries != null && !countries.isEmpty()) {
        queryFactory.setCondition(queryFactory.getCondition() + ' AND BillingCountry IN :countries');
    }
    
    // Add ordering
    queryFactory.addOrdering('Name', fflib_QueryFactory.SortOrder.ASCENDING);
    
    // Execute query
    return (List<Account>) Database.query(queryFactory.toSOQL());
}
```

### 3. Handling Relationships

#### Parent Relationship Queries

```apex
public List<Contact> selectWithAccount(Set<Id> contactIds) {
    fflib_QueryFactory queryFactory = newQueryFactory();
    
    // Add fields from parent object
    queryFactory.selectField('Account.Name');
    queryFactory.selectField('Account.Industry');
    
    // Set condition
    queryFactory.setCondition('Id IN :contactIds');
    
    return (List<Contact>) Database.query(queryFactory.toSOQL());
}
```

#### Child Relationship Queries

```apex
public List<Account> selectWithContacts(Set<Id> accountIds) {
    fflib_QueryFactory accountsQueryFactory = newQueryFactory();
    
    // Add subselect for contacts
    fflib_QueryFactory contactsQueryFactory = new ContactsSelector().addQueryFactorySubselect(accountsQueryFactory);
    
    // Add additional filters to the subquery if needed
    contactsQueryFactory.setCondition('IsActive = true');
    
    // Set main query condition
    accountsQueryFactory.setCondition('Id IN :accountIds');
    
    return (List<Account>) Database.query(accountsQueryFactory.toSOQL());
}
```

### 4. Composing Queries with Other Selectors

Work with multiple selectors for complex relationships:

```apex
public List<Opportunity> selectFullHierarchy(Set<Id> opportunityIds) {
    fflib_QueryFactory opportunitiesQueryFactory = newQueryFactory();
    
    // Add main condition
    opportunitiesQueryFactory.setCondition('Id IN :opportunityIds');
    
    // Add Account relationship fields
    new AccountsSelector().configureQueryFactoryFields(opportunitiesQueryFactory, 'Account');
    
    // Add OpportunityLineItems as a subselect
    fflib_QueryFactory lineItemsQueryFactory = 
        new OpportunityLineItemsSelector().addQueryFactorySubselect(opportunitiesQueryFactory);
    
    // Add further relationships to the subquery
    new PricebookEntriesSelector().configureQueryFactoryFields(lineItemsQueryFactory, 'PricebookEntry');
    new ProductsSelector().configureQueryFactoryFields(lineItemsQueryFactory, 'PricebookEntry.Product2');
    
    // Execute query
    return (List<Opportunity>) Database.query(opportunitiesQueryFactory.toSOQL());
}
```

### 5. Returning Custom Result Types

Create wrapper classes for specialized data needs:

```apex
public class OpportunityInfo {
    public Id opportunityId { get; private set; }
    public String name { get; private set; }
    public String stageName { get; private set; }
    public Decimal amount { get; private set; }
    public String accountName { get; private set; }
    
    public OpportunityInfo(Opportunity opp) {
        this.opportunityId = opp.Id;
        this.name = opp.Name;
        this.stageName = opp.StageName;
        this.amount = opp.Amount;
        this.accountName = opp.Account?.Name;
    }
}

// In the selector class
public List<OpportunityInfo> selectOpportunityInfo(Set<Id> idSet) {
    List<OpportunityInfo> opportunityInfos = new List<OpportunityInfo>();
    
    for(Opportunity opp : Database.query(
        newQueryFactory(false)
            .selectField('Id')
            .selectField('Name')
            .selectField('StageName')
            .selectField('Amount')
            .selectField('Account.Name')
            .setCondition('Id IN :idSet')
            .toSOQL()
    )) {
        opportunityInfos.add(new OpportunityInfo(opp));
    }
    
    return opportunityInfos;
}
```

### 6. Pagination and Limiting Results

Implement pagination for large result sets:

```apex
public class QueryPagination {
    public Integer pageSize { get; set; }
    public Integer pageNumber { get; set; }
    public String orderBy { get; set; }
    public String orderDirection { get; set; }
    
    public QueryPagination(Integer pageSize, Integer pageNumber, String orderBy, String orderDirection) {
        this.pageSize = pageSize;
        this.pageNumber = pageNumber;
        this.orderBy = orderBy;
        this.orderDirection = orderDirection;
    }
    
    public Integer getOffset() {
        return (pageNumber - 1) * pageSize;
    }
}

// In the selector class
public List<Account> selectWithPagination(String industry, QueryPagination pagination) {
    fflib_QueryFactory queryFactory = newQueryFactory();
    
    // Add condition
    queryFactory.setCondition('Industry = :industry');
    
    // Add ordering
    fflib_QueryFactory.SortOrder direction = pagination.orderDirection == 'DESC' ? 
        fflib_QueryFactory.SortOrder.DESCENDING : 
        fflib_QueryFactory.SortOrder.ASCENDING;
    
    queryFactory.addOrdering(pagination.orderBy, direction);
    
    // Add pagination
    queryFactory.setLimit(pagination.pageSize);
    queryFactory.setOffset(pagination.getOffset());
    
    return (List<Account>) Database.query(queryFactory.toSOQL());
}
```

### 7. Batch Processing with QueryLocator

Create methods that return QueryLocator for batch processing:

```apex
public Database.QueryLocator queryLocatorByIndustry(String industry) {
    fflib_QueryFactory queryFactory = newQueryFactory();
    
    queryFactory.setCondition('Industry = :industry');
    
    return Database.getQueryLocator(queryFactory.toSOQL());
}
```

## Advanced Techniques

### 1. Dynamic Field Selection

Enable dynamic field selection:

```apex
public class DynamicFieldSelector {
    private Set<String> fieldNames = new Set<String>();
    
    public DynamicFieldSelector addField(String fieldName) {
        fieldNames.add(fieldName);
        return this;
    }
    
    public DynamicFieldSelector addFields(List<String> fieldNames) {
        this.fieldNames.addAll(fieldNames);
        return this;
    }
    
    public Set<String> getFieldSet() {
        return fieldNames;
    }
}

// In the selector class
public List<Account> selectWithDynamicFields(Set<Id> accountIds, DynamicFieldSelector fieldSelector) {
    fflib_QueryFactory queryFactory = newQueryFactory(false);
    
    // Always include Id field
    queryFactory.selectField('Id');
    
    // Add dynamic fields
    for(String fieldName : fieldSelector.getFieldSet()) {
        // Validate field to prevent SOQL injection
        if(isValidField(fieldName)) {
            queryFactory.selectField(fieldName);
        }
    }
    
    queryFactory.setCondition('Id IN :accountIds');
    
    return (List<Account>) Database.query(queryFactory.toSOQL());
}

private Boolean isValidField(String fieldName) {
    // Implement validation logic to ensure fieldName is a valid field
    // This could check against a list of valid field API names
    Map<String, Schema.SObjectField> fieldMap = Account.SObjectType.getDescribe().fields.getMap();
    return fieldMap.containsKey(fieldName.toLowerCase());
}
```

### 2. Custom Query Builder Pattern

Implement a builder pattern for complex query construction:

```apex
public class AccountQueryBuilder {
    private fflib_QueryFactory queryFactory;
    private AccountsSelector selector;
    
    public AccountQueryBuilder(AccountsSelector selector) {
        this.selector = selector;
        this.queryFactory = selector.newQueryFactory();
    }
    
    public AccountQueryBuilder withName(String name) {
        queryFactory.setCondition('Name = :name');
        return this;
    }
    
    public AccountQueryBuilder withIndustry(String industry) {
        String condition = queryFactory.getCondition();
        queryFactory.setCondition(
            String.isBlank(condition) ? 
            'Industry = :industry' : 
            condition + ' AND Industry = :industry'
        );
        return this;
    }
    
    public AccountQueryBuilder withMinimumRevenue(Decimal minRevenue) {
        String condition = queryFactory.getCondition();
        queryFactory.setCondition(
            String.isBlank(condition) ? 
            'AnnualRevenue >= :minRevenue' : 
            condition + ' AND AnnualRevenue >= :minRevenue'
        );
        return this;
    }
    
    public AccountQueryBuilder withContacts() {
        new ContactsSelector().addQueryFactorySubselect(queryFactory);
        return this;
    }
    
    public AccountQueryBuilder withOpportunities() {
        new OpportunitiesSelector().addQueryFactorySubselect(queryFactory);
        return this;
    }
    
    public AccountQueryBuilder orderBy(String fieldName, Boolean isAscending) {
        queryFactory.addOrdering(fieldName, 
            isAscending ? fflib_QueryFactory.SortOrder.ASCENDING : fflib_QueryFactory.SortOrder.DESCENDING
        );
        return this;
    }
    
    public AccountQueryBuilder limitTo(Integer recordLimit) {
        queryFactory.setLimit(recordLimit);
        return this;
    }
    
    public List<Account> execute() {
        return (List<Account>) Database.query(queryFactory.toSOQL());
    }
}

// Using the builder
public List<Account> selectWithBuilder(String industry, Decimal minRevenue, Boolean includeContacts) {
    AccountQueryBuilder builder = new AccountQueryBuilder(this)
        .withIndustry(industry)
        .withMinimumRevenue(minRevenue)
        .orderBy('Name', true);
    
    if(includeContacts) {
        builder.withContacts();
    }
    
    return builder.execute();
}
```

### 3. Custom Junction Object Queries

Handle complex junction object relationships:

```apex
public List<Contact> selectByAccountTeams(Set<Id> userIds) {
    // This example assumes AccountTeamMember as a junction object between User and Account,
    // and we want to find Contacts related to Accounts where specific Users are team members
    
    fflib_QueryFactory queryFactory = newQueryFactory();
    
    // First, find the account IDs where our users are team members
    List<AccountTeamMember> teamMembers = [
        SELECT AccountId 
        FROM AccountTeamMember 
        WHERE UserId IN :userIds
    ];
    
    // Extract account IDs
    Set<Id> accountIds = new Set<Id>();
    for(AccountTeamMember member : teamMembers) {
        accountIds.add(member.AccountId);
    }
    
    // Now query contacts with these account IDs
    queryFactory.setCondition('AccountId IN :accountIds');
    
    return (List<Contact>) Database.query(queryFactory.toSOQL());
}
```

### 4. Selector Method Injection

Implement a pattern for pluggable query logic:

```apex
public interface ISelectorMethodInjectable {
    String getCondition();
}

public class AccountActiveStatusCondition implements ISelectorMethodInjectable {
    public String getCondition() {
        return 'IsActive__c = true';
    }
}

// In the selector class
public List<Account> selectWithInjectedCondition(ISelectorMethodInjectable conditionProvider) {
    fflib_QueryFactory queryFactory = newQueryFactory();
    
    // Apply the injected condition
    queryFactory.setCondition(conditionProvider.getCondition());
    
    return (List<Account>) Database.query(queryFactory.toSOQL());
}
```

## Testing Selector Classes

### 1. Basic Selector Testing

```apex
@IsTest
private class AccountsSelectorTest {
    @IsTest
    static void testSelectById() {
        // Create test data
        Account testAccount = new Account(Name = 'Test Account');
        insert testAccount;
        
        // Create selector instance
        AccountsSelector selector = new AccountsSelector();
        
        // Call the method to test
        Test.startTest();
        List<Account> accounts = selector.selectById(new Set<Id>{ testAccount.Id });
        Test.stopTest();
        
        // Verify results
        System.assertEquals(1, accounts.size(), 'Should return exactly one account');
        System.assertEquals(testAccount.Id, accounts[0].Id, 'Should return the correct account');
        System.assertEquals('Test Account', accounts[0].Name, 'Should return the correct account name');
    }
}
```

### 2. Testing with Relationships

```apex
@IsTest
private class AccountsSelectorTest {
    @IsTest
    static void testSelectWithRelationships() {
        // Create test data
        Account testAccount = new Account(Name = 'Test Account');
        insert testAccount;
        
        Contact testContact = new Contact(
            FirstName = 'Test',
            LastName = 'Contact',
            AccountId = testAccount.Id
        );
        insert testContact;
        
        // Create selector instance
        AccountsSelector selector = new AccountsSelector();
        
        // Call the method to test
        Test.startTest();
        List<Account> accounts = selector.selectByIdWithContacts(new Set<Id>{ testAccount.Id });
        Test.stopTest();
        
        // Verify results
        System.assertEquals(1, accounts.size(), 'Should return exactly one account');
        System.assertEquals(1, accounts[0].Contacts.size(), 'Should return one related contact');
        System.assertEquals(testContact.Id, accounts[0].Contacts[0].Id, 'Should return the correct contact');
    }
}
```

### 3. Testing with Mocks

```apex
@IsTest
private class AccountsSelectorTest {
    @IsTest
    static void testWithMocks() {
        // Create mock accounts
        List<Account> mockAccounts = new List<Account>{
            new Account(
                Id = fflib_IDGenerator.generate(Account.SObjectType),
                Name = 'Mock Account 1'
            ),
            new Account(
                Id = fflib_IDGenerator.generate(Account.SObjectType),
                Name = 'Mock Account 2'
            )
        };
        
        // Create the mock selector
        fflib_ApexMocks mocks = new fflib_ApexMocks();
        IAccountsSelector mockSelector = (IAccountsSelector)mocks.mock(IAccountsSelector.class);
        
        // Set up the stub
        Set<Id> accountIds = new Set<Id>{ mockAccounts[0].Id, mockAccounts[1].Id };
        mocks.startStubbing();
        mocks.when(mockSelector.selectById(accountIds)).thenReturn(mockAccounts);
        mocks.stopStubbing();
        
        // Register the mock selector
        Application.Selector.setMock(mockSelector);
        
        // Call the service that uses the selector
        Test.startTest();
        IAccountsService service = (IAccountsService) Application.Service.newInstance(IAccountsService.class);
        List<Account> result = service.getAccountsByIds(accountIds);
        Test.stopTest();
        
        // Verify the results
        System.assertEquals(2, result.size(), 'Should return two accounts');
        System.assertEquals('Mock Account 1', result[0].Name, 'Should return the first mock account');
        System.assertEquals('Mock Account 2', result[1].Name, 'Should return the second mock account');
        
        // Verify the mock was called
        ((IAccountsSelector)mocks.verify(mockSelector)).selectById(accountIds);
    }
}
```

## Common Pitfalls and Solutions

### 1. SOQL Query Limits

**Problem**: Hitting the SOQL query limit with complex selectors.

**Solution**: Optimize SOQL queries and use bulk selectors:

```apex
// Instead of querying in a loop
for(Account account : accounts) {
    List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :account.Id];
    // Process contacts
}

// Use a bulk approach
Set<Id> accountIds = new Set<Id>();
for(Account account : accounts) {
    accountIds.add(account.Id);
}

Map<Id, List<Contact>> contactsByAccountId = new Map<Id, List<Contact>>();
for(Contact contact : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
    if(!contactsByAccountId.containsKey(contact.AccountId)) {
        contactsByAccountId.put(contact.AccountId, new List<Contact>());
    }
    contactsByAccountId.get(contact.AccountId).add(contact);
}

for(Account account : accounts) {
    List<Contact> contacts = contactsByAccountId.get(account.Id);
    if(contacts != null) {
        //
