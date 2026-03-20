# MiScore JSON Structure

This document describes the full JSON schema used by MiScore for storing gaming records.

## Top-Level Structure

```json
{
  "games": [
    {
      "name": "Game Name",
      "difficulties": ["Easy", "Normal", "Hard"],
      "record_types": [...]
    }
  ]
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `games` | array | yes | List of game objects |

## Game Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Name of the game |
| `difficulties` | array of strings | no | Available difficulty levels |
| `record_types` | array | no | List of record type objects |

## Record Type Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Display name for this record type |
| `description` | string | no | Description of this record type |
| `type` | string | yes | One of the record type options (see below) |
| `components` | array of strings | no | Required when `type` is `"complex"`. Lists which record type attributes to combine. |
| `records` | array | no | List of record entries |

### Record Type Options

| Type | Description | Entry Fields |
|------|-------------|-------------|
| `completed` | Track game completions | date, description, screenshot |
| `completed_at_difficulty` | Track completions at specific difficulties | date, difficulty, description, screenshot |
| `fastest_time` | Track best speed runs | date, time, description, screenshot |
| `longest_time` | Track longest playthroughs | date, time, description, screenshot |
| `high_score` | Track highest scores | date, score, description, screenshot |
| `low_score` | Track lowest scores | date, score, description, screenshot |
| `complex` | Combine multiple record type attributes | date + fields from components, description, screenshot |

## Record Entry Fields

All record entries share these base fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string (YYYY-MM-DD) | yes | Date of the achievement |
| `description` | string | no | Description of the achievement |
| `screenshot` | string (file path) | no | Path to a screenshot file, relative to the JSON file |

### Type-Specific Fields

| Field | Type | Used By |
|-------|------|---------|
| `difficulty` | string | `completed_at_difficulty`, `complex` (with `completed_at_difficulty` component) |
| `time` | string (HH:MM:SS) | `fastest_time`, `longest_time`, `complex` (with time component) |
| `score` | number | `high_score`, `low_score`, `complex` (with score component) |

## Examples

### Completed Record

```json
{
  "name": "Game Completion",
  "type": "completed",
  "records": [
    { "date": "2024-01-15" }
  ]
}
```

### Completed at Difficulty Record

```json
{
  "name": "Difficulty Completion",
  "type": "completed_at_difficulty",
  "records": [
    { "date": "2024-01-15", "difficulty": "Hard" }
  ]
}
```

### Time Record

```json
{
  "name": "Speed Run",
  "type": "fastest_time",
  "records": [
    { "date": "2024-01-15", "time": "01:23:45" }
  ]
}
```

### Score Record

```json
{
  "name": "High Score",
  "type": "high_score",
  "records": [
    { "date": "2024-01-15", "score": 99999 }
  ]
}
```

### Complex Record

A complex record type combines attributes from multiple record types using the `components` field.

**Difficulty + Time:**

```json
{
  "name": "Difficulty Speedrun",
  "type": "complex",
  "components": ["completed_at_difficulty", "fastest_time"],
  "records": [
    { "date": "2024-01-15", "difficulty": "Nightmare", "time": "02:15:30" }
  ]
}
```

**Difficulty + Score:**

```json
{
  "name": "Difficulty High Score",
  "type": "complex",
  "components": ["completed_at_difficulty", "high_score"],
  "records": [
    { "date": "2024-01-15", "difficulty": "Hard", "score": 50000 }
  ]
}
```

**Difficulty + Time + Score:**

```json
{
  "name": "Full Run",
  "type": "complex",
  "components": ["completed_at_difficulty", "fastest_time", "high_score"],
  "records": [
    { "date": "2024-01-15", "difficulty": "Hard", "time": "01:30:00", "score": 50000 }
  ]
}
```

### Component Rules

- `components` is required when `type` is `"complex"` and must contain at least one entry
- `components` must not be set on non-complex record types
- `"complex"` and `"completed"` are not valid component values
- Each component adds required fields to the record entries:
  - `completed_at_difficulty` requires `difficulty`
  - `fastest_time` / `longest_time` requires `time`
  - `high_score` / `low_score` requires `score`
- Difficulty values in complex records are validated against the game's `difficulties` list
