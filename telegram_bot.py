import os
import subprocess

# Основные директории и файлы
structure = {
    'handlers': ['__init__.py', 'start.py'],
    'models': ['__init__.py', 'model.py'],
    'keyboards': ['__init__.py', 'inline.py', 'replykey.py'],
    'forms': ['__init__.py', 'forms.py'],
    'utilities': ['__init__.py', 'utilities.py'],
    'root_files': ['.gitignore', '.env', 'main.py', 'db_conf.py', 'requirements.txt']
}

# Основные записи для .gitignore
gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
.env
"""

# Основные переменные окружения для .env
env_content = """
# Telegram bot token
BOT_TOKEN=your_token_here
"""

# Функция создания структуры проекта
def create_project_structure(project_name):
    # Создание основной директории
    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)

    # Создание виртуального окружения
    subprocess.run(['python3', '-m', 'venv', 'venv'])

    # Создание папок и файлов
    for folder, files in structure.items():
        if folder == 'root_files':
            for file in files:
                with open(file, 'w') as f:
                    if file == '.gitignore':
                        f.write(gitignore_content)
                    elif file == '.env':
                        f.write(env_content)
                    else:
                        f.write('')
        else:
            os.makedirs(folder, exist_ok=True)
            for file in files:
                open(os.path.join(folder, file), 'w').close()

# Добавление пакетов в requirements.txt
def add_requirements(packages):
    with open('requirements.txt', 'w') as f:
        for package in packages:
            f.write(f'{package}\n')

if __name__ == '__main__':
    project_name = input("Введите название проекта: ")
    create_project_structure(project_name)

    # Запросить пакеты для requirements.txt
    add_requirements = input("Хотите добавить пакеты в requirements.txt? (y/n): ")
    if add_requirements.lower() == 'y':
        packages = input("Введите названия пакетов через пробел: ").split()
        add_requirements(packages)

    print(f"Проект '{project_name}' успешно создан!")
