#!/usr/bin/env python3
"""
CLI tool for checking template json file against potential stringified inputs.

Run like::
  ./flycheck_json_acqlabel.py \
        -t pitt-luna-habit-project-template.json \
        -r AntiSaccade,Habit \
        "13 - AntiSaccade" \
        "14 - AntiSaccade_repeat_SBRef::Functional::.json"

Yields rows of matchies.
The first column is input string, second column is BIDS file form::
  13 - AntiSaccade        sub-{session.info.BIDS.Subject}_task-AntiSaccade_bold.nii.gz
  14 - AntiSaccade_repeat_SBRef::Functional::.json        sub-{session.info.BIDS.Subject}_task-AntiSaccade_run-2_sbref.json

"""
import logging
import os

from flywheel_bids.supporting_files.bidsify_flywheel import (
    create_match_info_update,
    process_matching_templates,
)
from flywheel_bids.supporting_files.templates import load_template



#: ``Label`` and ``FileTemplate`` mock template input/output
Label = str
FileTemplate = str

def make_context(label: str, intent="Functional", ext=".nii.gz") -> dict:
    """
    Make a phony context using the label and maybe intent and/or ext
    :param label: label Flywheel would set likely from SeriesName dicom header
    :param intent: e.g. "Functional", "Structural"
    :param ext: file extension as would be parsed by flywheel.
    :return: very light mock context container
    """
    context = {
        "container_type": "file",
        # "acquisition.label" $regex in new json template
        "acquisition": {"label": label},
        # criteria from bids-client/flywheel_bids/templates/bids-v1.json:777
        "file": {"classification": {"Intent": intent}},
        "ext": ext,
    }
    return context




def simulate_output(
    json_fname: os.PathLike, labels: list[Label], rule_ids: list[str]
) -> dict[Label, FileTemplate]:
    """
    Run example labels against template for at provided rules.

    :param json_fname: input template json file to test
    :param labels: list of labels for the template to check
    :param rule_ids: list of template rules
    :return outputs:
    """

    template = load_template(
        json_fname, template_name="template_test", save_sidecar_as_metadata=True
    )

    outputs = {}
    for label in labels:
        logging.debug("trying against label %s", label)
        context = make_context(*label.split("::"))

        for rule in template.rules:
            if rule_ids and not rule.id in rule_ids:
                continue
            template_def = template.definitions.get(rule.template)
            match_info = create_match_info_update(
                rule, context, context["file"], template_def["properties"], "BIDS"
            )
            rule.initializeProperties(match_info, context)
            template.apply_custom_initialization(rule.id, match_info, context)

            logging.info("BIDS from apply custom: %s", context["file"]["info"]["BIDS"])

            # This only works when create_match_info_update has been run
            res = process_matching_templates(context, template, upload=False)  # type: ignore
            fname_template = res.get("info", {}).get("BIDS", {}).get("Filename")

            # store output
            outputs[label] = fname_template

    return outputs


def template_check():
    """
    Command line argument aware entry point for py:func:`simulate_output`.
    """

    import argparse
    loglevel = os.environ.get("LOGLEVEL", "WARN").upper()
    logging.getLogger().setLevel(loglevel)

    parser = argparse.ArgumentParser(
        description="Check labels against a flywheel template json file.",
        usage="""
   %(prog)s -t pitt-habit_reproin.json -r AntiSaccade,Habit \\
       "13 - AntiSaccade" \\
       "14 - AntiSaccade_repeat_SBRef::Functional::.json"

  export LOGLEVEL=DEBUG to increase verbosity
""",
    )
    parser.add_argument(
        "--template", "-t", required=True, help="Path to the JSON template file"
    )
    parser.add_argument(
        "--rule_id",
        "-r",
        required=False,
        default=None,
        help="Restrict checks to these rule ids. comma separate if more than one.",
    )
    parser.add_argument(
        "labels",
        nargs="+",
        type=str,
        help="One or more labels, optionally like label::intent::extension",
    )

    args = parser.parse_args()
    rule_ids = args.rule_id.split(",") if args.rule_id else []
    filenames = simulate_output(args.template, args.labels, rule_ids)

    # if verbose logging, hard to see where actual output is
    logging.info("#### MATCHES below ####")
    # tab separate
    print("\n".join([f"{k}\t{v}" for k, v in filenames.items()]))


if __name__ == "__main__":
    template_check()
