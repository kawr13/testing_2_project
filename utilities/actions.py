import importlib


def get_function(module_name, function_name):
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def get_class(module_name, class_name):
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class CallbackHandler:
    def __init__(self):
        self.handlers = {
            'add_user+': self.handle_target_id,
            'is_block+': self.handle_target_id,
        }

    def handle_target_id(self, data):
        return data.split('+')[0]

    def handle(self, data):
        for prefix, handler in self.handlers.items():
            if data.startswith(prefix):
                return handler(data)
        return data


class LazyLoader:
    def __init__(self, module, func):
        self.module = module
        self.func = func
        self._function = None

    def __call__(self, *args, **kwargs):
        if self._function is None:
            self._function = get_function(self.module, self.func)
        return self._function(*args, **kwargs)


def load_actions(mapping):
    actions = {}
    for key, (module, func) in mapping.items():
        actions[key] = LazyLoader(module, func)
    return actions


action_mapping = {
    'admin_panel': ('', ''),
    'check_imei': ('handlers.start', 'check_imei_handler'),
    'is_menu': ('handlers.start', 'start_handler'),
    'checking': ('handlers.start', 'checking_handler'),
    'add_token': ('handlers.as_token', 'add_token_handler'),
    'add_user': ('handlers.user_list', 'add_user_handler'),
    'add_user': ('handlers.user_list', 'add_user_handler'),
    'is_block': ('handlers.user_list', 'block_handler'),
}

img_dict = {
    'imei': 'https://i.pinimg.com/736x/5f/ff/30/5fff30a0c9889fe3c7651543986d8921.jpg',
    'no_auth': 'https://i.pinimg.com/736x/9a/fc/7a/9afc7a25b88f93f1f95e67186d979090.jpg',
    'token': 'https://i.pinimg.com/736x/57/cf/26/57cf26529029ab44309d7b52c2173713.jpg',
    'user': 'https://i.pinimg.com/736x/c8/1f/27/c81f27d71450b58942f9b632c6d18be7.jpg',
}

actions = load_actions(action_mapping)
callback_handler = CallbackHandler()