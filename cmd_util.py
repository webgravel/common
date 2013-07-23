import sys

def main_multiple_action(globals):
    actions = [ k[len('action_'):] for k in globals.keys() if k.startswith('action_') ]
    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        sys.exit('Usage: {} {} ...'.format(sys.argv[0], '|'.join(actions)))
    action = sys.argv[1]
    del sys.argv[1:2]
    sys.argv[0] += ' ' + action
    globals['action_' + action]()
