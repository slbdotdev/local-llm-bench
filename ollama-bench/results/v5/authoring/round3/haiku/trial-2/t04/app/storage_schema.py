from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # storage schema
    COLUMN_IDENTITY_01 = Record('column_identity_01', 'column-identity-01-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_01 = Record('column_until_01', 'column-until-01-rule', 'request')
    # storage schema
    COLUMN_REASON_01 = Record('column_reason_01', 'column-reason-01-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_01 = Record('column_created_at_01', 'column-created-at-01-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_01 = Record('column_updated_at_01', 'column-updated-at-01-rule', 'request')
    # storage schema
    COLUMN_VERSION_01 = Record('column_version_01', 'column-version-01-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_02 = Record('column_identity_02', 'column-identity-02-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_02 = Record('column_until_02', 'column-until-02-rule', 'request')
    # storage schema
    COLUMN_REASON_02 = Record('column_reason_02', 'column-reason-02-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_02 = Record('column_created_at_02', 'column-created-at-02-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_02 = Record('column_updated_at_02', 'column-updated-at-02-rule', 'request')
    # storage schema
    COLUMN_VERSION_02 = Record('column_version_02', 'column-version-02-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_03 = Record('column_identity_03', 'column-identity-03-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_03 = Record('column_until_03', 'column-until-03-rule', 'request')
    # storage schema
    COLUMN_REASON_03 = Record('column_reason_03', 'column-reason-03-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_03 = Record('column_created_at_03', 'column-created-at-03-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_03 = Record('column_updated_at_03', 'column-updated-at-03-rule', 'request')
    # storage schema
    COLUMN_VERSION_03 = Record('column_version_03', 'column-version-03-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_04 = Record('column_identity_04', 'column-identity-04-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_04 = Record('column_until_04', 'column-until-04-rule', 'request')
    # storage schema
    COLUMN_REASON_04 = Record('column_reason_04', 'column-reason-04-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_04 = Record('column_created_at_04', 'column-created-at-04-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_04 = Record('column_updated_at_04', 'column-updated-at-04-rule', 'request')
    # storage schema
    COLUMN_VERSION_04 = Record('column_version_04', 'column-version-04-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_05 = Record('column_identity_05', 'column-identity-05-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_05 = Record('column_until_05', 'column-until-05-rule', 'request')
    # storage schema
    COLUMN_REASON_05 = Record('column_reason_05', 'column-reason-05-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_05 = Record('column_created_at_05', 'column-created-at-05-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_05 = Record('column_updated_at_05', 'column-updated-at-05-rule', 'request')
    # storage schema
    COLUMN_VERSION_05 = Record('column_version_05', 'column-version-05-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_06 = Record('column_identity_06', 'column-identity-06-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_06 = Record('column_until_06', 'column-until-06-rule', 'request')
    # storage schema
    COLUMN_REASON_06 = Record('column_reason_06', 'column-reason-06-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_06 = Record('column_created_at_06', 'column-created-at-06-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_06 = Record('column_updated_at_06', 'column-updated-at-06-rule', 'request')
    # storage schema
    COLUMN_VERSION_06 = Record('column_version_06', 'column-version-06-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_07 = Record('column_identity_07', 'column-identity-07-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_07 = Record('column_until_07', 'column-until-07-rule', 'request')
    # storage schema
    COLUMN_REASON_07 = Record('column_reason_07', 'column-reason-07-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_07 = Record('column_created_at_07', 'column-created-at-07-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_07 = Record('column_updated_at_07', 'column-updated-at-07-rule', 'request')
    # storage schema
    COLUMN_VERSION_07 = Record('column_version_07', 'column-version-07-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_08 = Record('column_identity_08', 'column-identity-08-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_08 = Record('column_until_08', 'column-until-08-rule', 'request')
    # storage schema
    COLUMN_REASON_08 = Record('column_reason_08', 'column-reason-08-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_08 = Record('column_created_at_08', 'column-created-at-08-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_08 = Record('column_updated_at_08', 'column-updated-at-08-rule', 'request')
    # storage schema
    COLUMN_VERSION_08 = Record('column_version_08', 'column-version-08-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_09 = Record('column_identity_09', 'column-identity-09-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_09 = Record('column_until_09', 'column-until-09-rule', 'request')
    # storage schema
    COLUMN_REASON_09 = Record('column_reason_09', 'column-reason-09-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_09 = Record('column_created_at_09', 'column-created-at-09-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_09 = Record('column_updated_at_09', 'column-updated-at-09-rule', 'request')
    # storage schema
    COLUMN_VERSION_09 = Record('column_version_09', 'column-version-09-rule', 'audit')
    # storage schema
    COLUMN_IDENTITY_10 = Record('column_identity_10', 'column-identity-10-rule', 'tenant')
    # storage schema
    COLUMN_UNTIL_10 = Record('column_until_10', 'column-until-10-rule', 'request')
    # storage schema
    COLUMN_REASON_10 = Record('column_reason_10', 'column-reason-10-rule', 'audit')
    # storage schema
    COLUMN_CREATED_AT_10 = Record('column_created_at_10', 'column-created-at-10-rule', 'tenant')
    # storage schema
    COLUMN_UPDATED_AT_10 = Record('column_updated_at_10', 'column-updated-at-10-rule', 'request')
    # storage schema
    COLUMN_VERSION_10 = Record('column_version_10', 'column-version-10-rule', 'audit')


def all_records():
    return (
        COLUMN_IDENTITY_01,
        COLUMN_UNTIL_01,
        COLUMN_REASON_01,
        COLUMN_CREATED_AT_01,
        COLUMN_UPDATED_AT_01,
        COLUMN_VERSION_01,
        COLUMN_IDENTITY_02,
        COLUMN_UNTIL_02,
        COLUMN_REASON_02,
        COLUMN_CREATED_AT_02,
        COLUMN_UPDATED_AT_02,
        COLUMN_VERSION_02,
        COLUMN_IDENTITY_03,
        COLUMN_UNTIL_03,
        COLUMN_REASON_03,
        COLUMN_CREATED_AT_03,
        COLUMN_UPDATED_AT_03,
        COLUMN_VERSION_03,
        COLUMN_IDENTITY_04,
        COLUMN_UNTIL_04,
        COLUMN_REASON_04,
        COLUMN_CREATED_AT_04,
        COLUMN_UPDATED_AT_04,
        COLUMN_VERSION_04,
        COLUMN_IDENTITY_05,
        COLUMN_UNTIL_05,
        COLUMN_REASON_05,
        COLUMN_CREATED_AT_05,
        COLUMN_UPDATED_AT_05,
        COLUMN_VERSION_05,
        COLUMN_IDENTITY_06,
        COLUMN_UNTIL_06,
        COLUMN_REASON_06,
        COLUMN_CREATED_AT_06,
        COLUMN_UPDATED_AT_06,
        COLUMN_VERSION_06,
        COLUMN_IDENTITY_07,
        COLUMN_UNTIL_07,
        COLUMN_REASON_07,
        COLUMN_CREATED_AT_07,
        COLUMN_UPDATED_AT_07,
        COLUMN_VERSION_07,
        COLUMN_IDENTITY_08,
        COLUMN_UNTIL_08,
        COLUMN_REASON_08,
        COLUMN_CREATED_AT_08,
        COLUMN_UPDATED_AT_08,
        COLUMN_VERSION_08,
        COLUMN_IDENTITY_09,
        COLUMN_UNTIL_09,
        COLUMN_REASON_09,
        COLUMN_CREATED_AT_09,
        COLUMN_UPDATED_AT_09,
        COLUMN_VERSION_09,
        COLUMN_IDENTITY_10,
        COLUMN_UNTIL_10,
        COLUMN_REASON_10,
        COLUMN_CREATED_AT_10,
        COLUMN_UPDATED_AT_10,
        COLUMN_VERSION_10,
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

