# case_ml_engineer_pleno
case técnico

## instalar python  


```bash
sudo dnf install python3.14

pip install pipx

pipx install poetry 
```

## entre em qualquer um dos ambientes virtuais dos projetos  

```bash
cd parte_1

source $(poetry env info -p)/bin/activate

poetry install 
```

## iniciar documentação 

```bash
cd ..

mkdocs serve
```


