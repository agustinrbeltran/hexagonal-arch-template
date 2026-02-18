## Context

The README.md is a large document (~2080 lines) structured as both an architecture guide and project documentation. It was written when the project used cookie-based session authentication with an `AuthSession` domain aggregate. The codebase has since transitioned to JWT access tokens + server-side refresh tokens, with auth logic moved from the domain layer to infrastructure.

The README contains interleaved sections — some purely about architectural concepts (still accurate) and some about project-specific implementation (outdated). The challenge is surgically updating the implementation-specific content without disturbing the conceptual/educational content that remains valid.

## Goals / Non-Goals

**Goals:**
- Update all sections that reference the removed `AuthSession` domain aggregate
- Document the current JWT + refresh token authentication mechanism
- Update API endpoint documentation to reflect current routes
- Update the project structure tree to match current file layout
- Update code examples to match current implementation
- Keep the document consistent — no section should contradict another

**Non-Goals:**
- Rewriting the architectural principles sections (they're still valid)
- Changing the README structure or adding new major sections
- Updating diagrams/SVGs (those are separate image files, not inline)
- Adding documentation for features not yet implemented

## Decisions

### 1. Section-by-section editing approach
Edit each README section independently rather than rewriting the entire file. This preserves the educational content and voice while updating implementation details.

**Sections requiring updates (by line range):**
1. **Aggregate descriptions** (~L108-223): Remove AuthSession aggregate, update to show only User aggregate
2. **Application layer examples** (~L226-319): Update LogInHandler example to show token pair issuance
3. **Infrastructure layer examples** (~L323-405): Update to show JWT/refresh token infrastructure
4. **DDD Patterns - Aggregates** (~L418-492): Remove AuthSession from aggregate listing
5. **Domain Events** (~L494-557): Remove session events, keep user events
6. **Request Flow** (~L1106-1370): Rewrite to show JWT-based flow
7. **Project Structure tree** (~L1576-1693): Update to reflect current files
8. **API endpoints** (~L1782-1847): Remove logout, add refresh, update auth descriptions
9. **Configuration** (~L1848-end): Add JWT settings details

### 2. AuthSession references → Refresh token infrastructure
Wherever AuthSession is mentioned as a domain concept, replace with an explanation that auth tokens are an infrastructure concern. The key narrative shift: the domain layer now contains only the User aggregate; authentication tokens are handled entirely in infrastructure.

### 3. Code example updates
Update inline code examples to match actual current code. Read the actual files and use real (or close-to-real) snippets rather than fabricated examples.

## Risks / Trade-offs

- **Risk**: Inline code examples may drift again as code evolves → Mitigation: Keep examples minimal and focused on patterns, not exact implementation
- **Risk**: Some SVG diagrams still reference old architecture → Mitigation: Out of scope for this change; note in the README that diagrams are conceptual
- **Trade-off**: README is already long (~2080 lines); updating rather than trimming keeps it long but avoids losing educational value
