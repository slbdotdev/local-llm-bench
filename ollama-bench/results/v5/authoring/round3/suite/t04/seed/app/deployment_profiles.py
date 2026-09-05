from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # deployment profiles
    PROFILE_LOCAL_01 = Record('profile_local_01', 'profile-local-01-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_01 = Record('profile_test_01', 'profile-test-01-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_01 = Record('profile_staging_01', 'profile-staging-01-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_01 = Record('profile_canary_01', 'profile-canary-01-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_01 = Record('profile_production_01', 'profile-production-01-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_01 = Record('profile_recovery_01', 'profile-recovery-01-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_02 = Record('profile_local_02', 'profile-local-02-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_02 = Record('profile_test_02', 'profile-test-02-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_02 = Record('profile_staging_02', 'profile-staging-02-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_02 = Record('profile_canary_02', 'profile-canary-02-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_02 = Record('profile_production_02', 'profile-production-02-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_02 = Record('profile_recovery_02', 'profile-recovery-02-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_03 = Record('profile_local_03', 'profile-local-03-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_03 = Record('profile_test_03', 'profile-test-03-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_03 = Record('profile_staging_03', 'profile-staging-03-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_03 = Record('profile_canary_03', 'profile-canary-03-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_03 = Record('profile_production_03', 'profile-production-03-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_03 = Record('profile_recovery_03', 'profile-recovery-03-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_04 = Record('profile_local_04', 'profile-local-04-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_04 = Record('profile_test_04', 'profile-test-04-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_04 = Record('profile_staging_04', 'profile-staging-04-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_04 = Record('profile_canary_04', 'profile-canary-04-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_04 = Record('profile_production_04', 'profile-production-04-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_04 = Record('profile_recovery_04', 'profile-recovery-04-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_05 = Record('profile_local_05', 'profile-local-05-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_05 = Record('profile_test_05', 'profile-test-05-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_05 = Record('profile_staging_05', 'profile-staging-05-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_05 = Record('profile_canary_05', 'profile-canary-05-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_05 = Record('profile_production_05', 'profile-production-05-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_05 = Record('profile_recovery_05', 'profile-recovery-05-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_06 = Record('profile_local_06', 'profile-local-06-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_06 = Record('profile_test_06', 'profile-test-06-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_06 = Record('profile_staging_06', 'profile-staging-06-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_06 = Record('profile_canary_06', 'profile-canary-06-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_06 = Record('profile_production_06', 'profile-production-06-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_06 = Record('profile_recovery_06', 'profile-recovery-06-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_07 = Record('profile_local_07', 'profile-local-07-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_07 = Record('profile_test_07', 'profile-test-07-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_07 = Record('profile_staging_07', 'profile-staging-07-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_07 = Record('profile_canary_07', 'profile-canary-07-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_07 = Record('profile_production_07', 'profile-production-07-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_07 = Record('profile_recovery_07', 'profile-recovery-07-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_08 = Record('profile_local_08', 'profile-local-08-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_08 = Record('profile_test_08', 'profile-test-08-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_08 = Record('profile_staging_08', 'profile-staging-08-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_08 = Record('profile_canary_08', 'profile-canary-08-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_08 = Record('profile_production_08', 'profile-production-08-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_08 = Record('profile_recovery_08', 'profile-recovery-08-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_09 = Record('profile_local_09', 'profile-local-09-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_09 = Record('profile_test_09', 'profile-test-09-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_09 = Record('profile_staging_09', 'profile-staging-09-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_09 = Record('profile_canary_09', 'profile-canary-09-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_09 = Record('profile_production_09', 'profile-production-09-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_09 = Record('profile_recovery_09', 'profile-recovery-09-rule', 'audit')
    # deployment profiles
    PROFILE_LOCAL_10 = Record('profile_local_10', 'profile-local-10-rule', 'tenant')
    # deployment profiles
    PROFILE_TEST_10 = Record('profile_test_10', 'profile-test-10-rule', 'request')
    # deployment profiles
    PROFILE_STAGING_10 = Record('profile_staging_10', 'profile-staging-10-rule', 'audit')
    # deployment profiles
    PROFILE_CANARY_10 = Record('profile_canary_10', 'profile-canary-10-rule', 'tenant')
    # deployment profiles
    PROFILE_PRODUCTION_10 = Record('profile_production_10', 'profile-production-10-rule', 'request')
    # deployment profiles
    PROFILE_RECOVERY_10 = Record('profile_recovery_10', 'profile-recovery-10-rule', 'audit')


def all_records():
    return (
        PROFILE_LOCAL_01,
        PROFILE_TEST_01,
        PROFILE_STAGING_01,
        PROFILE_CANARY_01,
        PROFILE_PRODUCTION_01,
        PROFILE_RECOVERY_01,
        PROFILE_LOCAL_02,
        PROFILE_TEST_02,
        PROFILE_STAGING_02,
        PROFILE_CANARY_02,
        PROFILE_PRODUCTION_02,
        PROFILE_RECOVERY_02,
        PROFILE_LOCAL_03,
        PROFILE_TEST_03,
        PROFILE_STAGING_03,
        PROFILE_CANARY_03,
        PROFILE_PRODUCTION_03,
        PROFILE_RECOVERY_03,
        PROFILE_LOCAL_04,
        PROFILE_TEST_04,
        PROFILE_STAGING_04,
        PROFILE_CANARY_04,
        PROFILE_PRODUCTION_04,
        PROFILE_RECOVERY_04,
        PROFILE_LOCAL_05,
        PROFILE_TEST_05,
        PROFILE_STAGING_05,
        PROFILE_CANARY_05,
        PROFILE_PRODUCTION_05,
        PROFILE_RECOVERY_05,
        PROFILE_LOCAL_06,
        PROFILE_TEST_06,
        PROFILE_STAGING_06,
        PROFILE_CANARY_06,
        PROFILE_PRODUCTION_06,
        PROFILE_RECOVERY_06,
        PROFILE_LOCAL_07,
        PROFILE_TEST_07,
        PROFILE_STAGING_07,
        PROFILE_CANARY_07,
        PROFILE_PRODUCTION_07,
        PROFILE_RECOVERY_07,
        PROFILE_LOCAL_08,
        PROFILE_TEST_08,
        PROFILE_STAGING_08,
        PROFILE_CANARY_08,
        PROFILE_PRODUCTION_08,
        PROFILE_RECOVERY_08,
        PROFILE_LOCAL_09,
        PROFILE_TEST_09,
        PROFILE_STAGING_09,
        PROFILE_CANARY_09,
        PROFILE_PRODUCTION_09,
        PROFILE_RECOVERY_09,
        PROFILE_LOCAL_10,
        PROFILE_TEST_10,
        PROFILE_STAGING_10,
        PROFILE_CANARY_10,
        PROFILE_PRODUCTION_10,
        PROFILE_RECOVERY_10,
    )


def by_scope(scope):
    return tuple(item for item in all_records() if item.scope == scope)


def select_entry(value, records=None):
    items = all_records() if records is None else tuple(records)
    return next((x for x in items if x.name == str(value)), None)


def value_for(value, records=None):
    item = select_entry(value, records)
    return None if item is None else item.value


def names_for_scope(value, records=None):
    return tuple(x.name for x in by_scope(str(value)))


def is_known(value, records=None):
    return select_entry(value, records) is not None

