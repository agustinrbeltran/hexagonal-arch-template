## 1. Remove Outdated Assets

- [ ] 1.1 Delete `docs/handlers.png` from the repository
- [ ] 1.2 Remove the `handlers.png` image reference and its figure caption from README.md (Figure 14)

## 2. Update Overview and Introduction

- [ ] 2.1 Update the opening paragraph to describe bounded-context-first organization instead of layer-based
- [ ] 2.2 Update "About This Template" section to mention Account/Profile aggregates and bounded contexts
- [ ] 2.3 Update "Layer-Based DDD Architecture" section header and content to reflect bounded-context-first with layers inside each context

## 3. Update Domain Layer Documentation

- [ ] 3.1 Replace all `User` aggregate references with `Account` and `Profile` aggregates
- [ ] 3.2 Update the "Aggregates in this project" list: `account/domain/account/` (Account BC) and `core/domain/profile/` (Core BC)
- [ ] 3.3 Update value object examples: `UserId` → `AccountId`, `Username` → `Email` (Account) + `Username` (Profile), `UserPasswordHash` → `AccountPasswordHash`
- [ ] 3.4 Update domain events list: `UserCreated` → `AccountCreated`, `UserActivated` → `AccountActivated`, `UserRoleChanged` → `AccountRoleChanged`, add `ProfileCreated`, `UsernameChanged`
- [ ] 3.5 Update repository interface example to show `AccountRepository` instead of `UserRepository`
- [ ] 3.6 Update domain services example to show `AccountService` instead of `UserService`
- [ ] 3.7 Replace the `User` entity code example with `Account` entity from actual codebase
- [ ] 3.8 Update the aggregate boundaries ASCII diagram to show both Account and Profile aggregates

## 4. Add Cross-Context Integration Documentation

- [ ] 4.1 Add a section documenting cross-context communication via domain events (Account BC → `AccountCreated` event → Core BC `CreateProfileOnAccountCreated` handler)
- [ ] 4.2 Update the domain events flow diagram to show cross-context event handling

## 5. Update Application Layer Documentation

- [ ] 5.1 Update use case examples to reference Account-based handlers (e.g., `CreateAccountHandler` instead of `CreateUserHandler`)
- [ ] 5.2 Update command/handler code examples with current Account naming

## 6. Update Infrastructure Layer Documentation

- [ ] 6.1 Update repository implementation example to show `SqlaAccountRepository` instead of `SqlaUserRepository`
- [ ] 6.2 Update HTTP controller example to reference Account-based routes
- [ ] 6.3 Update security implementation references (e.g., `account_id_generator` instead of `user_id_generator_uuid`)

## 7. Update Project Structure Tree

- [ ] 7.1 Replace the entire project structure tree with the actual bounded-context-first layout (`src/account/`, `src/core/`, `src/shared/`)
- [ ] 7.2 Update the "Key Architecture Patterns" summary beneath the tree

## 8. Update API Section

- [ ] 8.1 Replace "Account (`/api/v1/account`)" section with "Accounts (`/api/v1/accounts`)" reflecting all current account endpoints
- [ ] 8.2 Replace "Users (`/api/v1/users`)" section with "Profiles (`/api/v1/profiles`)" reflecting profile endpoints (get_my_profile, set_username, list_profiles)
- [ ] 8.3 Update endpoint descriptions for any changed behavior (e.g., account creation returns account_id, not user_id)

## 9. Update DDD Tactical Patterns Deep Dive

- [ ] 9.1 Update Aggregates section code examples to use Account entity
- [ ] 9.2 Update Domain Events section with `AccountCreated`, `AccountActivated`, `AccountRoleChanged`, `ProfileCreated` examples
- [ ] 9.3 Update Value Objects section with `Email` and `AccountPasswordHash` examples
- [ ] 9.4 Update Repository Pattern section with `AccountRepository` protocol and `SqlaAccountRepository`
- [ ] 9.5 Update Domain Services section with current Account service code
- [ ] 9.6 Update Application Services section with a current Account handler example
- [ ] 9.7 Update the "When to Use Which Pattern" decision tree to reference Account/Profile instead of User

## 10. Update Request Flow Example

- [ ] 10.1 Update the request flow ASCII diagrams to reference Account-based entities and services
- [ ] 10.2 Update the "Detailed Flow with Code" examples with current Account naming
- [ ] 10.3 Update the "Data Flow" diagram with Account naming

## 11. Final Consistency Pass

- [ ] 11.1 Search for any remaining references to `User`, `user_`, `domain/user/`, `UserRepository`, `UserService` and replace with appropriate Account/Profile equivalents
- [ ] 11.2 Verify Table of Contents links still work after section renames
- [ ] 11.3 Renumber all figure references after handlers.png removal
