import sys
import os
from pathlib import Path
from logging import getLogger, DEBUG, INFO, StreamHandler
from jsonschema import ValidationError, Draft202012Validator
import referencing
import json
from enum import Enum


class ValidationResult(Enum):
    SKIPPED = "SKIPPED"
    PASSED = "PASSED"
    FAILED = "FAILED"


logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())

ROOT_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/..")

skip_path = ("venv", "siibra-configurations/maps")

skip_types = (
    "siibra/feature/timeseries/activity/v0.1",
    # "siibra/feature/connectivitymatrix/v0.3",
)


def populate_jsonschema_reg():
    registry = referencing.Registry()
    walk_path = Path(ROOT_DIR) / "siibra"
    for dirpath, dirnames, filenames in os.walk(walk_path):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue

            filepath = Path(dirpath) / filename
            with open(filepath, "r") as fp:
                uri = f"urn:siibra-local:{str(filepath.relative_to(ROOT_DIR))}"
                resource = referencing.Resource.from_contents(json.load(fp=fp))
                registry = registry.with_resource(uri=uri, resource=resource)

    return registry


def validate_json(path_to_json, registry, fail_fast=False):
    if any([path_fragment in path_to_json for path_fragment in skip_path]):
        return (
            path_to_json,
            ValidationResult.SKIPPED,
            None,
        )
    with open(path_to_json, "r") as fp:
        json_obj = json.load(fp)

    # skip list
    if isinstance(json_obj, list):
        return (path_to_json, ValidationResult.SKIPPED, None)
    _type = json_obj.get("@type", None)
    if not _type:
        # TODO consolidate how error are raied
        if fail_fast:
            raise ValidationError(f"type does not exist: {path_to_json}")
        return (path_to_json, ValidationResult.FAILED, None)

    # assert _schema is None
    if not _type or not _type.startswith("siibra"):
        return (path_to_json, ValidationResult.SKIPPED, None)
    if _type in skip_types:
        return (path_to_json, ValidationResult.SKIPPED, None)
    abspath = os.path.join(ROOT_DIR, (_type + ".json"))
    path_to_schema = os.path.abspath(abspath)
    with open(path_to_schema, "r") as fp:
        schema = json.load(fp)
    try:
        validator = Draft202012Validator(schema, registry=registry)
        validator.validate(json_obj)
    except ValidationError as e:
        if fail_fast:
            # TODO consolidate how error are raied
            raise e from e
        return (path_to_json, ValidationResult.FAILED, e)
    return (path_to_json, ValidationResult.PASSED, None)


def main(dir_to_validate: str = None, *args, debug=False):

    if debug:
        logger.setLevel(DEBUG)

    jsonschema_reg = populate_jsonschema_reg()
    # resolver = jsonschema_reg.resolver()

    if dir_to_validate is None:
        raise RuntimeError("pass the directory that needs to validated")

    result = []
    for dirpath, dirnames, filenames in os.walk(dir_to_validate):
        for filename in filenames:
            path_to_file = Path(dirpath) / filename
            if not filename.endswith(".json"):
                logger.debug(
                    f"Skipping {path_to_file} because it does not end in .json"
                )
                continue
            logger.debug(f"Processing {path_to_file}")
            result.append(
                validate_json(str(path_to_file),
                              jsonschema_reg,
                              fail_fast=False)
            )

    passed = [r for r in result if r[1] == ValidationResult.PASSED]
    failed = [r for r in result if r[1] == ValidationResult.FAILED]
    skipped = [r for r in result if r[1] == ValidationResult.SKIPPED]
    print(
        f"Validation results: PASSED: {len(passed)} SKIPPED:"
        f"{len(skipped)} FAILED: {len(failed)}"
    )

    if len(failed) > 0:
        print(failed)
        # TODO consolidate how error are raied
        raise ValidationError(
            message="\n-----\n".join([f"{f[0]}: {str(f[2])}" for f in failed])
        )


if __name__ == "__main__":
    main(*sys.argv[1:])
