from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, HTTPException, status

#Models
# Crear un modelo Estudiante utilizando SQLModel con los siguientes atributos:
# id: identificador autogenerado.
# nombre: nombre del estudiante.
# apellido: apellido del estudiante.
# correo: correo electrónico.
# edad: edad del estudiante.

class Estudiante(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    correo: str | None = None
    edad: int
    
class EstudianteCreate(SQLModel):
    nombre: str
    apellido: str
    correo: str | None = None
    edad: int
    
class EstudianteRead(SQLModel):
    id: int
    nombreCompleto: str
     
sqlite_url = "sqlite:///estudiantes.db" # String de conexion para su base de datos real 

engine = create_engine(
    sqlite_url,
    echo=True,
)

def create_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(lifespan=create_tables())

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Endpoints
@app.post("/estudiantes/", status_code=status.HTTP_201_CREATED, response_model=EstudianteRead)
def create_estudiante(datosEstudiante: EstudianteCreate):
    estudiante = Estudiante(**datosEstudiante.model_dump())
    with Session(engine) as session:
        session.add(estudiante)
        session.commit()
        session.refresh(estudiante)
        return EstudianteRead(id=estudiante.id, nombreCompleto=f"{estudiante.nombre} {estudiante.apellido}")
    
@app.get("/estudiantes/")
def read_estudiantes():
    with Session(engine) as session:
        return session.exec(select(Estudiante)).all()

@app.get("/estudiantes/{estudiante_id}")
def read_estudiante(estudiante_id: int):
    with Session(engine) as session:
        estudiante = session.get(Estudiante, estudiante_id)
        if estudiante is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
        return estudiante
        
@app.delete("/estudiantes/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estudiante(estudiante_id: int):
    with Session(engine) as session:
        estudiante = session.get(Estudiante, estudiante_id)
        if estudiante is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
        session.delete(estudiante)
        session.commit()