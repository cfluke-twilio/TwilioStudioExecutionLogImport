from threading import Thread
from time import sleep
import json

def call_at_interval(period, callback, args):
  while True:
    sleep(period)
    callback(*args)

def setInterval(period, callback, *args):
  Thread(target=call_at_interval, args=(period, callback, args)).start()

def format_execution(execution):
  return {
    "sid": execution.sid,
    "status": execution.status,
    "steps": []
  }

def format_step(step):
  return {
    "sid": step.sid,
    "execution_sid": step.execution_sid,
    "name": step.transitioned_to,
    "type": step.name,
    "transitioned_to": step.transitioned_to,
    "transitioned_from": step.transitioned_from,
    "@timestamp": datetime.strptime(str(step.date_created), '%Y-%m-%d %H:%M:%S+00:00'),
    "variables": {},
    "searchable": ""
  }

def percent_str(num, den):
  pct = round((num/den) * 100)
  return f"{pct}%"

def format_tree_data(executions):
  # put all step transitions into multidimentional array
  arr = []
  longest = 0
  for execution in executions:
    narr = []
    for step in execution['steps']:
      if step['transitioned_from'] !='Trigger':
        narr.append(step['transitioned_from'])
    if len(narr) > longest:
      longest = len(narr)
    narr = list(dict.fromkeys(narr))
    arr.append(narr)
  # adds index to each item
  for narr in arr:
    i = 0
    for step in narr:
      narr[i] = f"{step}.{i}"
      i+=1
  # format into steps
  data = {}
  fkey = ""
  for narr in arr:
    i = 0
    for step in narr:
      if not fkey:
        fkey = step
      if not data.get(step):
        parent = narr[i-1] if i > 0 else ""
        data[step] = {
          "id": step,
          "name": step.split(".")[0].replace('_', ' '),
          "parent": parent,
          "count": 0
        }
      data[step]['count'] += 1
      i += 1
  # add %s
  for step in data:
    data[step]['display_name'] = f"{data[step]['name']} ({data[step]['count']}) ({percent_str(data[step]['count'], data[fkey]['count'])})"
  # convert data hash to list
  data = list(data.values())
  return { "data":  data }

def get_executions(flow_sid, start_date=None, end_date=None):
  if not start_date:
    start_date = datetime.now() - timedelta(days=1)
  if not end_date:
    end_date = datetime.now() + timedelta(days=1)
  arr = []
  executions = client.studio.v1.flows(flow_sid).executions.list(
                 date_created_from=start_date,
                 date_created_to=end_date,
                 limit=20
               )
  for execution in executions:
    arr.append(format_execution(execution))
  return arr

def get_execution(flow_sid, execution_sid):
  execution = client.studio.v1.flows(flow_sid).executions(execution_sid).fetch()
  return format_execution(execution)

def get_execution_steps(flow_sid, execution_sid):
  arr = []
  steps = client.studio.v1 \
    .flows(flow_sid) \
    .executions(execution_sid) \
    .steps.list()
  for step in steps:
    arr.append(format_step(step))
  arr.reverse()
  return arr

def get_execution_step_context(flow_sid, execution_sid, step_sid):
  context = client.studio.v1 \
    .flows(flow_sid) \
    .executions(execution_sid) \
    .steps(step_sid) \
    .step_context() \
    .fetch()
  return context.context['widgets']

def get_all_flow_execution_log_details(flow_sid, start_date=None, end_date=None):
  # et executions
  executions = get_executions(flow_sid, start_date, end_date)
  for execution in executions:
    # get steps for execution
    execution['steps'] = get_execution_steps(flow_sid, execution['sid'])
    # get step context if relevant.
    variables_key = "GET_REPORTING_FILTERS"
    has_variables = False
    previous_step_name = ""
    variables = {}
    for step in execution['steps']:
      if previous_step_name == variables_key:
        has_variables = True
        context = get_execution_step_context(flow_sid, execution['sid'], step['sid'])
        variables = {**variables.copy(), **json.loads(context[variables_key]['body'])}
      previous_step_name = step["name"]
    # assign variables to all the steps
    if has_variables:
      for step in execution['steps']:
        step['variables'] = variables
        step['searchable'] = str(variables)
  return executions

def format_autopilot_queries(queries):
  executions = {}
  previous_step_name = ""
  # format all executions.
  for query in queries:
    if not executions.get(query.dialogue_sid):
      executions[query.dialogue_sid] = { "steps": [] }
    if query.results.get('task'):
      executions[query.dialogue_sid]['steps'].append({
        "sid": query.sid,
        "execution_sid": query.dialogue_sid,
        "name": query.results.get('task'),
        "type": query.results.get('task'),
        "transitioned_to": previous_step_name,
        "transitioned_from": "",
        "@timestamp": datetime.strptime(str(query.date_created), '%Y-%m-%d %H:%M:%S+00:00'),
        "date_created": query.date_created.isoformat(),
        "variables": {},
        "searchable": ""
      })
      executions[query.dialogue_sid]['steps'] = sorted(executions[query.dialogue_sid]['steps'], key = lambda i: i['date_created']) 
      previous_step_name = query.results.get('task')
  return executions

def format_autopilot_executions(executions):
  # add transitioned_from
  for key in executions:
    execution = executions[key]
    previous_step_name = ""
    for step in execution["steps"]:
      step['transitioned_from'] = previous_step_name
      previous_step_name = step['name']
    execution["steps"][-1]["transitioned_to"] = "Ended"
  variables_key = "GET_REPORTING_FILTERS"
  has_variables = False
  previous_step_name = ""
  variables = {}
  for step in execution['steps']:
    if previous_step_name == variables_key:
      has_variables = True
      variables = {**variables.copy(), **json.loads(context[variables_key]['body'])}
    previous_step_name = step["name"]
  # assign variables to all the steps
  if has_variables:
    for step in execution['steps']:
      step['variables'] = variables
      step['searchable'] = str(variables)
  return list(executions.values())

