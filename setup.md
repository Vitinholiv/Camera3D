Dentro da **pasta vazia** que você quer que o projeto seja instalado, digite no terminal uma linha por vez.

**Windows**

```
git clone https://github.com/Vitinholiv/Camera3D.git .
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Linux/MacOS**

```
git clone https://github.com/Vitinholiv/Camera3D.git .
python3 -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
python3 main.py
```
