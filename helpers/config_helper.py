import configparser


def read_config() -> dict:
    config: configparser.ConfigParser = configparser.ConfigParser()

    config.read('config.ini')

    log_level: str = config.get('General', 'log_level')
    command_prefix: str = config.get('Bot', 'command_prefix')

    config_values = {
        'log_level': log_level,
        'command_prefix': command_prefix,
    }

    return config_values


def read_info() -> dict:
    config: configparser.ConfigParser = configparser.ConfigParser()

    config.read('config.ini')

    about: str = config.get('Info', 'about')
    about2: str = config.get('Info', 'about2')
    ver: str = config.get('Info', 'version')

    config_values = {
        'about': about,
        'about2': about2,
        'ver': ver,
    }

    return config_values
