from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool

engine = None


def init(file=":memory:"):
    connect_args = {"check_same_thread": False}
    global engine
    if file == ":memory:":
        engine = create_engine(
            "sqlite:///:memory:",
            echo=True,
            connect_args=connect_args,
            poolclass=StaticPool,
        )
    else:
        engine = create_engine("sqlite:///{file}", echo=True, connect_args=connect_args)

    SQLModel.metadata.create_all(engine)


def open():
    if engine is None:
        raise Exception("attempted to get database before calling init")

    with Session(engine) as session:
        yield session
