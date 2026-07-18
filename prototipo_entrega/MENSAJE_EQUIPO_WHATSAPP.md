Hola equipo. Ya dejamos integrada en `main` una primera versión completa y reproducible del trabajo:

- notebook ejecutado de principio a fin;
- base horaria filtrada y base semanal utilizada;
- auditoría de calidad y cobertura;
- análisis exploratorio y gráficos;
- comparación de siete modelos;
- prueba final separada de la selección;
- pronóstico de ocho semanas con intervalos;
- análisis de sensibilidad;
- informe editable en Markdown.

Repositorio: <https://github.com/glopezr10/proyecto_series_tiempo>

Resultado actual: el modelo AutoReg con rezagos 1-4 y 52 obtuvo RMSE de 27,53 mg/Nm³ en las ocho semanas de prueba. Los residuos pasan Ljung-Box y el pronóstico central de las ocho semanas siguientes se mantiene aproximadamente entre 304 y 314 mg/Nm³. También verificamos los códigos operacionales con la Resolución Exenta SMA N.º 404/2017 y analizamos por separado el escenario que usa solo datos medidos durante operación en régimen (`DM+RE`).

Propongo que trabajemos así para no sobrescribirnos:

1. Antes de comenzar, actualizar `main`:
   `git switch main`
   `git pull origin main`
2. Cada persona crea o actualiza su propia rama desde `main`:
   `git switch -c Nombre`
3. Hacer cambios acotados, guardarlos con un mensaje claro y subir la rama:
   `git add .`
   `git commit -m 'Descripción breve del aporte'`
   `git push -u origin Nombre`
4. Abrir un pull request hacia `main` y avisar al grupo para revisarlo antes de fusionar.
5. Evitemos subir los CSV crudos de aproximadamente 3 GB; trabajemos con las bases reducidas que ya están versionadas.

Para la siguiente revisión necesitamos principalmente:

- confirmar que el objetivo y la interpretación ambiental nos representen a todos;
- revisar las decisiones de limpieza, agregación semanal e interpolación;
- revisar la comparación y selección de modelos;
- corregir redacción, nombres y referencias;
- cerrar el contenido y, como último paso, exportar el informe a Word y hacer su control visual;
- decidir qué partes presentará o explicará cada integrante.

La idea es que `main` sea siempre la versión estable y que cada aporte entre mediante una rama y un pull request. Así podemos comparar cambios, discutirlos y volver atrás si algo no funciona.
