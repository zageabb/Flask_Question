# Design Specification: Template-Based Form System Integration

## Overview
This document describes the current design of the template‑driven form system
implemented in this repository.  Non‑developers can define form structures as
JSON templates, upload or edit those templates through a management interface,
and have end users complete the resulting forms.  Submissions are stored in a
database so they can be queried, viewed, or edited later.  The goal of this
document is to capture the system as it exists today and provide verbose
explanations of the major components.

## Objectives
1. **Extend the master record** – each submitted form is stored with enough
   metadata to recreate it later, including the template name and raw response
   JSON.
2. **Template management UI** – the application exposes pages for uploading new
   templates or editing existing ones.  When a template file is modified, all
   templates are reloaded so changes are immediately reflected in the UI.
3. **Dynamic form pages** – end‑user forms are generated directly from the JSON
   template definitions.  Completed entries can be viewed or edited at any
   time, even if the underlying template has evolved since the original
   submission.
4. **Programmatic access** – a REST API exposes both the master question bank
   and completed forms for integration with other systems.

## Data Model
Submitted forms are persisted in a SQLite database (`forms.db`).  The table is
represented both by raw `sqlite3` usage and by a SQLAlchemy model so that the
web UI and the API share the same storage.  The schema is:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Primary key for the completed form record. |
| `template_name` | string | Identifier for the template used to render the form. |
| `timestamp` | string | ISO8601 timestamp when the form was submitted. |
| `form_json` | text | JSON payload containing the user's responses. |

These fields mirror the prototype's `completed_forms` table and allow the
system to reconstruct or export a submission at any time.  Additional tables in
the database hold a bank of reusable **questions**, which are exposed through
the REST API but are not directly tied to the template mechanism.

## Template Format and Lifecycle
Templates are plain JSON files stored under `forms/`.  The `template_loader`
module scans this directory at startup and converts each file into an in-memory
dictionary keyed by template name.  Each template typically contains:

- `id` (or `name`): unique identifier for the template. If omitted, the file
  name is used.
- `description` (optional): human-readable details about the form's purpose.
- `fields`: ordered list of field definitions.

Every field definition supports the following keys:

- `label`: user-facing label and key used to store the response.
- `type`: input type. Supported values include `text`, `number`, `dropdown`,
  `textarea`, and `info` for instructional text blocks.
- `options` (array): list of allowed values for `dropdown` fields.
- `help` (string, optional): hint text displayed to the user.
- `text` (string, for `info` fields): explanatory message shown on the form.

Example template:

```json
{
  "id": "ExampleForm",
  "description": "A sample form template",
  "fields": [
    {"label": "Intro", "type": "info", "text": "Thanks for taking our survey."},
    {"label": "Name", "type": "text", "help": "Enter your full name"},
    {"label": "Age", "type": "number", "help": "Age in years"},
    {"label": "Favorite Color", "type": "dropdown", "options": ["Red", "Green", "Blue"], "help": "Select a color"},
    {"label": "Comments", "type": "textarea"}
  ]
}
```

### Template Management Pages
Three primary pages support template maintenance:

1. **Template List** – enumerates all templates currently loaded and provides
   links for filling out or editing each one.
2. **Upload Template** – allows a JSON file to be uploaded to the `forms`
   directory.  After upload, templates are reloaded so the new definition is
   immediately available.
3. **Edit Template** – renders each field in a structured editor so labels,
   types, UOM values, dropdown options, help text, and the instructional text
   for `info` blocks can be modified directly.  When a user saves changes the
   client-side script rebuilds the JSON payload, writes it back to disk, and
   reloads every template into memory.

The editor keeps a hidden `<textarea>` synced with the visible controls so the
full JSON document can be rewritten on submit.  When a field's type switches to
`info`, JavaScript reveals a dedicated multiline "Info text" control bound to
the field's `text` attribute, ensuring instructional copy can be reviewed or
updated alongside labels, options, and help text.

## Form Rendering and Submission Flow
1. **User selects a template** from the Template List page.
2. **Dynamic form render** – the selected template's `fields` array is used to
   build an HTML form.  Input types, help text, and dropdown options come
   directly from the template.
3. **Submission** – on submit, responses are serialized to JSON along with the
   template name and an ISO8601 timestamp.  This data is written to the
   `completed_forms` table.
4. **View Completed Forms** – submissions are listed on the index page and can
   be viewed in a read‑only format.
5. **Edit Completed Forms** – when editing an existing entry the application
   reloads the corresponding template from disk and merges its field list with
   the stored responses.  If new fields were added to the template after the
   original submission, they appear in the edit form with empty defaults so the
   record can be brought up to date.

## REST API
The `api` blueprint exposes a JSON API with optional API‑key protection.  It
provides endpoints to:

- List or retrieve individual **questions** stored in the database.
- List, retrieve, or export as CSV the **completed form** records.

This API enables external systems to consume template metadata or completed
submissions without scraping the UI.

## Integration Considerations
- **Authentication/Authorization** – restrict template management, API access,
  and completed-form editing as appropriate for the hosting environment.
- **Validation** – uploaded JSON templates are parsed to ensure validity; user
  input should be validated to prevent malformed data.
- **Versioning** – because templates can evolve over time, consider storing a
  template version with each submission to preserve historical context.

## Summary
The template-driven architecture allows new data-collection workflows to be
introduced without code changes.  By storing a template name and JSON payload
for each submission, reloading templates from disk whenever edits occur, and
exposing both a management UI and a REST API, the system provides a flexible
foundation for building and maintaining custom forms.
