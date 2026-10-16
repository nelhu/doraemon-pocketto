# Interactive Visuals and Mockups

## Model the interaction first

Write down:

1. The state the user can change.
2. The visible consequence of that change.
3. The insight the change should reveal.

If one of these is missing, remove the control. Keep state local to the fragment unless the user explicitly needs a Codex follow-up.

## Controls and simulation

- Use semantic inputs, labels, buttons, and output regions.
- Initialize controls to a useful, representative state.
- Keep one source of truth for each state value and update all dependent text and graphics together.
- Constrain ranges to meaningful values and show units next to the control.
- Add Reset only when the state space is large enough to need it.
- Explain assumptions and simplified rules near the simulation.
- Distinguish computed output from source facts and from hypothetical scenarios.
- Respect `prefers-reduced-motion` and offer a manual step or pause when continuous motion matters.

## UI mockups

- Treat a mockup as an explanatory model, not a production implementation.
- Reproduce only screens and states supported by the user's description or source material.
- Use realistic hierarchy and content density, but do not invent KPIs, permissions, success states, or product capabilities.
- Make interactive hotspots visually discoverable and keyboard operable.
- If the user wants production UI, leave this skill and modify the project under its own design and engineering rules.

## Codex follow-ups

Use `window.openai.sendFollowUpMessage` only when a control intentionally turns the selected state into a new user request. Keep local inspection local. Provide a visible unavailable, pending, success, and failure state; prevent accidental duplicate sends.

## 3D

Use 3D only when depth, rotation, occlusion, or spatial arrangement is the mechanism being explained. Prefer an annotated 2D view for architecture, rankings, ordinary relationships, and decorative scenes.

When 3D is justified:

- Give the first camera position a useful view.
- Provide obvious orbit/reset controls and keyboard-accessible alternatives.
- Cap device pixel ratio and pause expensive rendering when the fragment is not visible.
- Use host-derived colors and a neutral background.
- Provide a text or 2D fallback that communicates the same main conclusion.

## QA

- Test every primary control from its default state.
- Confirm state, labels, graphics, and accessible summaries never drift apart.
- Confirm rapid input and repeated clicks do not create duplicate listeners or requests.
- Confirm the useful first render and core explanation survive when scripting or host follow-up is unavailable.
