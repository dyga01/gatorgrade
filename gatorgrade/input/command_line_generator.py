"""Generates a dictionary of shell and gator grader command options from a list of dict checks."""

import os
from typing import List
from typing import Union

from .checks import GatorGraderCheck
from .checks import ShellCheck
from .in_file_path import CheckData


# pylint: disable=too-many-nested-blocks
def generate_checks(
    check_data_list: List[CheckData],
) -> List[Union[ShellCheck, GatorGraderCheck]]:
    """Generate a list of checks based on check data from the configuration file.

    Args:
        check_data_list: A list of CheckData that each represent a check from the
            configuration file.

    Returns:
        A list of ShellChecks and GatorGraderChecks.
    """
    checks: List[Union[ShellCheck, GatorGraderCheck]] = []
    for check_data in check_data_list:
        gg_args = []
        # Add description option if in data
        description = check_data.check.get("description")
        if description is not None:
            gg_args.extend(["--description", str(description)])
        # Add name of check if it exists in data, otherwise use default_check
        check_name = check_data.check.get("check", "default_check")
        if check_name is not None:
            gg_args.append(str(check_name))
        # Add any additional options
        options = check_data.check.get("options")
        if options is not None:
            for option in options:
                # If option should be a flag (i.e. its value is the `True` boolean),
                # add only the option without a value
                option_value = options[option]
                if isinstance(option_value, bool):
                    if option_value:
                        gg_args.append(f"--{option}")
                # Otherwise, add both the option and its value
                else:
                    gg_args.extend([f"--{option}", str(option_value)])
        # Add directory and file if file context in data
        if check_data.file_context is not None:
            # Get the file and directory using os
            dirname, filename = os.path.split(check_data.file_context)
            if dirname == "":
                dirname = "."
            gg_args.extend(["--directory", dirname, "--file", filename])

        # If the check has a `command` key, then it is a shell check
        if "command" in check_data.check:
            checks.append(
                ShellCheck(
                    command=check_data.check.get("command"),
                    description=check_data.check.get("description"),
                    json_info=check_data.check,
                    gg_args=gg_args
                )
            )
        # Otherwise, it is a GatorGrader check
        else:
            checks.append(
                GatorGraderCheck(
                    gg_args=gg_args,
                    json_info=check_data.check
                )
            )

    return checks
