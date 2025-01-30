from io import UnsupportedOperation

import sqlalchemy as sqla
import sqlalchemy.orm as orm
from sqlalchemy.orm import DeclarativeBase, Mapped
from arbfls.config import table_name, config_dict
import enum
from sqlalchemy import types

engine = sqla.create_engine("postgresql://postgres:admin@localhost:5432/arbfls", echo=False)

class Base(DeclarativeBase):
    pass


class Edge_Algos(enum.Enum):
    LoG = "laplacian"
    Canny = "canny"

class Heuristics(enum.Enum):
    none = "none"
    flat = "flat"
    discrete_points = "discrete_points"


class Run(Base):
    __tablename__ = table_name
    # Informacoes base
    run_id : Mapped[int] = orm.mapped_column(primary_key=True)
    test_name : Mapped[str] = orm.mapped_column(nullable=False)
    # Nome da imagem
    image: Mapped[str] = orm.mapped_column(sqla.String(255))
    # Numeros das imagens
    im_num_1: Mapped[int] = orm.mapped_column(sqla.Integer)
    im_num_2: Mapped[int] = orm.mapped_column(sqla.Integer)
    # Resultados
    psnr_left: Mapped[float] = orm.mapped_column(sqla.Float)
    psnr_right: Mapped[float] = orm.mapped_column(sqla.Float)
    # Configuracoes
    edge_algo : Mapped[Edge_Algos] =  orm.mapped_column(types.Enum(Edge_Algos))
    heuristic : Mapped[Heuristics] = orm.mapped_column(types.Enum(Heuristics))
    dinamic_window : Mapped[bool] = orm.mapped_column(sqla.Boolean)
    horizontal_window : Mapped[int] = orm.mapped_column(sqla.Integer, nullable=True)
    vertical_window : Mapped[int] = orm.mapped_column(sqla.Integer, nullable=True)
    block_size : Mapped[int] = orm.mapped_column(sqla.Integer)
    # Parametros de heuristica
    heuristic_alpha : Mapped[int] = orm.mapped_column(sqla.Integer, nullable=True)
    heuristic_beta : Mapped[int] = orm.mapped_column(sqla.Integer, nullable=True)
    heuristic_npeaks : Mapped[int] = orm.mapped_column(sqla.Integer, nullable=True)
    # Parametros da janela dinamica
    dw_threshold : Mapped[float] = orm.mapped_column(sqla.Float, nullable=True)
    dw_extension : Mapped[float] = orm.mapped_column(sqla.Float, nullable=True)




Base.metadata.create_all(engine)


def save_run(image, im_nums, psnrs, test_name, config = config_dict):
    run = Run(
        image = image,
        test_name=test_name,
        im_num_1= im_nums[0],
        im_num_2= im_nums[1],
        psnr_left = psnrs[0],
        psnr_right = psnrs[1],
        edge_algo = Edge_Algos(config["pre_processing"]),
        heuristic = Heuristics(config["heuristic"]),
        dinamic_window = config["dinamic_window"],
        block_size = config["block_size"],
    )
    if run.dinamic_window:
        run.dw_threshold = config["dw_config"]["threshold"]
        run.dw_extension = config["dw_config"]["extension"]
    else:
        run.horizontal_window = config["horizontal_window"],
        run.vertical_window = config["vertical_window"],

    match run.heuristic:
        case Heuristics.none:
            pass
        case Heuristics.flat:
            run.heuristic_alpha = config["heuristic_params"]["alpha"]
        case Heuristics.discrete_points:
            run.heuristic_alpha = config["heuristic_params"]["alpha"]
            run.heuristic_beta = config["heuristic_params"]["beta"]
            run.heuristic_npeaks = config["heuristic_params"]["npeaks"]
    with orm.Session(engine) as session:
        session.add(run)
        session.commit()

