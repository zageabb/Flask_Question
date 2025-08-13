# Design Specification: Template-Based Form System Integration

## Overview
This document outlines the design for integrating a template-driven form
system, prototyped in this repository, into the existing application. The
goal is to allow non‑developers to define forms as JSON templates, upload them
through the UI, and capture user responses in the main system database.

## Objectives
1. **Extend the master record**: add fields that capture which template was
   used and the completed form data.
2. **Template management UI**: provide pages to upload and maintain form
   templates.
3. **Dynamic form pages**: render forms based on uploaded templates and display
   submitted data.

## Data Model Changes
To store forms in the existing master record, add the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `template_name` | string | Identifier for the template used to render the form. |
| `form_json` | text | JSON payload containing the user's responses. |
| `timestamp` | datetime | When the form was submitted. |

These fields mirror the prototype's `completed_forms` table and enable the
main system to reconstruct a submitted form at any time.

## Template Management
Templates are JSON files describing form fields and metadata. Example:

```json
{
  "name": "ExampleForm",
  "description": "A sample form template",
  "fields": [
    {"label": "Name", "type": "text"},
    {"label": "Age", "type": "number"},
    {"label": "Favorite Color", "type": "dropdown", "options": ["Red", "Green", "Blue"]}
  ]
}
```

Planned pages:

1. **Template List** – lists all templates and links to fill or edit them.
2. **Upload Template** – allows JSON files to be uploaded and stored on the
   server.
3. **Edit Template** – shows the JSON for an existing template and saves edits.

## Form Execution Flow
1. **User selects a template** from the Template List page.
2. **Dynamic form render** – fields from the template are used to construct an
   HTML form.
3. **Submission** – on submit, responses are serialized to JSON and stored in
   the master record fields described above.
4. **View/Edit Completed Forms** – index pages list past submissions and allow
   viewing or editing existing data.

## Integration Considerations
- **Authentication/Authorization**: restrict template management and form
  access as appropriate for the existing system.
- **Validation**: validate uploaded JSON and user input to prevent malformed
  forms.
- **Versioning**: if templates can change, consider versioning to preserve old
  submissions.

## Summary
By extending the master record and adding template management and form display
pages, the existing system gains a flexible mechanism for introducing new data
collection workflows without code changes.
