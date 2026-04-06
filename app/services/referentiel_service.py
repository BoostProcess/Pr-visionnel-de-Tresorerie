"""Service CRUD pour les référentiels."""

from datetime import date

from sqlalchemy.orm import Session

from app.models.adjustments import AjustementManuel
from app.models.cash import PositionTresorerie
from app.models.fixed_charges import ChargeFiscale, ChargeFix, Emprunt
from app.models.reference import Client, ConditionReglement, Fournisseur


class ReferentielService:
    """Opérations CRUD sur les référentiels."""

    def __init__(self, session: Session):
        self.session = session

    # --- Conditions de règlement ---

    def list_conditions(self) -> list[ConditionReglement]:
        return self.session.query(ConditionReglement).order_by(ConditionReglement.code).all()

    def create_condition(self, **kwargs) -> ConditionReglement:
        cr = ConditionReglement(**kwargs)
        self.session.add(cr)
        self.session.flush()
        return cr

    def delete_condition(self, condition_id: int):
        cr = self.session.get(ConditionReglement, condition_id)
        if cr:
            self.session.delete(cr)

    # --- Clients ---

    def list_clients(self) -> list[Client]:
        return self.session.query(Client).order_by(Client.name).all()

    # --- Fournisseurs ---

    def list_fournisseurs(self) -> list[Fournisseur]:
        return self.session.query(Fournisseur).order_by(Fournisseur.name).all()

    # --- Charges fixes ---

    def list_charges_fixes(self) -> list[ChargeFix]:
        return self.session.query(ChargeFix).order_by(ChargeFix.libelle).all()

    def create_charge_fixe(self, **kwargs) -> ChargeFix:
        charge = ChargeFix(**kwargs)
        self.session.add(charge)
        self.session.flush()
        return charge

    def delete_charge_fixe(self, charge_id: int):
        charge = self.session.get(ChargeFix, charge_id)
        if charge:
            self.session.delete(charge)

    # --- Emprunts ---

    def list_emprunts(self) -> list[Emprunt]:
        return self.session.query(Emprunt).order_by(Emprunt.libelle).all()

    def create_emprunt(self, **kwargs) -> Emprunt:
        emprunt = Emprunt(**kwargs)
        self.session.add(emprunt)
        self.session.flush()
        return emprunt

    def delete_emprunt(self, emprunt_id: int):
        emprunt = self.session.get(Emprunt, emprunt_id)
        if emprunt:
            self.session.delete(emprunt)

    # --- Charges fiscales ---

    def list_charges_fiscales(self) -> list[ChargeFiscale]:
        return self.session.query(ChargeFiscale).order_by(ChargeFiscale.libelle).all()

    def create_charge_fiscale(self, **kwargs) -> ChargeFiscale:
        charge = ChargeFiscale(**kwargs)
        self.session.add(charge)
        self.session.flush()
        return charge

    # --- Trésorerie initiale ---

    def get_initial_cash(self) -> PositionTresorerie | None:
        return (
            self.session.query(PositionTresorerie)
            .filter(PositionTresorerie.est_initial == True)
            .order_by(PositionTresorerie.date.desc())
            .first()
        )

    def set_initial_cash(self, solde: int, dt: date | None = None) -> PositionTresorerie:
        if dt is None:
            dt = date.today()
        pos = self.get_initial_cash()
        if pos:
            pos.solde_banque = solde
            pos.date = dt
        else:
            pos = PositionTresorerie(date=dt, solde_banque=solde, est_initial=True)
            self.session.add(pos)
        self.session.flush()
        return pos

    # --- Ajustements manuels ---

    def list_ajustements(self) -> list[AjustementManuel]:
        return (
            self.session.query(AjustementManuel)
            .order_by(AjustementManuel.mois, AjustementManuel.cree_le)
            .all()
        )

    def create_ajustement(self, **kwargs) -> AjustementManuel:
        adj = AjustementManuel(**kwargs)
        self.session.add(adj)
        self.session.flush()
        return adj

    def delete_ajustement(self, ajustement_id: int):
        adj = self.session.get(AjustementManuel, ajustement_id)
        if adj:
            self.session.delete(adj)
