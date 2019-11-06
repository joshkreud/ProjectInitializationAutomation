from PyInquirer import prompt

def query_yes_no(question:str,default:bool=False)->bool:
    """Simple yex/no query

    Arguments:
        question {[str]} -- [the question to prompt]

    Keyword Arguments:
        default {bool} -- [the default answer when pressing enter] (default: {False})

    Returns:
        [bool]
    """
    q = [
        {
        'type': 'confirm',
        'message': question,
        'name': 'quest',
        'default': default,
        }
    ]
    return prompt(q)['quest']
def query_text(question:str,default:str='')->str:
    """Simple text input query

    Arguments:
        question {[str]} -- [the question to prompt]

    Keyword Arguments:
        default {bool} -- [the default answer when pressing enter]

    Returns:
        [bool]
    """
    q = [
        {
        'type': 'input',
        'message': question,
        'name': 'quest',
        'default': default,
        }
    ]
    return prompt(q)['quest']