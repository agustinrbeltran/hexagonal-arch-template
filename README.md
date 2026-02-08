# Overview

📘 This FastAPI-based project demonstrates a practical implementation of **Hexagonal Architecture** (Ports and Adapters) with feature-based organization. It incorporates Command Query Responsibility Segregation (CQRS) principles and elements of Domain-Driven Design (DDD). While not meant to serve as a comprehensive reference or a strict application of these methodologies, the project shows how their core ideas can be effectively applied in Python. If these patterns are new to you, refer to the [Useful Resources](#useful-resources) section.

This template evolved from a Clean Architecture implementation with layered organization into a true hexagonal architecture with explicit ports, adapters, and feature-based bounded contexts. See [About This Template](#about-this-template) for the relationship to the original work.

## About This Template

This project is a fork and evolution of [fastapi-clean-example](https://github.com/ivan-borovets/fastapi-clean-example) by **Ivan Borovets**. While the original project demonstrated Clean Architecture with layered organization, this template has been refactored to implement true Hexagonal Architecture (Ports and Adapters) with feature-based organization.

**Key Changes from Original:**
- Migrated from layered structure (domain/application/infrastructure/presentation) to feature-based hexagonal architecture (features with ports/adapters)
- Explicit port abstractions (inbound/outbound) for each feature
- Feature-based bounded contexts instead of global layers
- Enhanced developer tooling (comprehensive Makefile, improved code quality automation)

Credit to Ivan Borovets for the excellent foundation and architecture patterns. This template builds upon his work to demonstrate an alternative architectural approach.

# Table of contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
   1. [Introduction](#introduction)
   2. [Hexagonal Architecture Approach](#hexagonal-architecture-approach)
   3. [Dependency Rule](#dependency-rule)
      1. [Note on Adapters](#note-on-adapters)
   4. [Hexagonal Architecture Continued](#hexagonal-architecture-continued)
   5. [Dependency Inversion](#dependency-inversion)
   6. [Dependency Injection](#dependency-injection)
   7. [CQRS](#cqrs)
3. [Project](#project)
   1. [Dependency Graphs](#dependency-graphs)
   2. [Structure](#structure)
   3. [Makefile Commands Reference](#makefile-commands-reference)
   4. [Technology Stack](#technology-stack)
   5. [API](#api)
      1. [General](#general)
      2. [Account](#account-apiv1account)
      3. [Users](#users-apiv1users)
   6. [Configuration](#configuration)
      1. [Files](#files)
      2. [Flow](#flow)
      3. [Local Environment](#local-environment)
      4. [Other Environments](#other-environments-devprod)
      5. [Adding New Environments](#adding-new-environments)
4. [Useful Resources](#useful-resources)
5. [Support the Project](#-support-the-project)
6. [Acknowledgements](#acknowledgements)

# Architecture Principles

## Introduction

This repository may be helpful for those seeking backend implementation in
Python that is both framework-agnostic and storage-agnostic (unlike Django).
Such flexibility can be achieved by using a web framework that doesn't impose
strict software design (like FastAPI) and applying a layered architecture
patterned after the one proposed by Robert Martin, which we'll explore further.

The original explanation of Clean Architecture concepts can be found
[here](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
If you're still wondering why Clean Architecture matters, read the article — it
only takes about 5 minutes. In essence, it’s about making your application
independent of external systems and highly testable.

<p align="center">
  <img src="docs/Robert_Martin_CA.png" alt="Clean Architecture Diagram" />
  <br><em>Figure 1: <b>Robert Martin's</b> Clean Architecture Diagram</em>
</p>

> "A computer program is a detailed description of the **policy** by which
> inputs are transformed into outputs."
>
> — Robert Martin

The most abstract policies define core business rules, while the least abstract
ones handle I/O operations. Being closer to implementation details, less
abstract policies are more likely to change. **Layer** represents a collection
of components expressing policies at the same level of abstraction.

Concentric circles represent boundaries between different layers. The meaning of
arrows in the diagram will be discussed [later](#dependency-rule). For now, we
will focus on the purpose of the layers.

## Hexagonal Architecture Approach

This project implements **Hexagonal Architecture** (also known as Ports and Adapters) with **feature-based organization**. Instead of organizing code into global layers (domain, application, infrastructure, presentation), each feature is a **bounded context** with its own hexagon containing domain logic, ports, adapters, and entrypoints.

### Feature Organization

Each feature (e.g., `features/account/`, `features/user/`) is a self-contained hexagon:

- **Domain (Core)** — Business logic at the center of the hexagon
- **Ports** — Abstractions (interfaces) defining the hexagon's boundaries
  - **Inbound Ports** (driving) — Use case interfaces invoked by external actors
  - **Outbound Ports** (driven) — Gateway interfaces for infrastructure dependencies
- **Adapters** — Concrete implementations connecting to external systems
- **Entrypoints** — Controllers that handle external requests (REST, CLI, etc.)

![#gold](https://placehold.co/15x15/gold/gold.svg) **Domain Core** (`features/{feature}/domain/core/`)

- **Domain model** is a set of concepts, rules and behaviors that define what
  business (context) is and how it operates. It is expressed in **ubiquitous
  language** — consistent terminology shared by developers and domain experts.
  Each feature domain implements its bounded context model in code.
- The strictest domain rules are **invariants** — conditions that must always
  hold true for the model. Enforcing invariants means maintaining data
  consistency in the model. This can be achieved through **encapsulation**,
  which hides internal state and couples data with behavior.
- Building blocks of domain model are (not limited to these):
  - **value objects** — smart business types (no identity, immutable, equal by
    value). Examples: `UserId`, `Username`, `RawPassword`
  - **entities** — business objects (have identity and lifecycle, equal by
    identity). Examples: `User`, `AuthSession`
  - **domain services** — containers for behavior that has no place in the
    components above. Examples: `LogInService`, `CreateUserService`
- Other domain model building blocks, unused in this project but important for
  deeper DDD:
  - **aggregates** — clusters of entities (1+) that must change together as a
    single unit, managed exclusively through their root, defining boundaries of
    transactional consistency.
  - **repositories** — abstractions emulating collections of aggregate roots.
- Domain model lies on a spectrum from anemic to rich.
  - **anemic** — simple data types, entities are just data holders, rules and
    behaviors live outside.
  - **rich** — value objects and entities encapsulate data and rules; invariants
    are enforced internally, so the model itself prevents invalid states. For
    components: anemic means no behavior within, rich — the contrary.
- Domain services represent operations that don't naturally belong to
  a specific entity or value object. But in projects with anemic entities, they
  can also contain logic that would otherwise be in those entities.
- In early stages of development when the domain model is not yet clearly
  defined, keeping entities flat and anemic is practical, even though the
  latter weakens encapsulation. Once domain logic is well established, some
  entities can, as aggregate roots, become non-flat and rich. This best enforces
  invariants but can be tricky to design once and for all.
- Prefer rich value objects early, freeing entities and services from an
  excessive burden of local rules.
- Consider the domain core the most important, stable, and independent part of
  each feature.

![#purple](https://placehold.co/15x15/purple/purple.svg) **Ports** (`features/{feature}/domain/port/`)

**Inbound Ports (Driving)** — Use case interfaces that define what the hexagon can do:
- These are **abstractions** (protocols/interfaces) that external actors use to interact with the domain
- Each port represents a single use case or business operation
- Examples: `LogInUseCase`, `CreateUserUseCase`, `GrantAdminUseCase`
- Domain services implement these ports, providing the actual business logic
- Controllers (entrypoints) depend on these abstractions, not on concrete implementations
- This allows the domain to remain decoupled from delivery mechanisms (REST, CLI, gRPC, etc.)

**Outbound Ports (Driven)** — Gateway interfaces that define what the hexagon needs:
- These are **abstractions** for infrastructure dependencies (databases, external APIs, etc.)
- Examples: `UserRepository`, `PasswordHasher`, `AuthSessionGateway`
- Adapters implement these ports, providing concrete infrastructure integrations
- Domain services depend on these abstractions, not on concrete implementations
- This allows the domain to remain agnostic of storage mechanisms and external systems

The **ports** define the hexagon's boundary. Everything inside the hexagon depends only on abstractions, never on concrete implementations outside the hexagon.

![#green](https://placehold.co/15x15/green/green.svg) **Adapters** (`features/{feature}/adapter/`)

- Adapters are concrete implementations of **outbound ports**
- They translate between the domain's abstractions and real-world infrastructure
- Examples:
  - `SqlaUserRepositoryAdapter` implements `UserRepository` using SQLAlchemy
  - `PasswordHasherBcrypt` implements `PasswordHasher` using bcrypt
  - `IdentityProvider` implements authentication details
- Adapters handle infrastructure concerns: database queries, API calls, file I/O, etc.
- They depend on both domain ports (to implement) and external systems (databases, libraries)
- Related adapter logic can be grouped into **infrastructure services**

> [!IMPORTANT]
>
> - Each feature is a **bounded context** with its own hexagon. Features can share
>   common building blocks from `/common`, but each maintains its own domain model.
> - The key principle remains the **Dependency Rule**: dependencies point inward
>   toward the domain core. Ports provide the abstraction layer that enables this.

## Dependency Rule

A dependency occurs when one software component relies on another to operate. If
you were to split all blocks of code into separate modules, dependencies would
manifest as imports between those modules. Typically, dependencies are
graphically depicted in UML style in such a way that

> [!IMPORTANT]
>
> - `A -> B` (**A points to B**) means **A depends on B**.

The key principle of Clean Architecture is the **Dependency Rule**. This rule
states that **more abstract software components must not depend on more concrete
ones.** In other words, dependencies must never point outwards.

> [!IMPORTANT]
>
> - The **domain core** (inside the hexagon) may import external tools and libraries to the
>   extent necessary for describing business logic - those that extend the
>   programming language's capabilities (math/numeric utilities, time zone
>   conversion, object modeling, etc.). This trades some core stability for
>   clarity and expressiveness. What is not acceptable are dependencies that
>   bind business logic to implementation details (including frameworks) or to
>   out-of-process systems (databases, brokers, file systems, cloud SDKs, etc.).
> - Components within the same zone **can depend on each other.** For example,
>   adapters in a feature can interact with one another, and domain services
>   within a feature can call each other.
> - **Entrypoints** (driving adapters) can depend on domain core through **inbound ports**.
>   **Infrastructure adapters** (driven adapters) implement **outbound ports** defined by
>   the domain. Both types of adapters can access domain entities and value objects as needed.
> - Avoid letting business logic leak into adapters. Adapters should focus purely on
>   technical concerns (database queries, API calls, serialization) without containing
>   business rules. However, in specific cases where database constraints enforce business
>   rules, adapters may raise domain-specific exceptions, such as
>   `UsernameAlreadyExistsError` for a `UNIQUE CONSTRAINT` violation. Handling
>   these exceptions in domain services ensures that any business logic
>   expressed in adapters remains under domain control.
> - Avoid introducing elements in the domain core that specifically exist to
>   support adapters. For example, don't add ports or domain logic solely
>   to accommodate a specific infrastructure technology. At first glance, based on
>   imports, it might seem that the Dependency Rule isn't violated. However,
>   you've broken the core idea of the rule by embedding infrastructure concerns
>   (more concrete) into the business logic (more abstract).
> - Each feature's hexagon should be **self-contained**. Cross-feature dependencies
>   should be minimized and go through well-defined integration points. Shared
>   concerns live in `/common`.

### Note on Adapters in Hexagonal Architecture

Hexagonal Architecture distinguishes between two types of adapters:

**Driving Adapters (Primary)** — Initiate interactions with the domain:
- **Entrypoints** such as REST controllers, CLI handlers, message consumers
- These adapters **drive** the application by invoking inbound ports (use cases)
- They translate external requests into domain operations
- Example: `features/account/entrypoint/rest/controllers/log_in.py`

**Driven Adapters (Secondary)** — Provide infrastructure services to the domain:
- **Infrastructure adapters** such as database repositories, external API clients
- These adapters are **driven by** the domain through outbound ports
- They translate domain abstractions into concrete infrastructure operations
- Example: `features/user/adapter/sqla_user_repository_adapter_.py`

Both adapter types depend on the domain through **ports** (abstractions). This creates a dependency structure where:
- Entrypoints depend on **inbound ports** (use case interfaces)
- Infrastructure adapters implement **outbound ports** (gateway interfaces)
- Domain core depends on nothing but port abstractions

This approach is a **pragmatic adaptation** that:
- Avoids excessive abstractions with implementations outside the application's boundaries
- Retains all key advantages of Clean Architecture (testability, replaceability, independence)
- Allows adapters to be removed/replaced along with external systems they connect to
- Simplifies real-world development without compromising architectural principles

The key principle for this project:

> "Dependencies must never point outwards **within the domain core**."

The domain core (entities, value objects, domain services, ports) has zero dependencies on adapters or external systems. Adapters depend on ports, not the other way around.

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 10px; justify-items: center;">
  <img src="docs/onion_1.svg" alt="Revised Interpretation of CA-D" style="width: 400px; height: auto;" />
  <img src="docs/onion_2.svg" alt="Revised Interpretation of CA-D, alternative" style="width: 400px; height: auto;" />
</div>
<p align="center" style="font-size: 14px;">
  <em>Figure 2: <b>Revised Interpretation</b> of Clean Architecture<br>
  (diagrammed — original and alternative representation)
  </em>
</p>

## Hexagonal Architecture Continued

![#blue](https://placehold.co/15x15/blue/blue.svg) **Entrypoints** (`features/{feature}/entrypoint/`)

Entrypoints are **driving adapters** that receive external requests and invoke the domain through inbound ports:

- This includes **controllers** (REST, GraphQL, CLI, message consumers, scheduled jobs)
  that translate external requests into domain use case invocations
- Controllers validate inputs and invoke **inbound ports** (use case interfaces)
- The domain core assumes that request data is already validated by controllers,
  allowing it to focus solely on business logic
- Controllers must be as thin as possible, containing no logic beyond basic
  input validation and routing. They act as an intermediary between
  external actors and the domain's inbound ports

**Example Flow:**
1. HTTP request arrives at `POST /api/v1/account/login`
2. Controller (`features/account/entrypoint/rest/controllers/log_in.py`) validates request structure
3. Controller invokes `LogInUseCase` (inbound port) with validated data
4. Domain service (`LogInService`) implements the use case, orchestrating business logic
5. Domain service calls outbound ports (`UserRepository`, `AuthSessionGateway`) as needed
6. Adapters implement outbound ports, executing database queries
7. Controller receives result and formats HTTP response

> [!IMPORTANT]
>
> - **_Basic_** validation, like checking whether the structure of the incoming
>   request matches the structure of the defined request model (e.g., type
>   safety and required fields) should be performed by controllers at the
>   entrypoint, while **_business rule_** validation (e.g., ensuring the email domain
>   is allowed, verifying the uniqueness of username, or checking if a user
>   meets the required age) belongs to the Domain core.
> - Business rule validation often involves relationships between fields, such
>   as ensuring that a discount applies only within a specific date range or a
>   promotion code is valid for orders above a certain total.
> - **Carefully** consider using Pydantic for business rule validation. While
>   convenient, Pydantic models are slower than regular dataclasses and reduce
>   domain core stability by coupling business logic to an external library.
> - If you choose Pydantic (or a similar tool bundled with web framework) for
>   domain model definitions, ensure that a Pydantic model in the domain core
>   is a separate model from the one in the entrypoint, even if their
>   structure appears identical. Mixing data presentation logic with business
>   logic is a common mistake made early in development to save effort on
>   creating separate models and field mapping, often due to not understanding
>   that structural similarities are temporary.
> - In hexagonal architecture, controllers depend on **inbound port abstractions**,
>   not directly on domain services. This decoupling allows the same domain logic
>   to be accessed through different entrypoints (REST, GraphQL, CLI) without
>   changing the domain.

![#gray](https://placehold.co/15x15/gray/gray.svg) **External Systems**

External systems operate completely outside the hexagon's boundaries:

- These include web frameworks (FastAPI), databases (PostgreSQL), message brokers,
  third-party APIs, file systems, and other infrastructure components
- External systems have no direct access to the domain core
- They interact with the application only through adapters:
  - **Driving side**: Web frameworks invoke controllers (entrypoints)
  - **Driven side**: Adapters use infrastructure libraries to implement outbound ports
- Because the domain depends only on port abstractions (not concrete implementations),
  external systems can be replaced without affecting business logic
- Examples of replaceability:
  - Switch from PostgreSQL to MongoDB by implementing new adapter
  - Add GraphQL alongside REST by creating new entrypoints
  - Replace bcrypt with Argon2 by swapping `PasswordHasher` implementation

> [!NOTE]
> The hexagon (domain core + ports) is the **stable center** of each feature.
> Everything outside — entrypoints, adapters, and external systems — is **replaceable**
> and depends on the hexagon through abstractions. This is the core value of
> Hexagonal Architecture: protecting business logic from infrastructure volatility.

<p align="center">
  <img src="docs/dep_graph_basic.svg" alt="Basic Dependency Graph" />
  <br><em>Figure 3: Basic Dependency Graph</em>
</p>

## Dependency Inversion

The **dependency inversion** technique enables reversing dependencies **by
introducing an interface** between components, allowing an inner layer to
communicate with an outer layer while adhering to the Dependency Rule.

<p align="center">
  <img src="docs/dep_graph_inv_corrupted.svg" alt="Corrupted Dependency" />
  <br><em>Figure 4: <b>Corrupted</b> Dependency</em>
</p>

In this example, the Application component depends directly on the
Infrastructure component, violating the Dependency Rule. This creates
"corrupted" dependencies, where changes in the Infrastructure layer can
propagate to and unintentionally affect the Application layer.

<p align="center">
  <img src="docs/dep_graph_inv_correct.svg" alt="Correct Dependency" />
  <br><em>Figure 5: <b>Correct</b> Dependency</em>
</p>

In the correct design, the Application layer component depends on an
**abstraction (port)**, and the Infrastructure layer component **implements**
the corresponding interface. This makes the Infrastructure component an adapter
for the port, effectively turning it into a plugin for Application layer. Such a
design adheres to the **Dependency Inversion Principle (DIP)**, minimizing the
impact of infrastructure changes on core business logic.

## Dependency Injection

The idea behind **Dependency Injection** is that a component shouldn't create
the dependencies it needs but rather receive them. From this definition, it's
clear that one common way to implement DI is by passing dependencies as
arguments to the `__init__` method or functions.

But how exactly should these dependencies be initialized (and finalized)?

**DI frameworks** offer an elegant solution by automatically creating necessary
objects (while managing their **lifecycle**) and injecting them where needed.
This makes the process of dependency injection much cleaner and easier to
manage.

<p align="center">
  <img src="docs/dep_graph_inv_correct_di.svg" alt="Correct Dependency with DI" />
  <br><em>Figure 6: <b>Correct</b> Dependency <b>with DI</b></em>
</p>

FastAPI provides a built-in **DI mechanism** called
[Depends](https://fastapi.tiangolo.com/tutorial/dependencies/), which tends to
leak into different layers of the application. This creates tight coupling to
FastAPI, violating the principles of Clean Architecture, where the web framework
belongs to the outermost layer and should remain easily replaceable.

Refactoring the codebase to remove `Depends` when switching frameworks can be
unnecessarily costly. It also has
[other limitations](https://dishka.readthedocs.io/en/stable/alternatives.html#why-not-fastapi)
that are beyond the scope of this README. Personally, I prefer
[**Dishka**](https://dishka.readthedocs.io/en/stable/index.html) — a solution
that avoids these issues and remains framework-agnostic.

## CQRS

The project implements Command Query Responsibility Segregation (**CQRS**) — a
pattern that separates read and write operations into distinct paths.

- **Commands** (via interactors) handle write operations and business-critical
  reads using command gateways that work with entities and value objects.
- **Queries** are implemented through query services (similar contract to
  interactors) that use query gateways to fetch data optimized for presentation
  as query models.

This separation enables:

- Efficient read operations through specialized query gates, avoiding loading
  complete entity models.
- Performance optimization by tailoring data retrieval to specific view
  requirements.
- Flexibility to combine data from multiple models in read operations with
  minimal field selection.

# Project

## Dependency Graphs

<details>
  <summary>Application Controller - Interactor</summary>

<p align="center">
  <img src="docs/application_controller_interactor.svg" alt="Application Controller - Interactor" />
  <br><em>Figure 7: Application Controller - Interactor</em>
  </p>

In the presentation layer, a Pydantic model appears when working with FastAPI
and detailed information needs to be displayed in OpenAPI documentation. You
might also find it convenient to validate certain fields using Pydantic;
however, be cautious to avoid leaking business rules into the presentation
layer.

For request data, a plain `dataclass` is often sufficient. Unlike lighter
alternatives, it provides attribute access, which is more convenient for working
in the application layer. However, such access is unnecessary for data returned
to the client, where a `TypedDict` is sufficient (it's approximately twice as
fast to create as a dataclass with slots, with comparable access times).

</details>

<details>
  <summary>Application Interactor</summary>

<p align="center">
  <img src="docs/application_interactor.svg" alt="Application Interactor" />
  <br><em>Figure 8: Application Interactor</em>
  </p>

</details>

<details>
  <summary>Application Interactor - Adapter</summary>

<p align="center">
  <img src="docs/application_interactor_adapter.svg" alt="Application Interactor - Adapter" />
  <br><em>Figure 9: Application Interactor - Adapter</em>
  </p>

</details>

<details>
  <summary>Domain - Adapter</summary>

<p align="center">
  <img src="docs/domain_adapter.svg" alt="Domain - Adapter" />
  <br><em>Figure 10: Domain - Adapter</em>
  </p>

</details>

<details>
  <summary>Infrastructure Controller - Handler</summary>
  <p align="center">
  <img src="docs/infrastructure_controller_handler.svg" alt="Infrastructure Controller - Handler" />
  <br><em>Figure 11: Infrastructure Controller - Handler</em>
  </p>

An infrastructure handler may be required as a temporary solution in cases where
a separate context exists but isn't physically separated into a distinct domain
(e.g., not implemented as a standalone module within a monolithic application).
In such cases, the handler operates as an application-level interactor but
resides in the infrastructure layer.

Initially, I called these handlers interactors, but the community reacted very
negatively to the idea of interactors in the infrastructure layer, refusing to
acknowledge that these essentially belong to another context.

In this application, such handlers include those managing user accounts, such as
registration, login, and logout.

</details>

<details>
  <summary>Infrastructure Handler</summary>
  <p align="center">
  <img src="docs/infrastructure_handler.svg" alt="Infrastructure Handler" />
  <br><em>Figure 12: Infrastructure Handler</em>
  </p>

Ports in infrastructure are not commonly seen — typically, only concrete
implementations are present. However, in this project, since we have a separate
layer of adapters (presentation) located outside the infrastructure, ports are
necessary to comply with the dependency rule.

</details>

<details>

**Identity Provider (IdP)** abstracts authentication details, linking the main
business context with the authentication context. In this example, the
authentication context is not physically separated, making it an infrastructure
detail. However, it can potentially evolve into a separate domain.

<summary>Identity Provider</summary>
  <p align="center">
  <img src="docs/identity_provider.svg" alt="Identity Provider" />
  <br><em>Figure 13: Identity Provider</em>
  </p>

Normally, IdP is expected to provide all information about current user.
However, in this project, since roles are not stored in sessions or tokens,
retrieving them in main context was more natural.

</details>

## Structure

This project implements **Hexagonal Architecture** (Ports and Adapters) with feature-based organization. Each feature is a bounded context containing its own hexagon with clearly separated domain logic, ports (abstractions), adapters (implementations), and entrypoints.

```
.
├── config/...                                   # configuration files and Docker setup
├── Makefile                                     # development task automation
├── scripts/...                                  # utility scripts (dependency plotting, etc.)
├── pyproject.toml                               # project metadata and tooling config
└── src/
    ├── run.py                                   # application entry point
    │
    ├── common/                                  # shared cross-cutting concerns
    │   ├── adapter/                             # shared infrastructure adapters
    │   │   ├── persistence_sqla/                # SQLAlchemy session management
    │   │   │   ├── registry.py                  # SQLAlchemy registry setup
    │   │   │   └── ...
    │   │   └── exceptions/...                   # adapter-level exceptions
    │   │
    │   ├── domain/                              # shared domain building blocks
    │   │   ├── core/
    │   │   │   ├── entities/                    # base entity classes
    │   │   │   ├── value_objects/               # base value object classes
    │   │   │   └── exceptions/                  # common domain exceptions
    │   │   └── port/                            # shared port abstractions
    │   │       ├── inbound/
    │   │       │   └── queries/                 # common query interfaces
    │   │       └── outbound/                    # common outbound ports
    │   │
    │   └── entrypoint/                          # shared presentation layer
    │       ├── rest/
    │       │   ├── controllers/                 # health check, root handlers
    │       │   ├── errors/                      # error translators, handlers
    │       │   └── ...                          # FastAPI router setup
    │       └── exceptions/...                   # presentation exceptions
    │
    ├── features/                                # feature modules (bounded contexts)
    │   │
    │   ├── account/                             # account management feature
    │   │   ├── adapter/                         # infrastructure implementations
    │   │   │   ├── sqla_auth_session_gateway_session_adapter.py
    │   │   │   ├── sqla_auth_session_transaction_manager.py
    │   │   │   └── types_.py
    │   │   │
    │   │   ├── domain/                          # business logic
    │   │   │   ├── core/                        # domain model
    │   │   │   │   ├── entities/                # AuthSession entity
    │   │   │   │   └── service/                 # domain services
    │   │   │   │       ├── change_password_service.py
    │   │   │   │       ├── log_in_service.py
    │   │   │   │       ├── log_out_service.py
    │   │   │   │       └── sign_up_service.py
    │   │   │   └── port/                        # abstractions (hexagon boundary)
    │   │   │       ├── inbound/                 # use case interfaces (driving)
    │   │   │       │   ├── change_password_use_case.py
    │   │   │       │   ├── log_in_use_case.py
    │   │   │       │   ├── log_out_use_case.py
    │   │   │       │   └── sign_up_use_case.py
    │   │   │       └── outbound/                # gateway interfaces (driven)
    │   │   │           ├── auth_session_gateway.py
    │   │   │           └── auth_session_transaction_manager.py
    │   │   │
    │   │   └── entrypoint/                      # presentation layer
    │   │       ├── rest/
    │   │       │   ├── controllers/             # HTTP handlers
    │   │       │   │   ├── change_password.py
    │   │       │   │   ├── log_in.py
    │   │       │   │   ├── log_out.py
    │   │       │   │   └── sign_up.py
    │   │       │   ├── account_router.py        # FastAPI router
    │   │       │   ├── constants.py             # JWT/cookie settings
    │   │       │   └── ...                      # JWT utils, cookie handlers
    │   │       └── exceptions/...               # account-specific exceptions
    │   │
    │   └── user/                                # user management feature
    │       ├── adapter/                         # infrastructure implementations
    │       │   ├── sqla_user_repository_adapter_.py
    │       │   ├── password_hasher_bcrypt.py
    │       │   ├── identity_provider.py
    │       │   ├── access_revoker.py
    │       │   ├── mapper/                      # entity-to-model mappers
    │       │   │   ├── user.py
    │       │   │   ├── auth_session.py
    │       │   │   └── all.py
    │       │   ├── utils/                       # adapter utilities
    │       │   │   ├── user_id_generator_uuid.py
    │       │   │   ├── timer_utc.py
    │       │   │   └── ...
    │       │   └── exceptions/...               # adapter exceptions
    │       │
    │       ├── domain/                          # business logic
    │       │   ├── core/                        # domain model
    │       │   │   ├── entities/
    │       │   │   │   └── user.py              # User aggregate root
    │       │   │   ├── vo/                      # value objects
    │       │   │   │   ├── user_id.py
    │       │   │   │   ├── username.py
    │       │   │   │   ├── user_password_hash.py
    │       │   │   │   └── raw_password.py
    │       │   │   ├── enums/                   # domain enumerations
    │       │   │   │   ├── user_role.py
    │       │   │   │   └── role_hierarchy.py
    │       │   │   ├── service/                 # domain services
    │       │   │   │   ├── user_service.py      # core user business logic
    │       │   │   │   ├── current_user_service.py
    │       │   │   │   ├── create_user_service.py
    │       │   │   │   ├── activate_user_service.py
    │       │   │   │   ├── deactivate_user_service.py
    │       │   │   │   ├── grant_admin_service.py
    │       │   │   │   ├── revoke_admin_service.py
    │       │   │   │   ├── set_user_password_service.py
    │       │   │   │   ├── list_users_service.py
    │       │   │   │   └── permissions.py       # authorization logic
    │       │   │   ├── utils/                   # domain utilities
    │       │   │   │   └── authorize.py
    │       │   │   ├── exceptions/              # domain exceptions
    │       │   │   │   └── user.py
    │       │   │   └── constants.py             # domain constants
    │       │   │
    │       │   └── port/                        # abstractions (hexagon boundary)
    │       │       ├── inbound/                 # use case interfaces (driving ports)
    │       │       │   ├── create_user_use_case.py
    │       │       │   ├── activate_user_use_case.py
    │       │       │   ├── deactivate_user_use_case.py
    │       │       │   ├── grant_admin_use_case.py
    │       │       │   ├── revoke_admin_use_case.py
    │       │       │   ├── set_user_password_use_case.py
    │       │       │   └── list_users_use_case.py
    │       │       └── outbound/                # gateway interfaces (driven ports)
    │       │           ├── user_repository.py
    │       │           ├── password_hasher.py
    │       │           ├── identity_provider.py
    │       │           ├── user_id_generator.py
    │       │           ├── access_revoker.py
    │       │           └── queries/
    │       │               └── user_queries.py
    │       │
    │       └── entrypoint/                      # presentation layer
    │           └── rest/
    │               ├── controllers/             # HTTP handlers
    │               │   ├── create_user.py
    │               │   ├── activate_user.py
    │               │   ├── deactivate_user.py
    │               │   ├── grant_admin.py
    │               │   ├── revoke_admin.py
    │               │   ├── set_user_password.py
    │               │   └── list_users.py
    │               └── user_router.py           # FastAPI router
    │
    └── setup/                                   # application configuration
        ├── config/                              # settings management
        │   ├── settings.py                      # environment-based configuration
        │   ├── loader.py                        # config file loader
        │   ├── database.py                      # database settings
        │   ├── security.py                      # JWT/auth settings
        │   └── logs.py                          # logging configuration
        │
        └── ioc/                                 # dependency injection (Dishka)
            ├── provider_registry.py             # main DI container setup
            ├── domain.py                        # domain service providers
            ├── infrastructure.py                # adapter providers
            ├── entrypoint.py                    # controller providers
            ├── application.py                   # use case providers
            └── settings.py                      # config providers
```

### Key Architecture Patterns

**Hexagonal Architecture (Ports and Adapters):**
- Each feature is a **hexagon** with a clear boundary defined by ports
- **Ports** are abstractions (interfaces) that define how the domain interacts with the outside world:
  - **Inbound ports** (driving): Use case interfaces that external actors invoke
  - **Outbound ports** (driven): Gateway interfaces that the domain uses to interact with infrastructure
- **Adapters** are concrete implementations of ports that connect to external systems (databases, frameworks, etc.)
- **Domain** contains business logic and depends only on port abstractions, never on adapters

**Feature-Based Organization:**
- Business capabilities are organized into features (`account`, `user`) rather than technical layers
- Each feature is a bounded context with its own domain model, ports, adapters, and entrypoints
- Common shared concerns live in `/common` and are reused across features

**Dependency Rule:**
- Dependencies point inward: `entrypoint` → `domain/port/inbound` → `domain/core` ← `domain/port/outbound` ← `adapter`
- Domain layer has **zero dependencies** on outer layers (framework-agnostic, storage-agnostic)
- Adapters and entrypoints depend on domain ports (abstractions), not on each other

**CQRS Pattern:**
- Write operations: Commands flow through use cases → domain services → repository
- Read operations: Queries can bypass domain layer for optimized reads (see `user_queries.py`)

## Makefile Commands Reference

The project includes a comprehensive Makefile for automating common development tasks. Run `make help` to see all available commands.

### Environment Management

- `make env.local` - Print command to set APP_ENV=local (run in shell: `eval $(make env.local)`)
- `make env` - Display current APP_ENV value
- `make dotenv` - Generate .env files from config templates
- `make venv` - Create or update virtual environment using uv
- `make venv.activate` - Print command to activate virtual environment
- `make venv.deactivate` - Print command to deactivate virtual environment

### Database Management (Supabase)

- `make up.db` - Start Supabase local database
- `make up.db-echo` - Start Supabase local database with debug output
- `make down.db` - Stop Supabase local database
- `make logs.db` - Tail Supabase database container logs
- `make shell.db` - Open interactive shell inside Supabase database container

### Docker Compose (Application)

- `make up` - Start application containers in detached mode
- `make up.echo` - Start application containers in foreground (with logs)
- `make down` - Stop application containers
- `make down.total` - Stop application containers and remove volumes
- `make prune` - Clean up docker compose artifacts (stopped containers, networks, etc.)

### Code Quality

- `make code.format` - Format code using ruff
- `make code.lint` - Run linters (ruff, slotscheck, mypy)
- `make code.test` - Run pytest test suite
- `make code.cov` - Run tests with coverage and print report
- `make code.cov.html` - Run tests with coverage and generate HTML report
- `make code.check` - Run full quality check (lint + test)

### Project Utilities

- `make pycache-del` - Remove all __pycache__ directories
- `make tree` - Display project tree structure (after cleaning)
- `make plot-data` - Plot Dishka dependency injection graph
- `make help` - Display this help information

## Technology Stack

- **Python**: `3.13`
- **Core**: `bcrypt`, `dishka`, `fastapi-error-map`, `fastapi`, `orjson`,
  `psycopg[binary]`, `pyjwt[crypto]`, `sqlalchemy[mypy]`, `uuid-utils`,
  `uvicorn`, `uvloop`
- **Development**: `mypy`, `pre-commit`, `ruff`, `slotscheck`
- **Testing**: `coverage`, `line-profiler`, `pytest`, `pytest-asyncio`

## API

<p align="center">
  <img src="docs/handlers.png" alt="Handlers" />
  <br><em>Figure 14: Handlers</em>
</p>

### General

- `/` (GET): Open to **everyone**.
  - Redirects to Swagger documentation.
- `/api/v1/health` (GET): Open to **everyone**.
  - Returns `200 OK` if the API is alive.

### Account (`/api/v1/account`)

- `/signup` (POST): Open to **everyone**.
  - Registers a new user with validation and uniqueness checks.
  - Passwords are peppered, salted, and stored as hashes.
  - A logged-in user cannot sign up until the session expires or is terminated.
- `/login` (POST): Open to **everyone**.
  - Authenticates registered user, sets a JWT access token with a session ID in
    cookies, and creates a session.
  - A logged-in user cannot log in again until the session expires or is
    terminated.
  - Authentication renews automatically when accessing protected routes before
    expiration.
  - If the JWT is invalid, expired, or the session is terminated, the user loses
    authentication. [^1]
- `/password` (PUT): Open to **authenticated users**.
  - The current user can change their password.
  - New password must differ from current password.
- `/logout` (DELETE): Open to **authenticated users**.
  - Logs the user out by deleting the JWT access token from cookies and removing
    the session from the database.

### Users (`/api/v1/users`)

- `/` (POST): Open to **admins**.
  - Creates a new user, including admins, if the username is unique.
  - Only super admins can create new admins.
- `/` (GET): Open to **admins**.
  - Retrieves a paginated list of existing users with relevant information.
- `/{user_id}/password` (PUT): Open to **admins**.
  - Admins can set passwords of subordinate users.
- `/{user_id}/roles/admin` (PUT): Open to **super admins**.
  - Grants admin rights to a specified user.
  - Super admin rights cannot be changed.
- `/{user_id}/roles/admin` (DELETE): Open to **super admins**.
  - Revokes admin rights from a specified user.
  - Super admin rights cannot be changed.
- `/{user_id}/activation` (PUT): Open to **admins**.
  - Restores a previously soft-deleted user.
  - Only super admins can activate other admins.
- `/{user_id}/activation` (DELETE): Open to **admins**.
  - Soft-deletes an existing user, making that user inactive.
  - Also deletes the user's sessions.
  - Only super admins can deactivate other admins.
  - Super admins cannot be soft-deleted.

> [!NOTE]
>
> - Super admin privileges must be initially granted manually (e.g., directly in
>   the database), though the user account itself can be created through the
>   API.

## Configuration

> [!WARNING]
>
> - This part of documentation is **not** related to the architecture approach.
> - Use any configuration method you prefer.

### Files

- **config.toml**: Main application settings organized in sections
- **export.toml**: Lists fields to export to .env
  (`export.fields = ["postgres.USER", "postgres.PASSWORD", ...]`)
- **.secrets.toml**: Optional sensitive data (same format as config.toml, merged
  with main config)

> [!IMPORTANT]
>
> - This project includes secret files for demonstration purposes only. In a
>   real project, you **must** ensure that `.secrets.toml` and all `.env` files
>   are not tracked by version control system to prevent exposing sensitive
>   information. See this project's `.gitignore` for an example of how to
>   properly exclude these sensitive files from Git.

### Flow

In this project I use my own configuration system based on TOML files as the
single source of truth. The system generates `.env` files for Docker and
infrastructure components while the application reads settings directly from the
structured TOML files. More details are available at
https://github.com/ivan-borovets/toml-config-manager

<p align="center">
  <img src="docs/toml_config_manager.svg" alt="Configuration flow" />
  <br><em>Figure 15: Configuration flow </em>
  <br><small>Here, the arrows represent usage flow, <b>not dependencies.</b></small>
</p>

### Local Environment

1. Configure local environment

- In this project, local configuration is already prepared in `config/local/`.\
  Nothing needs to be created — adjust files only if you want to change
  defaults.
- If you want to adjust settings, edit the existing TOML files in
  `config/local/` directly.\
  `.env.local` will be generated automatically — **don’t** create or edit it
  manually.
- Docker Compose in this project is already configured with `APP_ENV`.\
  Just keep in mind this variable if you change the setup:

```yaml
services:
  app:
    # ...
    environment:
      APP_ENV: ${APP_ENV}
```

2. Set environment variable

```shell
export APP_ENV=local
# export APP_ENV=dev
# export APP_ENV=prod
```

3. Check it and generate `.env`

```shell
# Probably you'll need Python 3.13 installed on your system to run these commands. 
# The next code section provides commands for its fast installation.
make env  # should print APP_ENV=local
make dotenv  # should tell you where .env.local was generated
```

4. Install `uv`

```shell
# sudo apt update
# sudo apt install pipx
# pipx ensurepath
# pipx install uv
# https://docs.astral.sh/uv/getting-started/installation/#shell-autocompletion
# uv python install 3.13  # To install Python
```

5. Set up virtual environment

```shell
uv sync --group dev
source .venv/bin/activate

# Alternatively,
# uv v
# source .venv/bin/activate  # on Unix
# .venv\Scripts\activate  # on Windows
# uv pip install -e . --group dev
```

Don't forget to tell your IDE where the interpreter is located.

Install pre-commit hooks:

```shell
# https://pre-commit.com/
pre-commit install
```

6. Launch

- To run only the database in Docker and use the app locally, use the following
  command:

  ```shell
  make up.db
  # make up.db-echo
  ```

- Then, start Supabase and apply migrations:
  ```shell
  supabase start
  # Migrations are automatically applied when Supabase starts
  ```

- After Supabase is running, the database is ready, and you can launch the
  application locally (e.g., through your IDE). Remember to set the `APP_ENV`
  environment variable in your IDE's run configuration.

- To run via Docker Compose:

  ```shell
  make up
  # make up.echo
  ```

  In this case, migrations will be applied automatically at startup.

7. Shutdown

- To stop the containers, use:
  ```shell
  make down
  ```

### Other Environments (dev/prod)

1. Use the instructions about [local environment](#local-environment) above

- But make sure you've created similar structure in `config/dev` or
  `config/prod` with [files](#files):
  - `config.toml`
  - `.secrets.toml`
  - `export.toml`
  - `docker-compose.yaml` if needed
- `.env.dev` or `.env.prod` to be generated later — **don't** create them
  manually

### Adding New Environments

1. Add new value to `ValidEnvs` enum in `config/toml_config_manager.py` (and
   maybe in your app settings)
2. Update `ENV_TO_DIR_PATHS` mapping in the same file (and maybe in your app
   settings)
3. Create corresponding directory in `config/` folder
4. Add required configuration [files](#files)

Environment directories can also contain other env-specific files like
`docker-compose.yaml`, which will be used by Makefile commands.

# Useful Resources

## Layered Architecture

- [Robert C. Martin. Clean Architecture: A Craftsman's Guide to Software Structure and Design. 2017](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)

- [Alistair Cockburn. Hexagonal Architecture Explained. 2024](https://www.amazon.com/Hexagonal-Architecture-Explained-Alistair-Cockburn-ebook/dp/B0D4JQJ8KD)
  (introduced in 2005)

## Domain-Driven Design

- [Vlad Khononov. Learning Domain-Driven Design: Aligning Software Architecture and Business Strategy. 2021](https://www.amazon.com/Learning-Domain-Driven-Design-Aligning-Architecture/dp/1098100131)

- [Vaughn Vernon. Implementing Domain-Driven Design. 2013](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)

- [Eric Evans. Domain-Driven Design: Tackling Complexity in the Heart of Software. 2003](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)

- [Martin Fowler. Patterns of Enterprise Application Architecture. 2002](https://www.amazon.com/Patterns-Enterprise-Application-Architecture-Martin/dp/0321127420)

## Adjacent

- [Vladimir Khorikov. Unit Testing Principles. 2020](https://www.amazon.com/Unit-Testing-Principles-Practices-Patterns/dp/1617296279)

# ⭐ Support the Project

If you find this project useful, please give it a star or share it! Your support
means a lot.

👉 Check out the amazing
[fastapi-error-map](https://github.com/ivan-borovets/fastapi-error-map), used
here to enable contextual, per-route error handling with automatic OpenAPI
schema generation.

💬 Feel free to open issues, ask questions, or submit pull requests.

# Acknowledgements

I would like to express my sincere gratitude to the following individuals for
their valuable ideas and support in satisfying my curiosity throughout the
development of this project: [igoryuha](https://github.com/igoryuha),
[tishka17](https://github.com/tishka17),
[chessenjoyer17](https://github.com/chessenjoyer17),
[PlzTrustMe](https://github.com/PlzTrustMe),
[Krak3nDev](https://github.com/Krak3nDev),
[Ivankirpichnikov](https://github.com/Ivankirpichnikov),
[SamWarden](https://github.com/SamWarden),
[nkhitrov](https://github.com/nkhitrov),
[ApostolFet](https://github.com/ApostolFet), Lancetnik, Sehat1137, Maclovi.

I also greatly appreciate the valuable insights shared by participants of the
ASGI Community Telegram chat, despite frequent and lively communication
challenges, as well as the ⚗️ Reagento (adaptix/dishka)
[Telegram chat](https://t.me/reagento_ru) for their thoughtful discussions and
generous knowledge exchange.

# Todo

- [x] set up CI
- [x] simplify settings
- [x] simplify annotations
- [ ] add integration tests
- [ ] explain design choices

[^1]: Session and token share the same expiry time, avoiding database reads if
    the token is expired. This scheme of using JWT **is not** related to OAuth
    2.0 and is a custom micro-optimization.
