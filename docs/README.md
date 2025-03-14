**Disclaimer:** I used Claude.ai Sonnect 3.7 to generate these detailed documentation artifacts for the FFLIB Apex Common architecture. My goal is to explore the capabilities of AI models in understanding frameworks and generating code using them. Please use with caution, and I welcome any feedback on potential inaccuracies or hallucinations. -- [Charlie](https://www.linkedin.com/in/charlieguo/)

1. **[FFLIB Architecture Overview](01-FFLIB-Architecture-Overview.md)** - A comprehensive overview of the entire architecture, explaining the layered approach and key design patterns.

2. **[FFLIB Implementation Guide & Best Practices](02-FFLIB-Implementation-Guide.md)** - A practical guide for implementing FFLIB in your Salesforce projects, with step-by-step instructions and best practices.

3. **[FFLIB Class Diagram](03-FFLIB-Common-Class-Diagram.svg)** - A visual representation of the class structure and relationships in the FFLIB architecture.

4. **[FFLIB Sequence Diagram](04-FFLIB-Common-Sequence-Diagram.plantuml)** - A sequence diagram showing the interaction flow between components during an opportunity discount operation.

5. **[FFLIB Component Diagram](05-FFLIB-Component-Diagram.plantuml)** - A component diagram showing the high-level architecture and interactions between different layers.

6. **[FFLIB Domain Layer Pattern Guide](06-FFLIB-Domain-Layer-Guide.md)** - An in-depth guide to implementing the Domain Layer, which encapsulates business logic.

7. **[FFLIB Selector Layer Pattern Guide](07-FFLIB-Selector-Layer-Guide.md)** - A detailed guide to implementing the Selector Layer, which handles all data retrieval.

These artifacts provide a comprehensive understanding of the FFLIB Apex Common architecture. The documentation covers both high-level architectural concepts and detailed implementation patterns with practical code examples.

Key insights from analyzing the fflib-apex-common-samplecode:

1. The architecture follows a clear separation of concerns with distinct layers:
   - Domain Layer for business logic
   - Selector Layer for data access
   - Service Layer for orchestration
   - Application Layer for configuration

2. The framework uses factories and interfaces extensively to promote loose coupling and testability.

3. The Unit of Work pattern manages all database operations as a single transaction.

4. The application class serves as the central configuration point and dependency injection container.

5. Domain classes implement business logic for specific SObjects, while Selector classes handle all queries.
