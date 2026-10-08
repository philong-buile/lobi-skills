<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/banner-dark.svg">
  <img alt="{{NAME}}: {{TAGLINE}}" src="./assets/banner-light.svg" width="100%">
</picture>

<p>
  <a href="./LICENSE"><img alt="License: {{LICENSE}}" src="https://img.shields.io/badge/license-{{LICENSE}}-{{ACCENT_HEX}}?style=flat-square"></a>
  <img alt="{{ECOSYSTEM}}" src="https://img.shields.io/badge/{{ECOSYSTEM_LEFT}}-{{ECOSYSTEM_RIGHT}}-3f3f46?style=flat-square">
  <img alt="{{COUNT}} {{UNIT}}" src="https://img.shields.io/badge/{{UNIT}}-{{COUNT}}-3f3f46?style=flat-square">
</p>

{{One or two sentences: what it does, and why someone would want it.}}

## Install

```bash
{{install command}}
```

## {{Features | Skills | Packages}}

| Name | What you get | Runs where / needs |
| --- | --- | --- |
| [`{{name}}`]({{path to doc}}) | {{outcome in plain words}} | {{where}} |

{{One line introducing the examples:}}

```text
{{example 1}}
{{example 2}}
{{example 3}}
```

## How it works

```mermaid
flowchart LR
  A["{{step}}"] --> B["{{step}}"] --> C["{{step}}"]
```

{{One paragraph about guarantees: what it never does, where output goes.}}

## Configuration

```text
{{config line}}
```

{{What happens when it is absent.}}

## Requirements

- {{tool, with link}}

## Repository layout

```text
.
├── {{path}}     {{comment}}
└── {{path}}     {{comment}}
```

## Contributing

{{Two or three sentences.}}

```bash
{{validate or test command}}
```

## License

[{{LICENSE}}](./LICENSE)
