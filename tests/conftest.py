"""Fixtures partagées pour les tests."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base


@pytest.fixture
def engine():
    """Crée un engine SQLite en mémoire."""
    eng = create_engine("sqlite:///:memory:", echo=False)
    # Import tous les modèles pour créer les tables
    import app.models.adjustments  # noqa: F401
    import app.models.assumptions  # noqa: F401
    import app.models.fec_entry  # noqa: F401
    import app.models.cash  # noqa: F401
    import app.models.fixed_charges  # noqa: F401
    import app.models.history  # noqa: F401
    import app.models.imports_log  # noqa: F401
    import app.models.invoices  # noqa: F401
    import app.models.orders  # noqa: F401
    import app.models.reference  # noqa: F401
    import app.models.versions  # noqa: F401

    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session(engine):
    """Crée une session de test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_condition_30fm(session):
    """Condition de règlement : 30 jours fin de mois."""
    from app.models.reference import ConditionReglement
    cr = ConditionReglement(
        code="30FM", libelle="30 jours fin de mois",
        base_jours=30, fin_de_mois=True,
    )
    session.add(cr)
    session.flush()
    return cr


@pytest.fixture
def sample_condition_60net(session):
    """Condition de règlement : 60 jours net."""
    from app.models.reference import ConditionReglement
    cr = ConditionReglement(
        code="60NET", libelle="60 jours net",
        base_jours=60, fin_de_mois=False,
    )
    session.add(cr)
    session.flush()
    return cr


@pytest.fixture
def sample_condition_45fm10(session):
    """Condition de règlement : 45 jours fin de mois le 10."""
    from app.models.reference import ConditionReglement
    cr = ConditionReglement(
        code="45FM10", libelle="45 jours fin de mois le 10",
        base_jours=45, fin_de_mois=True, jour_du_mois=10,
    )
    session.add(cr)
    session.flush()
    return cr


@pytest.fixture
def sample_client(session, sample_condition_30fm):
    """Client de test."""
    from app.models.reference import Client
    client = Client(
        sage_code="CLI001", name="Client Test SARL",
        condition_reglement_id=sample_condition_30fm.id,
        code_activite="BTP",
    )
    session.add(client)
    session.flush()
    return client


@pytest.fixture
def sample_fournisseur(session, sample_condition_60net):
    """Fournisseur de test."""
    from app.models.reference import Fournisseur
    fournisseur = Fournisseur(
        sage_code="FRN001", name="Fournisseur Test SA",
        condition_reglement_id=sample_condition_60net.id,
    )
    session.add(fournisseur)
    session.flush()
    return fournisseur
