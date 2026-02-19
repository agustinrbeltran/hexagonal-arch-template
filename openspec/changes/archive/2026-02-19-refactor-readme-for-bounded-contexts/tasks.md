## 1. Remove Outdated Assets

- [x] 1.1 Delete `docs/handlers.png` from the repository
- [x] 1.2 Remove the `handlers.png` image reference and its figure caption from README.md (Figure 14)

## 2. Update Overview and Introduction

- [x] 2.1 Update the opening paragraph to describe bounded-context-first organization instead of layer-based
- [x] 2.2 Update "About This Template" section to mention Account/Profile aggregates and bounded contexts
- [x] 2.3 Update "Layer-Based DDD Architecture" section header and content to reflect bounded-context-first with layers inside each context

## 3. Update Domain Layer Documentation

- [x] 3.1 Replace all `User` aggregate references with `Account` and `Profile` aggregates
- [x] 3.2 Update the "Aggregates in this project" list: `account/domain/account/` (Account BC) and `core/domain/profile/` (Core BC)
- [x] 3.3 Update value object examples: `UserId` → `AccountId`, `Username` → `Email` (Account) + `Username` (Profile), `UserPasswordHash` → `AccountPasswordHash`
- [x] 3.4 Update domain events list: `UserCreated` → `AccountCreated`, `UserActivated` → `AccountActivated`, `UserRoleChanged` → `AccountRoleChanged`, add `ProfileCreated`, `UsernameChanged`
- [x] 3.5 Update repository interface example to show `AccountRepository` instead of `UserRepository`
- [x] 3.6 Update domain services example to show `AccountService` instead of `UserService`
- [x] 3.7 Replace the `User` entity code example with `Account` entity from actual codebase
- [x] 3.8 Update the aggregate boundaries ASCII diagram to show both Account and Profile aggregates

## 4. Add Cross-Context Integration Documentation

- [x] 4.1 Add a section documenting cross-context communication via domain events (Account BC → `AccountCreated` event → Core BC `CreateProfileOnAccountCreated` handler)
- [x] 4.2 Update the domain events flow diagram to show cross-context event handling

## 5. Update Application Layer Documentation

- [x] 5.1 Update use case examples to reference Account-based handlers (e.g., `CreateAccountHandler` instead of `CreateUserHandler`)
- [x] 5.2 Update command/handler code examples with current Account naming

## 6. Update Infrastructure Layer Documentation

- [x] 6.1 Update repository implementation example to show `SqlaAccountRepository` instead of `SqlaUserRepository`
- [x] 6.2 Update HTTP controller example to reference Account-based routes
- [x] 6.3 Update security implementation references (e.g., `account_id_generator` instead of `user_id_generator_uuid`)

## 7. Update Project Structure Tree

- [x] 7.1 Replace the entire project structure tree with the actual bounded-context-first layout (`src/account/`, `src/core/`, `src/shared/`)
- [x] 7.2 Update the "Key Architecture Patterns" summary beneath the tree

## 8. Update API Section

- [x] 8.1 Replace "Account (`/api/v1/account`)" section with "Accounts (`/api/v1/accounts`)" reflecting all current account endpoints
- [x] 8.2 Replace "Users (`/api/v1/users`)" section with "Profiles (`/api/v1/profiles`)" reflecting profile endpoints (get_my_profile, set_username, list_profiles)
- [x] 8.3 Update endpoint descriptions for any changed behavior (e.g., account creation returns account_id, not user_id)

## 9. Update DDD Tactical Patterns Deep Dive

- [x] 9.1 Update Aggregates section code examples to use Account entity
- [x] 9.2 Update Domain Events section with `AccountCreated`, `AccountActivated`, `AccountRoleChanged`, `ProfileCreated` examples
- [x] 9.3 Update Value Objects section with `Email` and `AccountPasswordHash` examples
- [x] 9.4 Update Repository Pattern section with `AccountRepository` protocol and `SqlaAccountRepository`
- [x] 9.5 Update Domain Services section with current Account service code
- [x] 9.6 Update Application Services section with a current Account handler example
- [x] 9.7 Update the "When to Use Which Pattern" decision tree to reference Account/Profile instead of User

## 10. Update Request Flow Example

- [x] 10.1 Update the request flow ASCII diagrams to reference Account-based entities and services
- [x] 10.2 Update the "Detailed Flow with Code" examples with current Account naming
- [x] 10.3 Update the "Data Flow" diagram with Account naming

## 11. Final Consistency Pass

- [x] 11.1 Search for any remaining references to `User`, `user_`, `domain/user/`, `UserRepository`, `UserService` and replace with appropriate Account/Profile equivalents
- [x] 11.2 Verify Table of Contents links still work after section renames
- [x] 11.3 Renumber all figure references after handlers.png removal
