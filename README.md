# siibra-schema

`siibra-schema` is a helper repository to [siibra-python](https://github.com/fzj-inm1-bda/siibra-python/) and [siibra-configuration](https://github.com/FZJ-INM1-BDA/siibra-configurations/). It contains a collection of JSON schema files, which can validate new and/or custom JSON files. The validated JSON files are expected to be directly usable by `siibra-python`.

Whilst `siibra-schema` originated from, and was co-designed with `siibra-python` >= v2.0, it serves as the source of truth when/if new schemas are to be added to siibra-toolsuites.

## Installation

At the moment, you can install this repository from source via:

```sh
$ git clone https://github.com/FZJ-INM1-BDA/siibra-schema.git
$ cd siibra-schema
$ pip install -r requirements.txt
```

## Usage

The following code would recursively walk `/path/to/my/configuration`, find all JSON files, and attempt to validate them with the JSON schema defined in this repository.

```sh
$ python code/validate.py /path/to/my/configuration
```

## FAQ

### What's the deal with `urn:siibra-local:`

In order to reference relative schemas, `siibra-schema` uses this prefix internally to crawl this repository. Effectively, `urn:siibra-local:siibra/attr/v0.1.json` would point to <siibra/attr/v0.1.json>.

### Whom is this repository for

Users who would like to use custom configurations with siibra-python can use this repository to validate their custom JSON files. 

Users who would like to propose additional functionalities (e.g. additional supported data types, additional supported meta-data fields) can raise issues or PR in this repository.

## License

Apache 2.0
