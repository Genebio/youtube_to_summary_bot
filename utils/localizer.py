from config.locales import locales

def get_localized_message(language_code: str, var_name: str) -> str:
    """
    Retrieve the localized message for a given variable name and language code.

    :param language_code: The user's language code (e.g., 'en', 'fr').
    :param var_name: The variable name for the message (e.g., 'help_msg').
    :return: Localized message as a string.
    """
    # Fallback to 'en' if the language is not supported
    language_data = locales.get(language_code, locales['en'])
    
    # Fallback to 'en' if the variable is not found in the specified language
    return language_data.get(var_name, locales['en'][var_name])