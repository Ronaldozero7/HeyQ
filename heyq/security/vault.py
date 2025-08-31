"""
Legacy Vault client (removed).

This project now uses local YAML secrets in config/secrets.yaml.
Importing this module will raise to prevent accidental usage.
"""

raise RuntimeError(
    "Vault support has been removed. Use heyq.security.secrets.Secrets to load local secrets from config/secrets.yaml."
)
