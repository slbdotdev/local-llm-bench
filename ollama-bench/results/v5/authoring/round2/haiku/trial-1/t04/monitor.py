def report_cooldown(config, logger):
    logger.info("login cooldown configured: %s", config)


def reset_metrics(metrics):
    metrics.clear()
