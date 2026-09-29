"""Select original sealed start indices without changing a solver or its budget.

A process still constructs all16 identical seed4100 starts, then skips indices
assigned to another process. Selection occurs at the top of the outer loop only;
no optimizer body, initialization, bounds or report statement is transformed.
The original source and transformed-source hashes accompany every result.
"""
import ast
import hashlib
import inspect
import textwrap


def partition(function, indices):
    selected = tuple(sorted(set(indices)))
    if not selected or any(type(i) is not int or not 0 <= i < 16 for i in selected):
        raise ValueError('original start indices must be within0..15')
    source = textwrap.dedent(inspect.getsource(function))
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and ast.unparse(node.target) == '(i, start)' \
                and ast.unparse(node.iter) == 'enumerate(starts)':
            found.append(node)
    if len(found) != 1:
        raise ValueError('sealed outer start loop not uniquely identified')
    found[0].body.insert(0, ast.parse(f'if i not in {selected!r}:\n    continue').body[0])
    ast.fix_missing_locations(tree)
    transformed = ast.unparse(tree)
    # Use the SAME module namespace so the existing compact forward context
    # replaces precisely the forward function looked up by the sealed fitter.
    name = function.__name__
    original = function.__globals__[name]
    try:
        exec(compile(tree, function.__code__.co_filename, 'exec'), function.__globals__)
        result = function.__globals__[name]
    finally:
        function.__globals__[name] = original
    provenance = dict(originalStartIndices=list(selected), originalSeed=4100,
        originalSourceSha256=hashlib.sha256(source.encode()).hexdigest(),
        transformedSourceSha256=hashlib.sha256(transformed.encode()).hexdigest(),
        transform='skip unassigned original indices at outer-loop entry only',
        budgetsChanged=False, parameterizationChanged=False)
    return result, provenance
