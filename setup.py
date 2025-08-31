from setuptools import setup, find_packages

setup(
    name="heyq",
    version="0.1.0",
    description="Voice-Controlled Enterprise Test Automation Framework",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Kept empty; use requirements.txt for pinned deps
    ],
    entry_points={
        "console_scripts": [
            "heyq=heyq.main:cli",
            "heyq-plan=heyq.run_plan:main",
            "heyq-web=heyq.webapp.app:run",
            "heyq-check-locators=heyq.tools.check_locators:run",
        ]
    },
)
