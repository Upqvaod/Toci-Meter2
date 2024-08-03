#SO con el python   
FROM python:3.12-slim 
#Crear la carpeta  
WORKDIR /app
#Crear el codigo, copiarlo
COPY . /app
#Instale las dependencias (pip install)
RUN pip install --no-cache-dir -r requirements.txt
#python app.py
EXPOSE 5000
CMD ["python", "app.py"] 

