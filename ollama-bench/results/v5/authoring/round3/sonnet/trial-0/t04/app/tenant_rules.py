from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # tenant policy
    ALPHA_LOGIN = Record('alpha_login', 'alpha-login-rule', 'tenant')
    # tenant policy
    BETA_LOGIN = Record('beta_login', 'beta-login-rule', 'request')
    # tenant policy
    GAMMA_LOGIN = Record('gamma_login', 'gamma-login-rule', 'audit')
    # tenant policy
    DELTA_LOGIN = Record('delta_login', 'delta-login-rule', 'tenant')
    # tenant policy
    EPSILON_LOGIN = Record('epsilon_login', 'epsilon-login-rule', 'request')
    # tenant policy
    ZETA_LOGIN = Record('zeta_login', 'zeta-login-rule', 'audit')
    # tenant policy
    ETA_LOGIN = Record('eta_login', 'eta-login-rule', 'tenant')
    # tenant policy
    THETA_LOGIN = Record('theta_login', 'theta-login-rule', 'request')
    # tenant policy
    IOTA_LOGIN = Record('iota_login', 'iota-login-rule', 'audit')
    # tenant policy
    KAPPA_LOGIN = Record('kappa_login', 'kappa-login-rule', 'tenant')
    # tenant policy
    LAMBDA_LOGIN = Record('lambda_login', 'lambda-login-rule', 'request')
    # tenant policy
    MU_LOGIN = Record('mu_login', 'mu-login-rule', 'audit')
    # tenant policy
    NU_LOGIN = Record('nu_login', 'nu-login-rule', 'tenant')
    # tenant policy
    XI_LOGIN = Record('xi_login', 'xi-login-rule', 'request')
    # tenant policy
    OMICRON_LOGIN = Record('omicron_login', 'omicron-login-rule', 'audit')
    # tenant policy
    PI_LOGIN = Record('pi_login', 'pi-login-rule', 'tenant')
    # tenant policy
    RHO_LOGIN = Record('rho_login', 'rho-login-rule', 'request')
    # tenant policy
    SIGMA_LOGIN = Record('sigma_login', 'sigma-login-rule', 'audit')
    # tenant policy
    TAU_LOGIN = Record('tau_login', 'tau-login-rule', 'tenant')
    # tenant policy
    UPSILON_LOGIN = Record('upsilon_login', 'upsilon-login-rule', 'request')
    # tenant policy
    PHI_LOGIN = Record('phi_login', 'phi-login-rule', 'audit')
    # tenant policy
    CHI_LOGIN = Record('chi_login', 'chi-login-rule', 'tenant')
    # tenant policy
    PSI_LOGIN = Record('psi_login', 'psi-login-rule', 'request')
    # tenant policy
    OMEGA_LOGIN = Record('omega_login', 'omega-login-rule', 'audit')


def all_records():
    return (
        ALPHA_LOGIN,
        BETA_LOGIN,
        GAMMA_LOGIN,
        DELTA_LOGIN,
        EPSILON_LOGIN,
        ZETA_LOGIN,
        ETA_LOGIN,
        THETA_LOGIN,
        IOTA_LOGIN,
        KAPPA_LOGIN,
        LAMBDA_LOGIN,
        MU_LOGIN,
        NU_LOGIN,
        XI_LOGIN,
        OMICRON_LOGIN,
        PI_LOGIN,
        RHO_LOGIN,
        SIGMA_LOGIN,
        TAU_LOGIN,
        UPSILON_LOGIN,
        PHI_LOGIN,
        CHI_LOGIN,
        PSI_LOGIN,
        OMEGA_LOGIN,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def select_tenant(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((item for item in items if item.name == str(value)), None)


def allows_login(value, records=None):
    item = select_tenant(value, records)
    return item is not None and item.scope == "tenant"


def names(value, records=None):
    return tuple(item.name for item in all_records())


def as_mapping(value, records=None):
    return {item.name: item.value for item in all_records()}

