"""
 REPL session documentation.
 also see 01-issue_bidsify-duplicated.org

read in json bids file and pass through
  bidsify_flywheel.rule_matches -- check regex matching acquisition
  templates.apply_custom_initialization -- check rules

20241010WF - init
"""
import flywheel
import re
from flywheel_bids.curate_bids import curate_bids, curate_bids_tree, Count
from flywheel_bids.supporting_files.project_tree import get_project_node, set_tree
from flywheel_bids.supporting_files.templates import load_template

# editing debug info
import flywheel_bids.supporting_files.bidsify_flywheel
import importlib
importlib.reload(flywheel_bids.supporting_files.bidsify_flywheel)
from flywheel_bids.supporting_files.bidsify_flywheel import process_matching_templates, rule_matches, create_match_info_update
from typing import List, Dict
#from ipdb import set_trace


fw = flywheel.Client()
# used inside function. but made global for easy debugging
project_node = None
session = None

type Context = Dict
type Contexts = List[Context]
def get_contexts(session_id="65fa03345d3f3dbce8339c64",
                 file_regexp=r"Habit|T1|Rest|Anti") -> Contexts:
    """
    get example contexts to test against
    @param session_id
    @param file_regexp
    @return contexts
    """
    global fw, project_node, session  # 🤮 -- lazy, might want later
    session = fw.get(session_id)
    project_node = get_project_node(fw, session.parents.project)
    # subset to session for easier debugging
    set_tree(fw,project_node,fw.get(session.parents.subject))

    contexts = [x
                for x in project_node.context_iter()
                if x.get('ext')=='.nii.gz' and
                re.search(file_regexp, x['file']['name'])]

    return contexts

def context_empty_bids(contexts: Contexts) -> None:
    """
    empty dict for info.BIDS
    if missing, process_matching_templates will skip
    set to NA after matches?
    """
    for c in contexts:
        info = c.get('info',{})
        info['BIDS'] = info.get("BIDS", {})
        c['info'] = info

type RuleId = str
type AcqLabel = str
type RuleMatch = List[(int, RuleId, AcqLabel)]
def find_matches(contexts: Contexts) -> RuleMatch:
    """
    exercise rule_matches
    @return list of context index, rule id name, acq label
    """
    matches = []
    for  i, context in enumerate(contexts):
        for rule in template.rules:
            label = context['file']['name']
            if rule_matches(rule, context, label):
                matches.append((i, rule.id, label))
    return matches

contexts = get_contexts()
#print([x['file']['name'] for x in contexts])


template_path="./pitt-luna-habit-project-template.json"
template = load_template(template_path, template_name="mytemplate", save_sidecar_as_metadata=True)
print(template.initializer_map['bids_func_file'][0]['initialize']["Task"])
print(template.initializer_map['bids_func_file_anti'])

#{x.id: x.initialize.get("Task") for x in template.rules if re.search("func",x.id)}
#{'bids_func_file': {'acquisition.label': {'$regex': '(^|_)task-(?P<value>[^-_]+)'}}}


rules_dict = {rule.id: rule for rule in template.rules}
print([x.id for x in template.rules if re.search('func',x.id)])
# ['bids_func_file'] -- missing anti?!

#### what matches?
matches = find_matches(contexts)
print("\n".join(["\t".join([f'{xx}' for xx in x]) for x in matches]))


def check_match(context_idx, rule_id, file_label):
    print(f"# RUNNING {rule_id} for {file_label}")
    rule = rules_dict[rule_id]
    context = contexts[context_idx]
    container = context['file']
    #container['info']['BIDS'] == 'NA' will cause problems
    # see context_empty_bids above
    template_def = template.definitions.get(rule.template)
    match_info = create_match_info_update(rule, context, container, template_def["properties"], "BIDS")
    rule.initializeProperties(match_info, context)
    template.apply_custom_initialization(rule.id, match_info, context)
    print(context['file']['info']['BIDS'])

### how are rules applied?
context_empty_bids(contexts)
check_match(*matches[0])

# {x.id: x.initialize for x in template.rules if re.search("func",x.id)}
# {'bids_func_file': {'Task': {'acquisition.label': {'$regex': '(^|_)task-(?P<value>[^-_]+)'}}, 'Run': {'acquisition.label': {'$regex': ['(^|_)run-(?P<value>\\d+)', '(^|_)run(?P<value>[=+])']}, '$run_counter': {'key': 'functional.{file.info.BIDS.Task}'}}, 'Modality': {'$switch': {'$on': 'acquisition.label', '$cases': [{'$regex': '.*_SBRef$|.*_sbref$', '$value': 'sbref'}]}}}}



for (context_idx, rule_id, file_label) in matches:
    check_match(context_idx, rule_id, file_label)


# ----
# x = curate_bids_tree(fw, template, project_node, count=Count())
curate_bids(fw, project_node['id'], session_id=session_id, template_path=template_path)
contexts_bids = [x
            for x in project_node.context_iter()
            if x.get('ext')=='.nii.gz' and
               re.search(file_regexp, x['file']['name'])]


# context_empty_bids(contexts)
BIDS = [ process_matching_templates(context=c, template=template, upload=False) for c in contexts_bids]

print([(x['file']['name'], y['info']['BIDS']) for x,y in zip(contexts_bids,BIDS)])
