DEFAULT_PRESENTATION = """
<h1>${challenge_title}</h1>

<h3>Brought to you by ${challenge_organization_name}</h3>

<p>${challenge_description}</p>


This challenge was generated using chalab.
"""

DEFAULT_EVALUATION = """
<h1>${challenge_title}: Evaluation</h1>

<p>
The submission will be evaluated using the <code>${metric_name}</code>.
</p>

"""

DEFAULT_DATA = """
<h1>${challenge_title}: Data</h1>

<p>
This challenge relies on the ${dataset_name} dataset.
</p>
"""

DEFAULT_RULES = """
<h1>${challenge_title}: Rules</h1>

<p>
Submissions must be submitted before the ${end_data}.
You may submit ${protocol_max_submissions_per_day} submissions every day and
${protocol_max_submissions} in total.
</p>

<ul>
<li>You implicitly allow reuse of your submissions: ${protocol_allow_reuse}</li>
<li>This challenge is publicly available: ${protocol_publicly_available}</li>
</ul>

"""

DEFAULT_PAGES = [
    {'title': 'presentation', 'content': DEFAULT_PRESENTATION},
    {'title': 'evaluation', 'content': DEFAULT_EVALUATION},
    {'title': 'data', 'content': DEFAULT_DATA},
    {'title': 'rules', 'content': DEFAULT_RULES}
]
