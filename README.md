# Инструкция по запуску проекта

> ⚠️ Для работы проекта требуется Python версии **3.11.8**. Скачайте именно эту версию с официального сайта: https://www.python.org/downloads/release/python-3118/

## 1. Установка Python

1. Перейдите на официальный сайт Python: https://www.python.org/downloads/
2. Скачайте и установите версию Python 3.11.8 для вашей операционной системы (Windows, Mac, Linux).
3. При установке обязательно поставьте галочку "Add Python to PATH".

## 2. Клонирование или скачивание проекта

Скачайте этот проект на свой компьютер (например, через кнопку "Download ZIP" или с помощью git):

```
git clone https://github.com/bellinel/parsinstuments.git
cd parsinstuments
```

## 3. Создание и активация виртуального окружения

Рекомендуется использовать виртуальное окружение для изоляции библиотек:

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

## 4. Установка библиотек

После активации виртуального окружения выполните:

```
pip install -r requirements.txt
```

Если у вас несколько версий Python, используйте:
```
python -m pip install -r requirements.txt
```
или
```
python3 -m pip install -r requirements.txt
```

## 5. Запуск кода

Для запуска основного кода используйте команду:

```
python main.py
```

или, если у вас несколько версий Python:
```
python3 main.py
```

---

Если появятся вопросы или ошибки — скопируйте текст ошибки и обратитесь к автору проекта или поищите решение в интернете. 