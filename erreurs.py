class ErreurMetier(Exception):
    """Erreur prévisible, dont le message peut être montré à l'utilisateur."""


class SocieteIntrouvable(ErreurMetier):
    def __init__(self, societe_id):
        super().__init__(f"Aucune société avec l'identifiant {societe_id}.")


class SymboleDejaUtilise(ErreurMetier):
    def __init__(self, symbole):
        super().__init__(f"Le symbole boursier {symbole} est déjà utilisé.")


class SocieteLiee(ErreurMetier):
    def __init__(self, societe_id):
        super().__init__(
            f"La société {societe_id} a encore des bilans ou des cours : suppression impossible."
        )