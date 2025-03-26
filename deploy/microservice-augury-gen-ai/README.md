# helm: microservice-genai-template

This chart installs [microservice-genai-template](https://github.com/augurysys/microservice-genai-template), according to the following
pattern:

The [values.yaml](values.yaml) exposes a few of the configuration options in the
chart.

The values.ENV.yaml sets the values for specific environment.
The secrets.ENV.yaml sets the secrets for specific environment.


## Configuration

### Environment Variables

The microservice-genai-template pods have the following environment variables:

  - SENTRY_DSN
  - AUGURY_OAUTH2_INTERNAL_URL
  - AUGURY_OAUTH2_URL
  - MONGODB_DB
  - MONGODB_URL

## Installation

```console
helm secrets update -i -f values.yaml -f values.staging.yaml -f secrets.staging.yaml .
```

## Updating encrypted secrets

helm-secrets used for secrets encryption, please read the [README](https://github.com/futuresimple/helm-secrets#usage-and-examples)

KMS key ring: `helm`
KMS key: `secrets`

### Example of updating staging microservice-genai-template secrets:
```console
helm secrets edit chart/secrets.staging.yaml
```
