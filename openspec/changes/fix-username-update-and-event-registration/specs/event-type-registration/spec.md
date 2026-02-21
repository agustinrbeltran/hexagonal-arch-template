## ADDED Requirements

### Requirement: register_event decorator for independent event type registration
The system SHALL provide a `register_event(*event_types: type[DomainEvent])` callable in `shared/infrastructure/events/registry.py`. When used as a class decorator on a `DomainEvent` subclass (or called with event classes directly), it SHALL insert each event type into `_event_type_registry` keyed by `event_type.__name__`, without registering any handler. This allows the outbox relay to deserialize events that have no in-process handler.

#### Scenario: Decorated event class is registered at import time
- **WHEN** a `DomainEvent` subclass is decorated with `@register_event`
- **THEN** `get_event_class(event_class.__name__)` returns that class

#### Scenario: Event with no handler is deserializable
- **GIVEN** `UsernameChanged` is decorated with `@register_event` and has no `@handles` handler
- **WHEN** the outbox relay calls `deserialize_event("UsernameChanged", payload)`
- **THEN** deserialization succeeds and returns a `UsernameChanged` instance

#### Scenario: register_event does not register a handler
- **GIVEN** `UsernameChanged` is decorated with `@register_event`
- **WHEN** `get_handlers_for(UsernameChanged)` is called
- **THEN** an empty list is returned

#### Scenario: @handles still registers event type in registry
- **GIVEN** `@handles(AccountCreated)` is applied to a handler class
- **WHEN** `get_event_class("AccountCreated")` is called
- **THEN** the `AccountCreated` class is returned (existing behaviour unchanged)

#### Scenario: Event type registered by both @register_event and @handles
- **GIVEN** an event class decorated with `@register_event` AND a handler decorated with `@handles` for the same event
- **WHEN** `get_event_class` and `get_handlers_for` are called
- **THEN** both return the correct values without conflict
