## 1. Shared Domain: UNSET Sentinel

- [ ] 1.1 Create `shared/domain/unset.py` with `_Unset` class, `UNSET` singleton, and exported type alias

## 2. Domain Layer: Event + Aggregate Method

- [ ] 2.1 Add `ProfilePatchApplied` frozen dataclass to `core/domain/profile/events.py` with `profile_id` and four optional delta tuple fields (`first_name`, `last_name`, `birth_date`, `username`)
- [ ] 2.2 Add `apply_patch()` method to `Profile` aggregate in `core/domain/profile/entity.py` accepting `_Unset`-defaulted value object params, mutating only changed fields, and registering `ProfilePatchApplied`

## 3. Application Layer: Patch Use Case

- [ ] 3.1 Create `core/application/patch_profile/command.py` — `PatchProfileCommand` frozen dataclass with all four fields defaulting to `UNSET`
- [ ] 3.2 Create `core/application/patch_profile/port.py` — `PatchProfileUseCase` protocol
- [ ] 3.3 Create `core/application/patch_profile/handler.py` — `PatchProfileHandler` that loads profile, builds value objects for non-UNSET fields, calls `profile.apply_patch()`, saves, dispatches events, commits

## 4. Infrastructure: Wire PATCH Endpoint

- [ ] 4.1 Update `core/infrastructure/http/controllers/update_profile.py` — inject `PatchProfileUseCase` into `update_profile_patch`, build `PatchProfileCommand` using `body.model_fields_set` to detect provided fields
- [ ] 4.2 Register `PatchProfileHandler` in `shared/infrastructure/config/di/application.py`

## 5. Tests

- [ ] 5.1 Unit test `Profile.apply_patch()` — partial mutation, UNSET skip, explicit None clear, no-op, event delta
- [ ] 5.2 Unit test `PatchProfileHandler` — only provided fields updated, no-op, profile-not-found error
- [ ] 5.3 Unit test PATCH HTTP controller — correct command built from `model_fields_set`, 204 response
