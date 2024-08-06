from random import choice, randint

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    
    if lowered == '':
        return 'What a silence...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return choice(['I am fine, thank you', 'I am doing well, thank you'])
    elif 'who are you' in lowered:
        return 'I am a bot who loves Formula 1!'
    elif 'f1' in lowered:
        return 'I love Formula 1!'
    elif 'what is your favorite song' in lowered:
        return 'The Dutch National Anthem never leaves my playlist!'
    else:
        return 'I am sorry, I do not understand that...'