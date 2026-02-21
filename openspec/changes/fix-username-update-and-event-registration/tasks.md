## 1. Event Type Registration

- [ ] 1.1 Add `register_event(*event_types)` function to `src/shared/infrastructure/events/registry.py` that inserts each event class into `_event_type_registry` by `__name__`
- [ ] 1.2 Apply `@register_event` to `ProfileCreated` and `UsernameChanged` in `src/core/domain/profile/events.py`

## 2. Profile Repository Upsert

- [ ] 2.1 Change `SqlaProfileRepository.save()` in `src/core/infrastructure/persistence/sqla_profile_repository.py` to use `self._session.merge(record)` instead of `self._session.add(record)`

## 3. Set Username Handler Fix

- [ ] 3.1 Add `self._profile_repository.save(profile)` call in `SetUsernameHandler.execute()` in `src/core/application/set_username/handler.py`, after `profile.set_username(username)` and before `event_dispatcher.dispatch()`

## 4. Tests

- [ ] 4.1 Add unit test for `register_event` decorator: verify `get_event_class` returns the class and `get_handlers_for` returns empty list
- [ ] 4.2 Add/update unit test for `SqlaProfileRepository.save()`: verify it works for both new and existing profiles (upsert semantics)
- [ ] 4.3 Add/update unit test for `SetUsernameHandler`: verify `save()` is called and username is persisted
- [ ] 4.4 Run full test suite and confirm all tests pass
