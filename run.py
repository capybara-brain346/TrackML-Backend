from backend import create_app
from backend.models.models import Base, engine

app = create_app()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(debug=True)
