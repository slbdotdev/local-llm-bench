from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    name: str
    value: str
    scope: str


    # tenant catalog
    TENANT_CREATED_01 = Record('tenant_created_01', 'tenant-created-01-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_01 = Record('tenant_suspended_01', 'tenant-suspended-01-rule', 'request')
    # tenant catalog
    TENANT_BILLING_01 = Record('tenant_billing_01', 'tenant-billing-01-rule', 'audit')
    # tenant catalog
    TENANT_REGION_01 = Record('tenant_region_01', 'tenant-region-01-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_01 = Record('tenant_owner_01', 'tenant-owner-01-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_01 = Record('tenant_quota_01', 'tenant-quota-01-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_02 = Record('tenant_created_02', 'tenant-created-02-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_02 = Record('tenant_suspended_02', 'tenant-suspended-02-rule', 'request')
    # tenant catalog
    TENANT_BILLING_02 = Record('tenant_billing_02', 'tenant-billing-02-rule', 'audit')
    # tenant catalog
    TENANT_REGION_02 = Record('tenant_region_02', 'tenant-region-02-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_02 = Record('tenant_owner_02', 'tenant-owner-02-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_02 = Record('tenant_quota_02', 'tenant-quota-02-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_03 = Record('tenant_created_03', 'tenant-created-03-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_03 = Record('tenant_suspended_03', 'tenant-suspended-03-rule', 'request')
    # tenant catalog
    TENANT_BILLING_03 = Record('tenant_billing_03', 'tenant-billing-03-rule', 'audit')
    # tenant catalog
    TENANT_REGION_03 = Record('tenant_region_03', 'tenant-region-03-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_03 = Record('tenant_owner_03', 'tenant-owner-03-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_03 = Record('tenant_quota_03', 'tenant-quota-03-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_04 = Record('tenant_created_04', 'tenant-created-04-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_04 = Record('tenant_suspended_04', 'tenant-suspended-04-rule', 'request')
    # tenant catalog
    TENANT_BILLING_04 = Record('tenant_billing_04', 'tenant-billing-04-rule', 'audit')
    # tenant catalog
    TENANT_REGION_04 = Record('tenant_region_04', 'tenant-region-04-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_04 = Record('tenant_owner_04', 'tenant-owner-04-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_04 = Record('tenant_quota_04', 'tenant-quota-04-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_05 = Record('tenant_created_05', 'tenant-created-05-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_05 = Record('tenant_suspended_05', 'tenant-suspended-05-rule', 'request')
    # tenant catalog
    TENANT_BILLING_05 = Record('tenant_billing_05', 'tenant-billing-05-rule', 'audit')
    # tenant catalog
    TENANT_REGION_05 = Record('tenant_region_05', 'tenant-region-05-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_05 = Record('tenant_owner_05', 'tenant-owner-05-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_05 = Record('tenant_quota_05', 'tenant-quota-05-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_06 = Record('tenant_created_06', 'tenant-created-06-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_06 = Record('tenant_suspended_06', 'tenant-suspended-06-rule', 'request')
    # tenant catalog
    TENANT_BILLING_06 = Record('tenant_billing_06', 'tenant-billing-06-rule', 'audit')
    # tenant catalog
    TENANT_REGION_06 = Record('tenant_region_06', 'tenant-region-06-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_06 = Record('tenant_owner_06', 'tenant-owner-06-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_06 = Record('tenant_quota_06', 'tenant-quota-06-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_07 = Record('tenant_created_07', 'tenant-created-07-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_07 = Record('tenant_suspended_07', 'tenant-suspended-07-rule', 'request')
    # tenant catalog
    TENANT_BILLING_07 = Record('tenant_billing_07', 'tenant-billing-07-rule', 'audit')
    # tenant catalog
    TENANT_REGION_07 = Record('tenant_region_07', 'tenant-region-07-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_07 = Record('tenant_owner_07', 'tenant-owner-07-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_07 = Record('tenant_quota_07', 'tenant-quota-07-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_08 = Record('tenant_created_08', 'tenant-created-08-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_08 = Record('tenant_suspended_08', 'tenant-suspended-08-rule', 'request')
    # tenant catalog
    TENANT_BILLING_08 = Record('tenant_billing_08', 'tenant-billing-08-rule', 'audit')
    # tenant catalog
    TENANT_REGION_08 = Record('tenant_region_08', 'tenant-region-08-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_08 = Record('tenant_owner_08', 'tenant-owner-08-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_08 = Record('tenant_quota_08', 'tenant-quota-08-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_09 = Record('tenant_created_09', 'tenant-created-09-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_09 = Record('tenant_suspended_09', 'tenant-suspended-09-rule', 'request')
    # tenant catalog
    TENANT_BILLING_09 = Record('tenant_billing_09', 'tenant-billing-09-rule', 'audit')
    # tenant catalog
    TENANT_REGION_09 = Record('tenant_region_09', 'tenant-region-09-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_09 = Record('tenant_owner_09', 'tenant-owner-09-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_09 = Record('tenant_quota_09', 'tenant-quota-09-rule', 'audit')
    # tenant catalog
    TENANT_CREATED_10 = Record('tenant_created_10', 'tenant-created-10-rule', 'tenant')
    # tenant catalog
    TENANT_SUSPENDED_10 = Record('tenant_suspended_10', 'tenant-suspended-10-rule', 'request')
    # tenant catalog
    TENANT_BILLING_10 = Record('tenant_billing_10', 'tenant-billing-10-rule', 'audit')
    # tenant catalog
    TENANT_REGION_10 = Record('tenant_region_10', 'tenant-region-10-rule', 'tenant')
    # tenant catalog
    TENANT_OWNER_10 = Record('tenant_owner_10', 'tenant-owner-10-rule', 'request')
    # tenant catalog
    TENANT_QUOTA_10 = Record('tenant_quota_10', 'tenant-quota-10-rule', 'audit')


def all_records():
    return (
        TENANT_CREATED_01,
        TENANT_SUSPENDED_01,
        TENANT_BILLING_01,
        TENANT_REGION_01,
        TENANT_OWNER_01,
        TENANT_QUOTA_01,
        TENANT_CREATED_02,
        TENANT_SUSPENDED_02,
        TENANT_BILLING_02,
        TENANT_REGION_02,
        TENANT_OWNER_02,
        TENANT_QUOTA_02,
        TENANT_CREATED_03,
        TENANT_SUSPENDED_03,
        TENANT_BILLING_03,
        TENANT_REGION_03,
        TENANT_OWNER_03,
        TENANT_QUOTA_03,
        TENANT_CREATED_04,
        TENANT_SUSPENDED_04,
        TENANT_BILLING_04,
        TENANT_REGION_04,
        TENANT_OWNER_04,
        TENANT_QUOTA_04,
        TENANT_CREATED_05,
        TENANT_SUSPENDED_05,
        TENANT_BILLING_05,
        TENANT_REGION_05,
        TENANT_OWNER_05,
        TENANT_QUOTA_05,
        TENANT_CREATED_06,
        TENANT_SUSPENDED_06,
        TENANT_BILLING_06,
        TENANT_REGION_06,
        TENANT_OWNER_06,
        TENANT_QUOTA_06,
        TENANT_CREATED_07,
        TENANT_SUSPENDED_07,
        TENANT_BILLING_07,
        TENANT_REGION_07,
        TENANT_OWNER_07,
        TENANT_QUOTA_07,
        TENANT_CREATED_08,
        TENANT_SUSPENDED_08,
        TENANT_BILLING_08,
        TENANT_REGION_08,
        TENANT_OWNER_08,
        TENANT_QUOTA_08,
        TENANT_CREATED_09,
        TENANT_SUSPENDED_09,
        TENANT_BILLING_09,
        TENANT_REGION_09,
        TENANT_OWNER_09,
        TENANT_QUOTA_09,
        TENANT_CREATED_10,
        TENANT_SUSPENDED_10,
        TENANT_BILLING_10,
        TENANT_REGION_10,
        TENANT_OWNER_10,
        TENANT_QUOTA_10,
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

